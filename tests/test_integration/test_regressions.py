"""Regression tests for bugs fixed while modernizing the project."""

import ast
from pathlib import Path

import pytest

from py_imports.manager import PyImports
from tests.conftest import FileFactory


def test_unused_dotted_import_keeps_full_name(set_up_file: FileFactory) -> None:
    """`import os.path` unused must be reported as `os.path`, matching `children`."""
    file_path = set_up_file("import os.path\n")

    with PyImports() as handler:
        imports = handler.get_file_imports(file_path)

    assert imports.imports[0].children == ["os.path"]
    assert imports.imports[0].children_unused == ["os.path"]


def test_unused_aliased_imports(set_up_file: FileFactory) -> None:
    """Aliased imports must be reported by their imported name, not `x as y`."""
    file_path = set_up_file("import a.b as c\nfrom x import y as z, w\nw()\n")

    with PyImports() as handler:
        imports = handler.get_file_imports(file_path)

    assert imports.imports[0].children_unused == ["a.b"]
    assert imports.absolute_imports[0].children_unused == ["y"]


def test_unused_relative_and_multiline_imports(set_up_file: FileFactory) -> None:
    """Relative and multi-line imports are detected as unused at the statement line."""
    content = "from . import a\nfrom ..pkg import (\n    b,\n    c,\n)\nc()\n"
    file_path = set_up_file(content)

    with PyImports() as handler:
        imports = handler.get_file_imports(file_path)

    first, second = imports.relative_imports
    assert first.children_unused == ["a"]
    assert second.children_unused == ["b"]
    assert second.statement == "from ..pkg import (\n    b,\n    c,\n)"


def test_import_in_inner_scope(set_up_file: FileFactory) -> None:
    """Imports inside functions expose the enclosing node."""
    file_path = set_up_file("import os\n\ndef foo():\n    from typing import Any\n")

    with PyImports() as handler:
        imports = handler.get_file_imports(file_path)

    assert imports.imports[0].in_inner_scope is False
    assert imports.imports[0].outer_parent_node is None

    inner = imports.absolute_imports[0]
    assert inner.in_inner_scope is True
    assert isinstance(inner.outer_parent_node, ast.FunctionDef)
    assert inner.outer_parent_node.name == "foo"
    assert inner.statement == "from typing import Any"


def test_accepts_pathlike_and_detects_encoding(tmp_path: Path) -> None:
    """`pathlib.Path` inputs and PEP 263 encodings / BOM are supported."""
    latin = tmp_path / "latin.py"
    latin.write_bytes("# -*- coding: latin-1 -*-\nimport os  # ñ\n".encode("latin-1"))
    bom = tmp_path / "bom.py"
    bom.write_bytes(b"\xef\xbb\xbfimport sys\n")

    with PyImports() as handler:
        assert handler.get_file_imports(latin).imports[0].children == ["os"]
        assert handler.get_imports(bom).imports[0].children == ["sys"]  # type: ignore[union-attr]
        assert set(handler.get_dir_imports(tmp_path)) == {str(latin), str(bom)}


def test_typed_helpers_reject_wrong_kind(
    tmp_path: Path, set_up_file: FileFactory
) -> None:
    """The typed helpers raise when given the wrong kind of path."""
    file_path = set_up_file("import os\n")

    with PyImports() as handler:
        with pytest.raises(IsADirectoryError):
            handler.get_file_imports(tmp_path)
        with pytest.raises(NotADirectoryError):
            handler.get_dir_imports(file_path)
