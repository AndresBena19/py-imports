"""Classify the blocks (guards) that condition whether an import runs."""

import ast

from py_imports.base.models import GuardCategory


#: Exceptions whose handlers are considered to catch a failed import.
IMPORT_ERRORS = frozenset(
    {"ImportError", "ModuleNotFoundError", "Exception", "BaseException"}
)

_VERSION_NAMES = frozenset(
    {"sys.version_info", "sys.hexversion", "version_info", "hexversion"}
)
_PLATFORM_NAMES = frozenset({"sys.platform", "os.name", "sys.implementation", "platform"})


def dotted_name(node: ast.expr) -> str | None:
    """Return ``a.b.c`` for ``Name``/``Attribute`` chains, ``None`` otherwise."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = dotted_name(node.value)
        return f"{base}.{node.attr}" if base else None
    return None


def _is_type_checking_flag(node: ast.expr) -> bool:
    return (isinstance(node, ast.Name) and node.id == "TYPE_CHECKING") or (
        isinstance(node, ast.Attribute) and node.attr == "TYPE_CHECKING"
    )


def type_checking_test(test: ast.expr) -> bool | None:
    """Detect ``if TYPE_CHECKING:`` (True) and ``if not TYPE_CHECKING:`` (False).

    Returns ``None`` for any other condition.
    """
    if _is_type_checking_flag(test):
        return True
    if (
        isinstance(test, ast.UnaryOp)
        and isinstance(test.op, ast.Not)
        and _is_type_checking_flag(test.operand)
    ):
        return False
    return None


def condition_category(test: ast.expr) -> GuardCategory | None:
    """Classify a condition as a Python version or platform check."""
    names = {
        name
        for node in ast.walk(test)
        if isinstance(node, ast.Name | ast.Attribute)
        and (name := dotted_name(node)) is not None
    }
    if names & _VERSION_NAMES:
        return "version_check"
    if names & _PLATFORM_NAMES or any(name.startswith("platform.") for name in names):
        return "platform_check"
    return None


def _catches_import_error(node: ast.expr) -> bool:
    types = node.elts if isinstance(node, ast.Tuple) else [node]
    return any(
        (name := dotted_name(item)) is not None
        and name.rsplit(".", 1)[-1] in IMPORT_ERRORS
        for item in types
    )


def handler_catches_import_error(handler: ast.ExceptHandler) -> bool:
    """Whether an ``except`` clause catches a failed import (bare ``except`` too)."""
    return handler.type is None or _catches_import_error(handler.type)


def suppresses_import_error(item: ast.withitem) -> bool:
    """Whether a ``with`` item is ``suppress(ImportError, ...)``."""
    call = item.context_expr
    if not isinstance(call, ast.Call):
        return False
    func = dotted_name(call.func)
    return (
        func is not None
        and func.rsplit(".", 1)[-1] == "suppress"
        and any(_catches_import_error(arg) for arg in call.args)
    )
