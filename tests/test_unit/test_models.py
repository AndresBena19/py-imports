"""Unit tests for the typed data model."""

import ast
import dataclasses
import pickle

import pytest

import py_imports
from py_imports import (
    AbsoluteImportStatement,
    ImportedName,
    ImportsCollectionFile,
    ImportStatement,
    PyImports,
    RelativeImportStatement,
)
from tests.conftest import FileFactory


def test_statements_are_frozen_and_keyword_only() -> None:
    statement = ImportStatement(line=1, statement="import os")

    with pytest.raises(dataclasses.FrozenInstanceError):
        statement.line = 2  # type: ignore[misc]
    with pytest.raises(TypeError):
        ImportStatement(1, "import os")  # type: ignore[call-arg]


def test_backwards_compatible_properties() -> None:
    statement = RelativeImportStatement(
        line=3,
        statement="from ..pkg import a as b, c",
        names=(ImportedName(name="a", asname="b"), ImportedName(name="c", unused=True)),
        module="pkg",
        level=2,
    )

    assert statement.kind == "relative"
    assert statement.children == ["a", "c"]
    assert statement.aliases == ["b", None]
    assert statement.children_unused == ["c"]
    assert statement.parent == "pkg"
    assert statement.in_inner_scope is False
    assert AbsoluteImportStatement(line=1, statement="from os import path").kind == (
        "absolute"
    )


def test_bound_name() -> None:
    assert ImportedName(name="os.path").bound_name == "os"
    assert ImportedName(name="numpy", asname="np").bound_name == "np"


def test_equality_ignores_ast_node_and_results_pickle(set_up_file: FileFactory) -> None:
    with PyImports() as handler:
        imports = handler.get_file_imports(set_up_file("def f():\n    import os\n"))

    statement = imports.imports[0]
    assert isinstance(statement.outer_parent_node, ast.FunctionDef)
    assert statement == dataclasses.replace(statement, outer_parent_node=None)
    assert hash(statement) == hash(dataclasses.replace(statement, outer_parent_node=None))
    assert pickle.loads(pickle.dumps(imports)) == imports  # noqa: S301 (trusted data)


def test_all_imports_is_in_source_order(set_up_file: FileFactory) -> None:
    content = "from . import a; import b\nfrom c import d\nimport e\n"
    with PyImports() as handler:
        imports = handler.get_file_imports(set_up_file(content))

    assert [item.statement for item in imports.all_imports] == [
        "from . import a",
        "import b",
        "from c import d",
        "import e",
    ]
    assert imports.all_imports[1].column == 17


def test_multiline_statement_end_line(set_up_file: FileFactory) -> None:
    with PyImports() as handler:
        imports = handler.get_file_imports(
            set_up_file("from x import (\n    a,\n    b,\n)\n")
        )

    statement = imports.absolute_imports[0]
    assert (statement.line, statement.end_line) == (1, 4)


def test_collection_add_routes_by_type() -> None:
    collection = ImportsCollectionFile()
    collection.add(ImportStatement(line=1, statement="import a"))
    collection.add(AbsoluteImportStatement(line=2, statement="from b import c"))
    collection.add(RelativeImportStatement(line=3, statement="from . import d", level=1))

    assert [len(collection.imports), len(collection.absolute_imports)] == [1, 1]
    assert len(collection.relative_imports) == 1


def test_public_api_is_exported_from_the_package() -> None:
    assert set(py_imports.__all__) >= {"PyImports", "ImportStatement", "ImportedName"}
