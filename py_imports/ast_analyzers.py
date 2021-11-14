"""ast classes to parse py files"""
import ast
from typing import Any, List

from py_imports.base import ImportsCollectionFile
from py_imports.mixins import UnUsedImportMixin


class AstImportAnalyzer(UnUsedImportMixin, ast.NodeVisitor):
    """
    Capture the import statements in a py module file
    """

    # will be disable invalid-name alert in this class, because the builtin ast, does not
    # follow the snake_case format in his methods name
    # pylint: disable=C0103
    def __init__(self, file_content: List[str], raw_content: str) -> None:
        self.file_content = file_content
        self.raw_content = raw_content
        super().__init__()
        self._imports_collector = ImportsCollectionFile()
        self._unused_imports = self.get_unused_import()

    def visit_Import(self, node: ast.Import) -> Any:
        """
        Capture the import statements that not used "from" keyword
        Args:
            node: ast node with the import data

        Examples:
            import x, y, z
        """
        imports: List[str] = [pkg_name.name for pkg_name in node.names]

        self._imports_collector.register_import(
            line=node.lineno,
            children=imports,
            statement=self.file_content[node.lineno - 1],
            children_unused=self._unused_imports.get(node.lineno, []),
        )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
        """
        Capture the import statements that used "from" keyword
        Args:
            node: ast node with the import from data

        Examples:
            from .x import y --> level = 1
            from ..x import y --> level = 2

        Notes:
            Here is also capture the level, this will help us to determine if
            it was a absolute or relative import and how many packages traversed
            to import the object
        """
        imports: List[str] = [alias.name for alias in node.names]
        self._imports_collector.register_import_from(
            line=node.lineno,
            children=imports,
            parent=node.module if node.module else "",
            level=node.level,
            statement=self.file_content[node.lineno - 1],
            children_unused=self._unused_imports.get(node.lineno, []),
        )
        self.generic_visit(node)

    @property
    def imports_metadata(self) -> ImportsCollectionFile:
        """Get the import invoked with just statement import"""
        return self._imports_collector
