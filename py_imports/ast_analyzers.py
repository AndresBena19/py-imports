"""AST classes to parse py files."""

import ast
from collections.abc import Sequence
from typing import Any

from py_imports.base.models import (
    AbsoluteImportStatement,
    Guard,
    GuardCategory,
    GuardKind,
    ImportedName,
    ImportsCollectionFile,
    ImportStatement,
    RelativeImportStatement,
)
from py_imports.guards import (
    condition_category,
    handler_catches_import_error,
    suppresses_import_error,
    type_checking_test,
)
from py_imports.mixins import UnUsedImportMixin


ScopeNode = ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef


class AstImportAnalyzer(UnUsedImportMixin, ast.NodeVisitor):
    """Capture the import statements in a py module file.

    An import is "in an inner scope" only when it is defined inside a function or a
    class. Module-level guards such as ``if TYPE_CHECKING:``, ``try/except
    ImportError`` or ``if sys.version_info`` keep the import in the module scope;
    they are reported in ``guards`` instead.
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
        self._guards: list[Guard] = []

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

    def _visit_guarded(self, statements: Sequence[ast.stmt], guard: Guard) -> None:
        """Visit a block of statements while ``guard`` applies to them."""
        if not statements:
            return
        self._guards.append(guard)
        try:
            for statement in statements:
                self.visit(statement)
        finally:
            self._guards.pop()

    def _visit_body_and_else(
        self,
        node: ast.If | ast.For | ast.AsyncFor | ast.While,
        kind: GuardKind,
        condition: str,
        body_category: GuardCategory | None = None,
        else_category: GuardCategory | None = None,
    ) -> None:
        """Visit the ``body`` and ``orelse`` blocks of an if/for/while statement."""
        self._visit_guarded(
            node.body,
            Guard(
                kind=kind,
                branch="body",
                line=node.lineno,
                condition=condition,
                category=body_category,
            ),
        )
        self._visit_guarded(
            node.orelse,
            Guard(
                kind=kind,
                branch="orelse",
                line=node.lineno,
                condition=condition,
                category=else_category,
            ),
        )

    def visit_If(self, node: ast.If) -> None:
        """Track ``if``/``elif``/``else`` blocks."""
        is_type_checking = type_checking_test(node.test)
        body_category: GuardCategory | None
        else_category: GuardCategory | None
        if is_type_checking is None:
            body_category = else_category = condition_category(node.test)
        elif is_type_checking:
            body_category, else_category = "type_checking", "not_type_checking"
        else:
            body_category, else_category = "not_type_checking", "type_checking"
        self._visit_body_and_else(
            node, "if", ast.unparse(node.test), body_category, else_category
        )

    def visit_Try(self, node: ast.Try | ast.TryStar) -> None:
        """Track ``try``/``except``/``else``/``finally`` blocks."""
        catches_import_error = any(
            handler_catches_import_error(handler) for handler in node.handlers
        )
        self._visit_guarded(
            node.body,
            Guard(
                kind="try",
                branch="body",
                line=node.lineno,
                category="import_attempt" if catches_import_error else None,
            ),
        )
        for handler in node.handlers:
            self._visit_guarded(
                handler.body,
                Guard(
                    kind="try",
                    branch="handler",
                    line=handler.lineno,
                    condition=ast.unparse(handler.type) if handler.type else None,
                    category=(
                        "import_fallback"
                        if handler_catches_import_error(handler)
                        else None
                    ),
                ),
            )
        self._visit_guarded(
            node.orelse, Guard(kind="try", branch="orelse", line=node.lineno)
        )
        self._visit_guarded(
            node.finalbody, Guard(kind="try", branch="finalbody", line=node.lineno)
        )

    visit_TryStar = visit_Try

    def visit_With(self, node: ast.With | ast.AsyncWith) -> None:
        """Track ``with suppress(ImportError):`` blocks; other ``with`` are ignored."""
        if not any(suppresses_import_error(item) for item in node.items):
            self.generic_visit(node)
            return
        self._visit_guarded(
            node.body,
            Guard(
                kind="with",
                branch="body",
                line=node.lineno,
                condition=", ".join(ast.unparse(item) for item in node.items),
                category="import_attempt",
            ),
        )

    visit_AsyncWith = visit_With

    def visit_For(self, node: ast.For | ast.AsyncFor) -> None:
        """Track ``for`` loops (their body may never run)."""
        condition = f"{ast.unparse(node.target)} in {ast.unparse(node.iter)}"
        self._visit_body_and_else(node, "for", condition)

    visit_AsyncFor = visit_For

    def visit_While(self, node: ast.While) -> None:
        """Track ``while`` loops."""
        category = condition_category(node.test)
        self._visit_body_and_else(
            node, "while", ast.unparse(node.test), category, category
        )

    def visit_Match(self, node: ast.Match) -> None:
        """Track ``match``/``case`` blocks."""
        subject = ast.unparse(node.subject)
        for case in node.cases:
            condition = f"{subject}: {ast.unparse(case.pattern)}"
            if case.guard is not None:
                condition += f" if {ast.unparse(case.guard)}"
            self._visit_guarded(
                case.body,
                Guard(
                    kind="match",
                    branch="case",
                    line=case.pattern.lineno,
                    condition=condition,
                    category=condition_category(node.subject),
                ),
            )

    def _statement(self, node: ast.stmt) -> str:
        """Get the source text of the import statement (supports multi-line imports)."""
        segment = ast.get_source_segment(self.raw_content, node)
        if segment is not None:
            return segment
        return self.file_content[node.lineno - 1].strip()

    def _common_fields(self, node: ast.Import | ast.ImportFrom) -> dict[str, Any]:
        """Fields shared by every kind of import statement."""
        unused = self._unused_imports.get(node.lineno, [])
        return {
            "line": node.lineno,
            "end_line": node.end_lineno,
            "column": node.col_offset,
            "statement": self._statement(node),
            "names": tuple(
                ImportedName(
                    name=alias.name, asname=alias.asname, unused=alias.name in unused
                )
                for alias in node.names
            ),
            "scope": ".".join(scope.name for scope in self._scopes) or None,
            "guards": tuple(self._guards),
            "outer_parent_node": self._scopes[-1] if self._scopes else None,
        }

    def visit_Import(self, node: ast.Import) -> None:
        """Capture the import statements that do not use the "from" keyword.

        Args:
            node: ast node with the import data

        Examples:
            import x, y, z
        """
        self._imports_collector.add(ImportStatement(**self._common_fields(node)))
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
        statement_class = (
            RelativeImportStatement if node.level > 0 else AbsoluteImportStatement
        )
        self._imports_collector.add(
            statement_class(
                **self._common_fields(node), module=node.module or "", level=node.level
            )
        )
        self.generic_visit(node)

    @property
    def imports_metadata(self) -> ImportsCollectionFile:
        """Get the imports collected in the file."""
        return self._imports_collector
