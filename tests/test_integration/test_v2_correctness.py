"""Regression tests for the correctness fixes released in 2.1.0."""

import ast
import json
import logging
from pathlib import Path

import pytest

from py_imports.ast_analyzers import AstImportAnalyzer
from py_imports.manager import PyImports
from tests.conftest import FileFactory


GUARDED_MODULE = """\
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

try:
    import tomllib
except ImportError:
    import tomli as tomllib

if sys.version_info >= (3, 12):
    from itertools import batched
"""


def test_module_level_guards_are_not_inner_scope(set_up_file: FileFactory) -> None:
    """Imports under if/try at module level stay in the module scope."""
    with PyImports() as handler:
        imports = handler.get_file_imports(set_up_file(GUARDED_MODULE))

    every_import = [*imports.imports, *imports.absolute_imports]
    assert len(every_import) == 6
    for item in every_import:
        assert item.in_inner_scope is False, item.statement
        assert item.outer_parent_node is None
        assert item.scope is None


def test_inner_scope_is_the_enclosing_function_or_class(
    set_up_file: FileFactory,
) -> None:
    """The enclosing def/class is reported even when the import is nested in an if."""
    content = """\
class Service:
    def run(self):
        if True:
            import json

async def main():
    import asyncio
"""
    with PyImports() as handler:
        imports = handler.get_file_imports(set_up_file(content))

    in_method, in_coroutine = imports.imports
    assert in_method.in_inner_scope is True
    assert isinstance(in_method.outer_parent_node, ast.FunctionDef)
    assert in_method.outer_parent_node.name == "run"
    assert in_method.scope == "Service.run"

    assert isinstance(in_coroutine.outer_parent_node, ast.AsyncFunctionDef)
    assert in_coroutine.scope == "main"


def test_analyzer_does_not_mutate_the_ast() -> None:
    """The caller's tree is left untouched (no ``parent`` attributes added)."""
    source = "import os\ndef f():\n    import sys\n"
    tree = ast.parse(source)

    analyzer = AstImportAnalyzer(source.splitlines(keepends=True), source, tree)
    analyzer.visit(tree)

    assert len(analyzer.imports_metadata.imports) == 2
    assert not any(hasattr(node, "parent") for node in ast.walk(tree))


def test_directory_scan_skips_unparseable_files(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """A broken file is reported in ``parse_errors`` instead of aborting the scan."""
    (tmp_path / "good.py").write_text("import os\n", encoding="utf-8")
    (tmp_path / "broken.py").write_text("def broken(:\n", encoding="utf-8")
    (tmp_path / "binary.py").write_bytes(b"\xff\xfe\x00import os\n")

    with PyImports() as handler, caplog.at_level(logging.WARNING):
        imports = handler.get_dir_imports(tmp_path)

    assert list(imports) == [str(tmp_path / "good.py")]
    assert set(handler.parse_errors) == {
        str(tmp_path / "broken.py"),
        str(tmp_path / "binary.py"),
    }
    assert isinstance(handler.parse_errors[str(tmp_path / "broken.py")], SyntaxError)
    assert "broken.py" in caplog.text


def test_single_file_still_raises_on_syntax_error(set_up_file: FileFactory) -> None:
    """Asking for one specific file keeps raising, so the caller sees the error."""
    with PyImports() as handler, pytest.raises(SyntaxError):
        handler.get_file_imports(set_up_file("def broken(:\n"))


def test_directory_scan_skips_vendored_dirs_and_is_sorted(tmp_path: Path) -> None:
    """Hidden dirs, virtualenvs and caches are skipped; results are sorted."""
    for relative in [
        "b.py",
        "a.py",
        "pkg/z.py",
        "pkg/c.py",
        ".venv/lib/x.py",
        ".git/hooks/y.py",
        "__pycache__/w.py",
        "node_modules/n.py",
        "env/lib/site-packages/dep.py",
    ]:
        file = tmp_path / relative
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text("import os\n", encoding="utf-8")
    (tmp_path / "env" / "pyvenv.cfg").write_text("home = /usr\n", encoding="utf-8")

    with PyImports() as handler:
        imports = handler.get_dir_imports(tmp_path)

    assert [Path(path).relative_to(tmp_path).as_posix() for path in imports] == [
        "a.py",
        "b.py",
        "pkg/c.py",
        "pkg/z.py",
    ]


def test_results_are_json_serializable_and_keep_aliases(
    set_up_file: FileFactory,
) -> None:
    """``to_dict`` returns plain data, including ``as`` aliases and scope names."""
    content = """\
import numpy as np, os
from .models import User as U
def f():
    from typing import Any
np.array
"""
    with PyImports() as handler:
        imports = handler.get_file_imports(set_up_file(content))

    data = json.loads(json.dumps(imports.to_dict()))

    assert data["imports"] == [
        {
            "kind": "import",
            "line": 1,
            "end_line": 1,
            "column": 0,
            "statement": "import numpy as np, os",
            "names": [
                {"name": "numpy", "asname": "np", "unused": False},
                {"name": "os", "asname": None, "unused": True},
            ],
            "in_inner_scope": False,
            "scope": None,
        }
    ]
    assert data["relative_imports"][0] == {
        "kind": "relative",
        "line": 2,
        "end_line": 2,
        "column": 0,
        "statement": "from .models import User as U",
        "names": [{"name": "User", "asname": "U", "unused": True}],
        "in_inner_scope": False,
        "scope": None,
        "module": "models",
        "level": 1,
    }
    assert data["absolute_imports"][0]["kind"] == "absolute"
    assert data["absolute_imports"][0]["scope"] == "f"
    assert data["absolute_imports"][0]["in_inner_scope"] is True
