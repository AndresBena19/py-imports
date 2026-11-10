"""Typed data model describing the imports found in a Python file.

Every import class is an immutable (frozen, slotted) dataclass with a
keyword-only constructor. ``to_dict()`` returns plain JSON-serializable data.
"""

import ast
from dataclasses import dataclass, field
from typing import Any, Literal


ImportKind = Literal["import", "absolute", "relative"]

GuardKind = Literal["if", "try", "with", "match", "for", "while"]
GuardBranch = Literal["body", "orelse", "handler", "finalbody", "case"]
GuardCategory = Literal[
    "type_checking",
    "not_type_checking",
    "import_attempt",
    "import_fallback",
    "version_check",
    "platform_check",
]


@dataclass(frozen=True, slots=True, kw_only=True)
class Guard:
    """A block that conditions whether an import runs.

    Attributes:
        kind: Statement that opens the block (``if``, ``try``, ``with``...).
        branch: Part of the statement holding the import: ``body``, ``orelse``
            (``else``/``elif``), ``handler`` (``except``), ``finalbody`` or ``case``.
        line: Line of the ``if``/``try``/... statement, or of the ``except``/``case``
            clause for ``handler``/``case`` branches.
        condition: Source of the condition: the ``if``/``while`` test, the handled
            exceptions of an ``except``, the ``with`` items, the ``for`` target and
            iterator, the ``match`` subject and ``case`` pattern. ``None`` when there
            is no condition (e.g. ``try`` body, bare ``except``).
        category: Well-known pattern the guard matches, if any:

            * ``type_checking``: body of ``if TYPE_CHECKING:``
            * ``not_type_checking``: its ``else``, or body of ``if not TYPE_CHECKING:``
            * ``import_attempt``: ``try`` body (or ``with suppress(...)``) whose
              handlers catch ``ImportError``
            * ``import_fallback``: ``except ImportError`` handler
            * ``version_check``: condition on ``sys.version_info`` / ``sys.hexversion``
            * ``platform_check``: condition on ``sys.platform``, ``os.name``,
              ``platform.*`` or ``sys.implementation``
    """

    kind: GuardKind
    branch: GuardBranch
    line: int
    condition: str | None = None
    category: GuardCategory | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return {
            "kind": self.kind,
            "branch": self.branch,
            "line": self.line,
            "condition": self.condition,
            "category": self.category,
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class ImportedName:
    """One name imported by an import statement.

    Examples:
        ``import numpy as np``      -> ImportedName(name="numpy", asname="np")
        ``from os import path``     -> ImportedName(name="path")
        ``from typing import *``    -> ImportedName(name="*")
    """

    name: str
    asname: str | None = None
    unused: bool = False

    @property
    def bound_name(self) -> str:
        """Name bound in the importing module (``import a.b`` binds ``a``)."""
        if self.asname:
            return self.asname
        return self.name.split(".", 1)[0]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return {"name": self.name, "asname": self.asname, "unused": self.unused}


@dataclass(frozen=True, slots=True, kw_only=True)
class ImportStatement:
    """An ``import x, y as z`` statement.

    Attributes:
        line: First line of the statement (1-based).
        statement: Exact source text of the statement.
        names: The names imported by the statement, in source order.
        end_line: Last line of the statement (differs for multi-line imports).
        column: 0-based column where the statement starts.
        scope: Dotted name of the enclosing functions/classes (e.g.
            ``"Service.run"``), ``None`` for module-level imports.
        guards: Enclosing ``if``/``try``/``with``/``match``/loop blocks, from the
            outermost to the innermost (including blocks outside the enclosing
            function or class). Empty for unconditional imports.
        outer_parent_node: Nearest enclosing ``FunctionDef``/``AsyncFunctionDef``/
            ``ClassDef`` node, ``None`` for module-level imports. Excluded from
            equality, ``repr`` and ``to_dict()``.
    """

    line: int
    statement: str
    names: tuple[ImportedName, ...] = ()
    end_line: int | None = None
    column: int = 0
    scope: str | None = None
    guards: tuple[Guard, ...] = ()
    outer_parent_node: ast.AST | None = field(default=None, repr=False, compare=False)

    @property
    def kind(self) -> ImportKind:
        """Kind of import statement."""
        return "import"

    @property
    def in_inner_scope(self) -> bool:
        """Whether the import is defined inside a function or a class."""
        return self.scope is not None or self.outer_parent_node is not None

    def _has_category(self, *categories: GuardCategory) -> bool:
        return any(guard.category in categories for guard in self.guards)

    @property
    def is_conditional(self) -> bool:
        """Whether the import is inside any ``if``/``try``/``with``/``match``/loop."""
        return bool(self.guards)

    @property
    def is_type_checking_only(self) -> bool:
        """Whether the import only runs for type checkers (``if TYPE_CHECKING:``)."""
        return self._has_category("type_checking")

    @property
    def is_optional(self) -> bool:
        """Whether the import is attempted in a ``try`` that handles ``ImportError``."""
        return self._has_category("import_attempt")

    @property
    def is_fallback(self) -> bool:
        """Whether the import is the fallback in an ``except ImportError`` handler."""
        return self._has_category("import_fallback")

    @property
    def is_version_dependent(self) -> bool:
        """Whether the import depends on a Python version check."""
        return self._has_category("version_check")

    @property
    def is_platform_dependent(self) -> bool:
        """Whether the import depends on a platform check."""
        return self._has_category("platform_check")

    @property
    def children(self) -> list[str]:
        """Imported names, as written in the statement."""
        return [item.name for item in self.names]

    @property
    def aliases(self) -> list[str | None]:
        """``as`` names, parallel to ``children`` (``None`` when not aliased)."""
        return [item.asname for item in self.names]

    @property
    def children_unused(self) -> list[str]:
        """Imported names that are never used in the file."""
        return [item.name for item in self.names if item.unused]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of the import."""
        return {
            "kind": self.kind,
            "line": self.line,
            "end_line": self.end_line,
            "column": self.column,
            "statement": self.statement,
            "names": [item.to_dict() for item in self.names],
            "in_inner_scope": self.in_inner_scope,
            "scope": self.scope,
            "guards": [guard.to_dict() for guard in self.guards],
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class ImportFromStatement(ImportStatement):
    """A ``from module import x`` statement.

    Attributes:
        module: Module after ``from`` without the leading dots (``""`` for
            ``from . import x``).
        level: Number of leading dots; ``0`` for absolute imports.
    """

    module: str = ""
    level: int = 0

    @property
    def kind(self) -> ImportKind:
        """Kind of import statement: ``absolute`` or ``relative``."""
        return "relative" if self.level > 0 else "absolute"

    @property
    def parent(self) -> str:
        """Alias of ``module`` kept for backwards compatibility."""
        return self.module

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of the import."""
        return {
            **ImportStatement.to_dict(self),
            "module": self.module,
            "level": self.level,
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class RelativeImportStatement(ImportFromStatement):
    """A relative import, e.g. ``from .models import User`` (``level > 0``)."""


@dataclass(frozen=True, slots=True, kw_only=True)
class AbsoluteImportStatement(ImportFromStatement):
    """An absolute from-import, e.g. ``from os import path`` (``level == 0``)."""


AnyImport = ImportStatement | AbsoluteImportStatement | RelativeImportStatement


@dataclass(slots=True)
class ImportsCollectionFile:
    """The imports found in a file, grouped by kind."""

    imports: list[ImportStatement] = field(default_factory=list)
    absolute_imports: list[AbsoluteImportStatement] = field(default_factory=list)
    relative_imports: list[RelativeImportStatement] = field(default_factory=list)

    def add(self, statement: AnyImport) -> None:
        """Add an import statement to the matching group."""
        if isinstance(statement, RelativeImportStatement):
            self.relative_imports.append(statement)
        elif isinstance(statement, AbsoluteImportStatement):
            self.absolute_imports.append(statement)
        else:
            self.imports.append(statement)

    @property
    def all_imports(self) -> list[AnyImport]:
        """Every import statement in the file, in source order."""
        statements: list[AnyImport] = [
            *self.imports,
            *self.absolute_imports,
            *self.relative_imports,
        ]
        return sorted(statements, key=lambda item: (item.line, item.column))

    def to_dict(self) -> dict[str, list[dict[str, Any]]]:
        """Return a JSON-serializable representation of the imports in the file."""
        return {
            "imports": [item.to_dict() for item in self.imports],
            "absolute_imports": [item.to_dict() for item in self.absolute_imports],
            "relative_imports": [item.to_dict() for item in self.relative_imports],
        }
