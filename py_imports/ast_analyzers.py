"""AST classes to parse py files."""

import ast

from py_imports.base import ImportsCollectionFile
from py_imports.mixins import UnUsedImportMixin


ScopeNode = ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef


class AstImportAnalyzer(UnUsedImportMixin, ast.NodeVisitor):
    """Capture the import statements in a py module file.

    An import is "in an inner scope" only when it is defined inside a function or a
    class. Module-level guards such as ``if TYPE_CHECKING:``, ``try/except
    ImportError`` or ``if sys.version_info`` keep the import in the module scope.
    """

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
        self._scopes: list[ScopeNode] = []

    def _visit_scope(self, node: ScopeNode) -> None:
        """Track the function/class being traversed (the AST itself is not modified)."""
        self._scopes.append(node)
        try:
            self.generic_visit(node)
        finally:
            self._scopes.pop()

    visit_FunctionDef = _visit_scope
    visit_AsyncFunctionDef = _visit_scope
    visit_ClassDef = _visit_scope

    def _statement(self, node: ast.stmt) -> str:
        """Get the source text of the import statement (supports multi-line imports)."""
        segment = ast.get_source_segment(self.raw_content, node)
        if segment is not None:
            return segment
        return self.file_content[node.lineno - 1]

    def _scope_kwargs(self, node: ast.Import | ast.ImportFrom) -> dict[str, object]:
        """Metadata shared by every kind of import statement."""
        return {
            "aliases": [alias.asname for alias in node.names],
            "children_unused": self._unused_imports.get(node.lineno, []),
            "outer_parent_node": self._scopes[-1] if self._scopes else None,
            "scope": ".".join(scope.name for scope in self._scopes) or None,
        }

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
            **self._scope_kwargs(node),
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
            **self._scope_kwargs(node),
        )
        self.generic_visit(node)

    @property
    def imports_metadata(self) -> ImportsCollectionFile:
        """Get the imports collected in the file."""
        return self._imports_collector
