"""AST classes to parse py files."""

import ast
from typing import Any

from py_imports.base import ImportsCollectionFile
from py_imports.mixins import UnUsedImportMixin


class AstImportAnalyzer(UnUsedImportMixin, ast.NodeVisitor):
    """Capture the import statements in a py module file."""

    def __init__(
        self,
        file_content: list[str],
        raw_content: str,
        tree: ast.AST | None = None,
    ) -> None:
        """Initialize the analyzer.

        Args:
            file_content: Lines of the file.
            raw_content: Full content of the file.
            tree: Already parsed AST of ``raw_content``, to avoid parsing it twice.
        """
        self.file_content = file_content
        self.raw_content = raw_content
        super().__init__()
        self._imports_collector = ImportsCollectionFile()
        self._unused_imports = self.get_unused_import(tree)

    def visit(self, node: ast.AST) -> Any:
        """Visit a node, attaching a ``parent`` reference to each of its children."""
        for child in ast.iter_child_nodes(node):
            child.parent = node  # type: ignore[attr-defined]
        return super().visit(node)

    def _statement(self, node: ast.stmt) -> str:
        """Get the source text of the import statement (supports multi-line imports)."""
        segment = ast.get_source_segment(self.raw_content, node)
        if segment is not None:
            return segment
        return self.file_content[node.lineno - 1]

    @staticmethod
    def _outer_parent(node: ast.AST) -> ast.AST | None:
        """Return the parent node when the import is not at module level."""
        parent: ast.AST | None = getattr(node, "parent", None)
        return None if isinstance(parent, ast.Module) else parent

    def visit_Import(self, node: ast.Import) -> None:
        """Capture the import statements that do not use the "from" keyword.

        Args:
            node: ast node with the import data

        Examples:
            import x, y, z
        """
        self._imports_collector.register_import(
            line=node.lineno,
            children=[alias.name for alias in node.names],
            statement=self._statement(node),
            children_unused=self._unused_imports.get(node.lineno, []),
            outer_parent_node=self._outer_parent(node),
        )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Capture the import statements that use the "from" keyword.

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
        self._imports_collector.register_import_from(
            line=node.lineno,
            children=[alias.name for alias in node.names],
            parent=node.module or "",
            level=node.level,
            statement=self._statement(node),
            children_unused=self._unused_imports.get(node.lineno, []),
            outer_parent_node=self._outer_parent(node),
        )
        self.generic_visit(node)

    @property
    def imports_metadata(self) -> ImportsCollectionFile:
        """Get the imports collected in the file."""
        return self._imports_collector
