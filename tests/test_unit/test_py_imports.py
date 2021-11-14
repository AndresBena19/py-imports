"""Unit test cases to validate PyImports"""
import os
from typing import Callable
from unittest.mock import call

import pytest
from pytest_mock import MockerFixture

from py_imports.exceptions import WrongFileExtension
from py_imports.manager import PyImports


class TestPyImports:
    """
    Test cases to validate the properly parse of imports in .py file
    """

    IMPORT_TEST_CASE = """from flask import request"""

    entry_point = PyImports

    def test_raise_error_when_the_path_is_not_py_file(
        self,
        tmpdir: str,
        set_up_file: Callable,
    ) -> None:
        """
        Validate if WrongFileExtension is raised when is the path provided is a file
        if an extension different to .py
        """
        path = os.path.join(tmpdir, "pyproject.toml")
        file_path = set_up_file(self.IMPORT_TEST_CASE, path)
        with self.entry_point() as dep:  # type: ignore
            with pytest.raises(WrongFileExtension):
                dep.get_imports(file_path)

    def test_py_files_are_filtered_and_processed_when_is_provided_a_directory(
        self,
        tmpdir: str,
        mocker: MockerFixture,
    ) -> None:
        """
        Validate if just the .py files are properly filtered and processed in order to get
        the imports
        Args:
            tmpdir: Temporal dir
            mocker: Fixture to mock objects
        """
        test_py_files = ["main.py", "product.py"]
        others_files = ["py_project.toml"]
        test_directory_structure = [(tmpdir, ["test_dir"], test_py_files + others_files)]

        process_file_mock = mocker.patch.object(self.entry_point, "_process_file")
        mocker.patch("py_imports.manager.os.walk", return_value=test_directory_structure)

        with self.entry_point() as dep:  # type: ignore
            dep.get_imports(tmpdir)
            expected_calls = [call(os.path.join(tmpdir, file)) for file in test_py_files]
            assert process_file_mock.call_count == 2
            process_file_mock.assert_has_calls(expected_calls, any_order=True)
