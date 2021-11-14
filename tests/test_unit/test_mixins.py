"""Unit test cases to validate mixins"""

from typing import Callable

from py_imports.mixins import UnUsedImportMixin


# Disable because pylint assume that the classes used to group test
# are concrete implementations
# pylint: disable=no-self-use


class TestUnUsedImportMixin:
    """
    Test cases to validate the UnUsedImportMixin
    """

    mixin = UnUsedImportMixin

    def test_if_it_returned_the_unused_import_from_file(
        self, set_up_file: Callable
    ) -> None:
        """
        Validate if the unused import are properly detected

        Notes:
            Cases:
                from flask import request
                from module_one import function_one
                function_one()

        Expected result:
            * request from flask was not used in the file
        """
        file_path = set_up_file(
            """from flask import request\nfrom module import foo\nfoo()"""
        )
        unused_imports = UnUsedImportMixin.get_unused_import(file_path)
        assert unused_imports[0] == "flask.request"
