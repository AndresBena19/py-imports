"""General conftest"""
import os
from typing import Callable, List, Tuple

import pytest


# Disable because pylint assume that the fixture as a parameters are a redefinition
# pylint: disable=redefined-outer-name


@pytest.fixture
def set_up_file(tmp_path: str) -> Callable[[str, str], str]:
    """
    Dynamic fixture to create a tmp file to parse

    Args:
        tmp_path: temporal path
    """

    def create_file(content: str, destine_path: str = "") -> str:
        """
         Create a dummy file with the context provided in imports

        Args:
            destine_path: Optional destine path to save the file
            content: content that will be included in the file

        Returns:
             path of the file generated

        Notes:
            By default it's created a .py file with the name example, using a temp
            path provided by a pytest fixture 'tmp_path'
        """
        path = destine_path if destine_path else os.path.join(tmp_path, "example.py")
        with open(path, "w", encoding="utf-8") as file:
            file.write(content)
        return path

    return create_file


@pytest.fixture
def py_package(tmpdir: str, set_up_file: Callable[[str, str], str]) -> Tuple[str, List]:
    """
    Fixture to create a temporal python package

    Args:
        set_up_file: Dynamic fixture to create files
        tmpdir: temporal directory path
    """

    first_file = set_up_file("", os.path.join(tmpdir, "__init__.py"))
    second_file = set_up_file("""import django""", os.path.join(tmpdir, "module1.py"))
    third_file = set_up_file(
        """import flask\nfrom module1 import django""", os.path.join(tmpdir, "main.py")
    )

    return tmpdir, [first_file, second_file, third_file]
