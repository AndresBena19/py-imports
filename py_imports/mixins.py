"""Mixins"""
import ast
import textwrap
from typing import List

from pyflakes import checker
from pyflakes.messages import UnusedImport


class UnUsedImportMixin:
    """
    Mixin that provide features to validate if an import was used in the file
    """

    @staticmethod
    def get_unused_import(file_path: str) -> List:
        """
        Get modules of packages not used but was imported
        Args:
            file_path: File path to analyze

        Returns:
                List of the packages/modules not used in the file
        """
        unused = []
        with open(file_path, "r", encoding="utf-8") as file:
            data = file.read()
            tree = ast.parse(data)
            file_tokens = checker.make_tokens(textwrap.dedent(data))

        analysis_result = checker.Checker(tree, file_tokens=file_tokens)
        for alert in analysis_result.messages:
            if isinstance(alert, UnusedImport):
                unused.append(alert.message_args[0])
        return unused
