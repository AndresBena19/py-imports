"""Tests for the guard context (if/try/with/match/loops) of each import."""

import json
import textwrap

import pytest

from py_imports import Guard, ImportStatement, PyImports
from tests.conftest import FileFactory


def scan(set_up_file: FileFactory, source: str) -> dict[str, ImportStatement]:
    """Scan ``source`` and index its import statements by their source text."""
    with PyImports() as handler:
        imports = handler.get_file_imports(set_up_file(textwrap.dedent(source)))
    return {statement.statement: statement for statement in imports.all_imports}


def summary(statement: ImportStatement) -> list[tuple[str, str, str | None]]:
    return [(guard.kind, guard.branch, guard.category) for guard in statement.guards]


def test_unconditional_imports_have_no_guards(set_up_file: FileFactory) -> None:
    found = scan(
        set_up_file,
        "import os\nwith open('f'):\n    import sys\nwith lock:\n    import json\n",
    )

    for statement in found.values():
        assert statement.guards == ()
        assert statement.is_conditional is False


@pytest.mark.parametrize(
    ("condition", "body", "orelse"),
    [
        ("TYPE_CHECKING", "type_checking", "not_type_checking"),
        ("typing.TYPE_CHECKING", "type_checking", "not_type_checking"),
        ("not TYPE_CHECKING", "not_type_checking", "type_checking"),
    ],
)
def test_type_checking_blocks(
    set_up_file: FileFactory, condition: str, body: str, orelse: str
) -> None:
    found = scan(
        set_up_file,
        f"""
        if {condition}:
            import a
        else:
            import b
        """,
    )

    assert summary(found["import a"]) == [("if", "body", body)]
    assert summary(found["import b"]) == [("if", "orelse", orelse)]
    assert found["import a"].is_type_checking_only is (body == "type_checking")
    assert found["import b"].is_type_checking_only is (orelse == "type_checking")
    assert found["import a"].guards[0].condition == condition


def test_optional_imports_and_fallbacks(set_up_file: FileFactory) -> None:
    found = scan(
        set_up_file,
        """
        from contextlib import suppress
        try:
            import ujson as json
        except (ImportError, OSError):
            import json
        else:
            import orjson
        finally:
            import atexit
        with suppress(ModuleNotFoundError):
            import rich
        try:
            import settings
        except ValueError:
            import defaults
        """,
    )

    attempt = found["import ujson as json"]
    assert summary(attempt) == [("try", "body", "import_attempt")]
    assert attempt.is_optional is True
    assert attempt.guards[0].condition is None

    fallback = found["import json"]
    assert summary(fallback) == [("try", "handler", "import_fallback")]
    assert fallback.is_fallback is True
    assert fallback.guards[0].condition == "(ImportError, OSError)"
    assert fallback.guards[0].line == 5

    assert summary(found["import orjson"]) == [("try", "orelse", None)]
    assert summary(found["import atexit"]) == [("try", "finalbody", None)]

    suppressed = found["import rich"]
    assert summary(suppressed) == [("with", "body", "import_attempt")]
    assert suppressed.guards[0].condition == "suppress(ModuleNotFoundError)"

    # a try that does not handle ImportError is conditional, not optional
    assert summary(found["import settings"]) == [("try", "body", None)]
    assert found["import settings"].is_optional is False
    assert found["import defaults"].is_fallback is False


def test_bare_except_counts_as_fallback(set_up_file: FileFactory) -> None:
    found = scan(set_up_file, "try:\n    import a\nexcept:\n    import b\n")

    assert found["import a"].is_optional is True
    assert found["import b"].is_fallback is True
    assert found["import b"].guards[0].condition is None


def test_version_and_platform_checks(set_up_file: FileFactory) -> None:
    found = scan(
        set_up_file,
        """
        if sys.version_info >= (3, 11):
            import tomllib
        elif sys.platform == "win32":
            import winreg
        if os.name == "nt" and platform.system() == "Windows":
            import msvcrt
        """,
    )

    assert summary(found["import tomllib"]) == [("if", "body", "version_check")]
    assert found["import tomllib"].is_version_dependent is True

    # elif = else branch of the version check + body of the platform check
    winreg = found["import winreg"]
    assert summary(winreg) == [
        ("if", "orelse", "version_check"),
        ("if", "body", "platform_check"),
    ]
    assert winreg.is_version_dependent is True
    assert winreg.is_platform_dependent is True

    assert found["import msvcrt"].is_platform_dependent is True


def test_loops_and_match(set_up_file: FileFactory) -> None:
    found = scan(
        set_up_file,
        """
        for name in plugins:
            import a
        while sys.version_info < (4,):
            import b
            break
        match command:
            case "run" if enabled:
                import c
        match sys.platform:
            case "linux":
                import d
        if get_settings().debug:
            import e
        """,
    )

    assert summary(found["import a"]) == [("for", "body", None)]
    assert found["import a"].guards[0].condition == "name in plugins"
    assert summary(found["import b"]) == [("while", "body", "version_check")]
    assert summary(found["import c"]) == [("match", "case", None)]
    assert found["import c"].guards[0].condition == "command: 'run' if enabled"
    assert summary(found["import d"]) == [("match", "case", "platform_check")]
    assert found["import d"].guards[0].condition == "sys.platform: 'linux'"
    assert summary(found["import e"]) == [("if", "body", None)]


def test_guards_outside_the_function_still_apply(set_up_file: FileFactory) -> None:
    found = scan(
        set_up_file,
        """
        if TYPE_CHECKING:
            def helper():
                try:
                    import a
                except ImportError:
                    pass
        """,
    )

    statement = found["import a"]
    assert statement.scope == "helper"
    assert summary(statement) == [
        ("if", "body", "type_checking"),
        ("try", "body", "import_attempt"),
    ]
    assert statement.is_type_checking_only
    assert statement.is_optional


def test_guards_are_serialized(set_up_file: FileFactory) -> None:
    found = scan(set_up_file, "if TYPE_CHECKING:\n    import a\n")

    data = json.loads(json.dumps(found["import a"].to_dict()))

    assert data["guards"] == [
        {
            "kind": "if",
            "branch": "body",
            "line": 1,
            "condition": "TYPE_CHECKING",
            "category": "type_checking",
        }
    ]
    assert Guard(kind="if", branch="body", line=1).to_dict()["category"] is None
