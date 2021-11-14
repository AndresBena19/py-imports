"""Mixins"""
import ast
import textwrap
from typing import Dict, List

from pyflakes import checker
from pyflakes.messages import UnusedImport


class UnUsedImportMixin:
    """
    Mixin that provide features to validate if an import was used in the file
    """

    raw_content: str

    def get_unused_import(self) -> Dict:
        """
        Get modules of packages not used but was imported

        Returns:
            Dict of the packages/modules not used in the file by line index
        """
        unused: Dict[int, List] = {}
        tree = ast.parse(self.raw_content)
        file_tokens = checker.make_tokens(textwrap.dedent(self.raw_content))
        analysis_result = checker.Checker(tree, file_tokens=file_tokens)

        for alert in analysis_result.messages:
            if not isinstance(alert, UnusedImport):
                continue

            alert_messages = [msg.split(".")[-1] for msg in alert.message_args]
            if alert.lineno in unused:
                unused[alert.lineno].append(*alert_messages)
            else:
                unused.update({alert.lineno: [*alert_messages]})

        return unused
