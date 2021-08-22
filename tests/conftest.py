"""General conftest"""
import os
from typing import Callable

import pytest


@pytest.fixture
def set_up_py_file(tmp_path: str) -> Callable[[str, str], str]:
    """
    Dynamic fixture to create a tmp .py file to parse

    Args:
        tmp_path: temporal path
    """

    def create_file(content: str, extension: str) -> str:
        """
         Create a dummy .py file with the context provided in imports

        Args:
            content: content that will be included in the file
            extension: extension of the file

        Returns:
             path of the file generated
        """
        file_path = os.path.join(tmp_path, f"example.{extension}")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        return file_path

    return create_file
