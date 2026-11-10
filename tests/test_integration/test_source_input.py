"""Tests for parsing source code that is not read from a file."""

import pytest

from py_imports import PyImports
from tests.conftest import FileFactory


SOURCE = """\
import os
from typing import TYPE_CHECKING
from . import models

if TYPE_CHECKING:
    from collections.abc import Iterator

def run():
    import json
"""


def test_source_gives_the_same_result_as_the_file(set_up_file: FileFactory) -> None:
    with PyImports() as handler:
        from_file = handler.get_file_imports(set_up_file(SOURCE))

    from_source = PyImports.get_source_imports(SOURCE)

    assert from_source == from_file
    assert from_source.to_dict() == from_file.to_dict()
    assert [item.statement for item in from_source.all_imports] == [
        "import os",
        "from typing import TYPE_CHECKING",
        "from . import models",
        "from collections.abc import Iterator",
        "import json",
    ]


def test_source_is_not_recorded_in_the_resume() -> None:
    with PyImports() as handler:
        handler.get_source_imports("import os\n")

        assert handler.imports_resume() == {}


@pytest.mark.parametrize(
    "source",
    [
        b"\xef\xbb\xbfimport sys\n",
        "# -*- coding: latin-1 -*-\nimport sys  # \xf1\n".encode("latin-1"),
        b"import sys\n",
    ],
    ids=["utf8-bom", "latin1-cookie", "plain-bytes"],
)
def test_bytes_are_decoded_like_files(source: bytes) -> None:
    imports = PyImports.get_source_imports(source)

    assert imports.imports[0].children == ["sys"]


@pytest.mark.parametrize("newline", ["\r\n", "\r"])
def test_newlines_are_normalized(newline: str) -> None:
    source = "from x import (\n    a,\n)\n".replace("\n", newline)

    for value in (source, source.encode()):
        statement = PyImports.get_source_imports(value).absolute_imports[0]
        assert statement.statement == "from x import (\n    a,\n)"
        assert (statement.line, statement.end_line) == (1, 3)


def test_syntax_error_uses_the_given_filename() -> None:
    with pytest.raises(SyntaxError) as error:
        PyImports.get_source_imports("def broken(:\n", filename="buffer.py")

    assert error.value.filename == "buffer.py"


def test_undecodable_bytes_raise_syntax_error_like_files() -> None:
    with pytest.raises(SyntaxError, match="encoding"):
        PyImports.get_source_imports(b"import os  # \xff\n")


def test_empty_source() -> None:
    assert PyImports.get_source_imports("").all_imports == []
