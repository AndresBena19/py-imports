"""Base classes to define Imports behaviors"""
from typing import Any, List, Union


class ImportStatement:
    """
    Class that represent the most simple import statement in python
    """

    def __init__(
        self, line: int, children: List[str], statement: str, **kwargs: Any
    ) -> None:
        """Initialize basic python import
        Args:
            line: Line where the import was found in the file
            children: Packages or modules imports after the import statement
            statement: Plane text representation of the import found
            **kwargs: Extra data passed

        Examples:
            import flask, dataclass, ...
        """
        self.line = line
        self.children = children
        self.statement = statement

        self.from_internal: bool = False
        self.children_unused: List = kwargs.get("children_unused", [])
        self.kwargs = kwargs


class ImportFromStatement(ImportStatement):
    """
    Class that represent a import statement that use FROM in python
    """

    def __init__(
        self,
        line: int,
        children: List[str],
        parent: str,
        statement: str,
        level: int = 0,
        **kwargs: Any,
    ) -> None:
        """Initialize from statement python import
        Args:
            line:  Line where the import was found in the file
            children: Packages or modules imports after the import statement
            parent: Package or module  where the children was imported
            statement: Plane text representation of the import found
            level: Integer holding the level of the relative import.
            **kwargs: Extra data passed

        Examples:
            from <parents> imports <children>
        """
        self.parent = parent
        self.level = level
        super().__init__(line, children, statement, **kwargs)


class RelativeImportStatement(ImportFromStatement):
    """
    Class that represent a relative import statement in python
    """

    def __init__(
        self,
        line: int,
        parent: str,
        children: List[str],
        statement: str,
        level: int,
        **kwargs: Any,
    ) -> None:
        """Initialize relative statement python import
        Args:
            line:  Line where the import was found in the file
            children: Packages or modules imports after the import statement
            parent: Package or module  where the children was imported
            statement: Plane text representation of the import found
            level: Integer holding the level of the relative import.
            **kwargs: Extra data passed

        Examples:
            from . import mixins
            from .mixins import UnUsedImportMixin
        """
        super().__init__(line, children, parent, statement, level, **kwargs)


class AbsoluteImportStatement(ImportFromStatement):
    """
    Class that represent an absolute import statement in python
    """

    def __init__(
        self, line: int, parent: str, children: List[str], statement: str, **kwargs: Any
    ):
        """Initialize relative statement python import
        Args:
            line:  Line where the import was found in the file
            children: Packages or modules imports after the import statement
            parent: Package or module  where the children was imported
            statement: Plane text representation of the import found
            **kwargs: Extra data passed

        Examples:
            from py_dep import mixins
            from mixins import UnUsedImportMixin

        Notes:
            An absolute import by default has a level equals to 0
        """
        self.level = 0
        super().__init__(line, children, parent, statement, **kwargs)


class ImportsCollectionFile:
    """
    Class to collect the meta information about the imports in a file
    """

    def __init__(self) -> None:
        self.imports: List = []
        self.relative_imports: List = []
        self.absolute_imports: List = []

    def register_import_from(
        self,
        line: int,
        children: List[str],
        statement: str,
        level: int,
        parent: str,
        **kwargs: Any,
    ) -> Union[AbsoluteImportStatement, RelativeImportStatement]:
        """Register absolute or relative import

        Notes:
            If the level of the current imports is equals to 0, that's mean that is a
            absolute import otherwise is a relative import

        Returns:
            The object that represent the relative or absolute import
        """
        import_from: Union[AbsoluteImportStatement, RelativeImportStatement]

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
        self, line: int, children: List[str], statement: str, **kwargs: Any
    ) -> ImportStatement:
        """Register simple import"""
        simple_import = ImportStatement(line, children, statement, **kwargs)
        self.imports.append(simple_import)
        return simple_import
