"""General conftest"""
import os
from typing import Callable

import pytest
from git import Repo


@pytest.fixture
def set_up_file(tmp_path: str) -> Callable[[str, str, str], str]:
    """
    Dynamic fixture to create a tmp .py file to parse

    Args:
        tmp_path: temporal path
    """

    def create_file(content: str, extension: str, destine_path: str = "") -> str:
        """
         Create a dummy .py file with the context provided in imports

        Args:
            destine_path: Optional destine path to save the file
            content: content that will be included in the file
            extension: extension of the file

        Returns:
             path of the file generated
        """
        path = destine_path if destine_path else tmp_path
        file_path = os.path.join(path, f"example.{extension}")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        return file_path

    return create_file


@pytest.fixture
def set_up_git_repository(tmpdir: str) -> Callable[[str, str], Repo]:
    """Fixture to initialize a local repository
    Args:
        tmpdir: Temporal directory to host the repository

    Returns:
        Repo: Repository instance
    """

    def set_up(file_path: str, destine_path: str = "") -> Repo:
        path = destine_path if destine_path else tmpdir
        repo = Repo.init(path)
        repo.index.add([file_path])
        repo.index.commit("initial commit")
        return repo

    return set_up
