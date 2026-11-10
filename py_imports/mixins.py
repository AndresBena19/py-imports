"""Mixins."""

import ast

from pyflakes import checker
from pyflakes.messages import UnusedImport


_ALIAS_SEPARATOR = " as "


def _pyflakes_name(node: ast.Import | ast.ImportFrom, alias: ast.alias) -> str:
    """Build the fully qualified name that pyflakes reports for an imported alias.

    Examples:
        import os.path            -> "os.path"
        from x import y           -> "x.y"
        from . import y           -> ".y"
        from ..pkg.mod import y   -> "..pkg.mod.y"
    """
    if isinstance(node, ast.Import):
        return alias.name

    prefix = "." * node.level
    if node.module:
        return f"{prefix}{node.module}.{alias.name}"
    return f"{prefix}{alias.name}"


class UnUsedImportMixin:
    """Mixin that provide features to validate if an import was used in the file."""

    raw_content: str

    def get_unused_import(self, tree: ast.AST | None = None) -> dict[int, list[str]]:
        """Get modules or packages that were imported but never used.

        Args:
            tree: Already parsed AST of ``raw_content``; parsed on demand if omitted.

        Returns:
            Mapping of the import statement line to the children (as written in the
            import statement) that are not used in the file.
        """
        if tree is None:
            tree = ast.parse(self.raw_content)

        reported: set[tuple[int, str]] = set()
        for message in checker.Checker(tree).messages:
            if isinstance(message, UnusedImport):
                name: str = message.message_args[0]
                reported.add((message.lineno, name.split(_ALIAS_SEPARATOR, 1)[0]))

        unused: dict[int, list[str]] = {}
        if not reported:
            return unused

        for node in ast.walk(tree):
            if not isinstance(node, ast.Import | ast.ImportFrom):
                continue
            for alias in node.names:
                if (node.lineno, _pyflakes_name(node, alias)) in reported:
                    unused.setdefault(node.lineno, []).append(alias.name)

        return unused
