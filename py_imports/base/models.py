"""Base classes to define Imports behaviors."""

import ast
from typing import Any


class ImportStatement:
    """Class that represent the most simple import statement in python."""

    def __init__(
        self, line: int, children: list[str], statement: str, **kwargs: Any
    ) -> None:
        """Initialize basic python import.

        Args:
            line: Line where the import was found in the file
            children: Packages or modules imports after the import statement
            statement: Plane text representation of the import found
            **kwargs: Extra data passed.

        Examples:
            import flask, dataclass, ...
        """
        self.line = line
        self.children = children
        self.statement = statement.strip()

        self.from_internal: bool = False
        self.children_unused: list[str] = kwargs.pop("children_unused", [])
        # ``as`` names, parallel to ``children`` (None when the child is not aliased)
        self.aliases: list[str | None] = kwargs.pop("aliases", [None] * len(children))
        # Nearest enclosing function/class node, None for module-level imports
        self.outer_parent_node: ast.AST | None = kwargs.pop("outer_parent_node", None)
        # Dotted name of the enclosing functions/classes, e.g. "MyClass.method"
        self.scope: str | None = kwargs.pop("scope", None)
        self.in_inner_scope: bool = self.outer_parent_node is not None

        self.kwargs = kwargs

    @property
    def kind(self) -> str:
        """Kind of import statement: ``import``, ``absolute`` or ``relative``."""
        return "import"

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of the import.

        The ``outer_parent_node`` AST node is not included; ``scope`` carries its
        dotted name instead.
        """
        return {
            "kind": self.kind,
            "line": self.line,
            "statement": self.statement,
            "children": list(self.children),
            "aliases": list(self.aliases),
            "children_unused": list(self.children_unused),
            "in_inner_scope": self.in_inner_scope,
            "scope": self.scope,
        }


class ImportFromStatement(ImportStatement):
    """Class that represent a import statement that use FROM in python."""

    def __init__(
        self,
        line: int,
        children: list[str],
        parent: str,
        statement: str,
        level: int = 0,
        **kwargs: Any,
    ) -> None:
        """Initialize from statement python import.

        Args:
            line:  Line where the import was found in the file
            children: Packages or modules imports after the import statement
            parent: Package or module  where the children was imported
            statement: Plane text representation of the import found
            level: Integer holding the level of the relative import.
            **kwargs: Extra data passed.

        Examples:
            from <parents> imports <children>
        """
        self.parent = parent
        self.level = level
        super().__init__(line, children, statement, **kwargs)

    @property
    def kind(self) -> str:
        """Kind of import statement: ``absolute`` or ``relative``."""
        return "relative" if self.level > 0 else "absolute"

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of the import."""
        return {**super().to_dict(), "parent": self.parent, "level": self.level}


class RelativeImportStatement(ImportFromStatement):
    """Class that represent a relative import statement in python."""

    def __init__(
        self,
        line: int,
        parent: str,
        children: list[str],
        statement: str,
        level: int,
        **kwargs: Any,
    ) -> None:
        """Initialize relative statement python import.

        Args:
            line:  Line where the import was found in the file
            children: Packages or modules imports after the import statement
            parent: Package or module  where the children was imported
            statement: Plane text representation of the import found
            level: Integer holding the level of the relative import.
            **kwargs: Extra data passed.

        Examples:
            from . import mixins
            from .mixins import UnUsedImportMixin
        """
        super().__init__(line, children, parent, statement, level, **kwargs)


class AbsoluteImportStatement(ImportFromStatement):
    """Class that represent an absolute import statement in python."""

    def __init__(
        self, line: int, parent: str, children: list[str], statement: str, **kwargs: Any
    ):
        """Initialize relative statement python import.

        Args:
            line:  Line where the import was found in the file
            children: Packages or modules imports after the import statement
            parent: Package or module  where the children was imported
            statement: Plane text representation of the import found
            **kwargs: Extra data passed.

        Examples:
            from py_dep import mixins
            from mixins import UnUsedImportMixin

        Notes:
            An absolute import by default has a level equals to 0
        """
        super().__init__(line, children, parent, statement, **kwargs)


class ImportsCollectionFile:
    """Class to collect the meta information about the imports in a file."""

    def __init__(self) -> None:
        self.imports: list[ImportStatement] = []
        self.relative_imports: list[RelativeImportStatement] = []
        self.absolute_imports: list[AbsoluteImportStatement] = []

    def to_dict(self) -> dict[str, list[dict[str, Any]]]:
        """Return a JSON-serializable representation of the imports in the file."""
        return {
            "imports": [item.to_dict() for item in self.imports],
            "absolute_imports": [item.to_dict() for item in self.absolute_imports],
            "relative_imports": [item.to_dict() for item in self.relative_imports],
        }

    def register_import_from(
        self,
        line: int,
        children: list[str],
        statement: str,
        level: int,
        parent: str,
        **kwargs: Any,
    ) -> AbsoluteImportStatement | RelativeImportStatement:
        """Register absolute or relative import.

        Notes:
            If the level of the current imports is equals to 0, that's mean that is a
            absolute import otherwise is a relative import

        Returns:
            The object that represent the relative or absolute import
        """
        import_from: AbsoluteImportStatement | RelativeImportStatement

        if level > 0:
            import_from = RelativeImportStatement(
                line, parent, children, statement, level, **kwargs
            )
            self.relative_imports.append(import_from)
        else:
            import_from = AbsoluteImportStatement(
                line, parent, children, statement, **kwargs
            )
            self.absolute_imports.append(import_from)

        return import_from

    def register_import(
        self, line: int, children: list[str], statement: str, **kwargs: Any
    ) -> ImportStatement:
        """Register simple import."""
        simple_import = ImportStatement(line, children, statement, **kwargs)
        self.imports.append(simple_import)
        return simple_import
