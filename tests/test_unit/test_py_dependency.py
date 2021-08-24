"""Unit test cases to validate PyDependence"""
import os
from typing import Callable
from unittest.mock import call

import pytest
from pytest_mock import MockerFixture

from pydep.exceptions import RequiredBaseDirError, WrongFileExtension
from pydep.py_dependency import PyDependence


class TestPyDependence:
    """
    Test cases to validate the properly parse of imports in .py file
    """

    IMPORT_TEST_CASE = """from flask import request"""

    entry_point = PyDependence

    def test_define_base_dir_properly_when_omit_internal_imports_is_provided(
        self, tmpdir: str, mocker: MockerFixture
    ) -> None:
        """
        Validate if the base_dir is properly defined, and the config option
        omit_internal_imports is True
        Args:
            tmpdir: Temporal dir
            mocker: Fixture to mock objects
        """
        logger_mock = mocker.patch("pydep.py_dependency.logger")
        mocker.patch.object(self.entry_point, "is_valid", return_value=True)
        mocker.patch.object(self.entry_point, "_process_dir")

        dep = self.entry_point(omit_internal_imports=True)
        dep.get_imports(tmpdir)

        assert dep.base_dir == tmpdir, f"The base_dir expected is: {tmpdir}"
        logger_mock.info.assert_called_with("default base dir: %s", tmpdir)

    def test_raise_error_when_omit_internal_imports_and_path_is_file(
        self,
        set_up_file: Callable,
    ) -> None:
        """
        Validate if RequiredBaseDirError is raised when is the path provided is a file
        and the config option omit_internal_imports is True
        Args:
            set_up_file: Dynamic fixture to create .py test file
        """
        file_path = set_up_file(self.IMPORT_TEST_CASE, "py")
        dep = self.entry_point(omit_internal_imports=True)
        with pytest.raises(RequiredBaseDirError):
            dep.get_imports(file_path)

    def test_raise_error_when_the_path_is_not_py_file(
        self,
        set_up_file: Callable,
    ) -> None:
        """
        Validate if WrongFileExtension is raised when is the path provided is a file
        if an extension different to .py
        """
        file_path = set_up_file(self.IMPORT_TEST_CASE, "toml")
        dep = self.entry_point(omit_internal_imports=True)
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
        mocker.patch("pydep.py_dependency.os.walk", return_value=test_directory_structure)

        dep = self.entry_point()
        dep.get_imports(tmpdir)

        expected_calls = [call(os.path.join(tmpdir, file)) for file in test_py_files]
        assert process_file_mock.call_count == 2
        process_file_mock.assert_has_calls(expected_calls, any_order=True)
