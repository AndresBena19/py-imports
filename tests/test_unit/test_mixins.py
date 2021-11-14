"""Unit test cases to validate mixins"""

from py_imports.mixins import UnUsedImportMixin


# Disable because pylint assume that the classes used to group test
# are concrete implementations
# pylint: disable=no-self-use


class TestUnUsedImportMixin:
    """
    Test cases to validate the UnUsedImportMixin
    """

    class TestCase(UnUsedImportMixin):
        """test class"""

        def __init__(self, raw_content: str) -> None:
            self.raw_content = raw_content

    def test_if_it_returned_the_unused_import_from_file(self) -> None:
        """
        Validate if the unused import are properly detected

        Notes:
            Cases:
                from flask import request
                from module_one import function_one
                function_one()

        Expected result:
            * In the line 1, request from flask was not used in the file
        """

        raw_content = """from flask import request\nfrom module import foo\nfoo()"""

        test_instance = self.TestCase(raw_content)
        unused_imports = test_instance.get_unused_import()
        assert unused_imports[1] == ["request"]
