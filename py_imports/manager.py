"""Core feature to get imports."""

import ast
import logging
import os
import tokenize
from types import TracebackType
from typing import Literal, Self

from py_imports.ast_analyzers import AstImportAnalyzer
from py_imports.base.models import ImportsCollectionFile
from py_imports.exceptions import WrongFileExtension
from py_imports.mixins import UnUsedImportMixin


logger = logging.getLogger(__name__)

StrPath = str | os.PathLike[str]


class PyImports(UnUsedImportMixin):
    """Parse and capture every import data statement in a directory, file.

    Examples:
        1. Parse imports in an specific local directory
            with PyImports() as manager:
                manager.get_imports(path=DIR_PATH)

        2. Parse imports in an specific local file
            with PyImports() as manager:
                manager.get_imports(path=FILE_PATH)
    """

    def __init__(self) -> None:
        self._imports: dict[str, ImportsCollectionFile] = {}

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        return False

    @staticmethod
    def is_valid(path: StrPath) -> bool:
        """Validate that the path provided is a directory or a ``.py`` file.

        Raises:
            WrongFileExtension: if the path is a file without the ``.py`` extension.
        """
        path = os.fspath(path)
        if os.path.isfile(path) and not path.endswith(".py"):
            raise WrongFileExtension("The file path provided must be .py")

        return True

    @staticmethod
    def get_ast_imports(path_file: StrPath) -> ImportsCollectionFile:
        """Parse .py file to get imports.

        Parse the .py file with the ast library in order to get the imports
        statement execute in a specific file. The file encoding is detected
        following PEP 263 (coding cookie / BOM), defaulting to UTF-8.

        Args:
            path_file: absolute path file to parse
        """
        with tokenize.open(path_file) as file:
            raw_content = file.read()

        tree = ast.parse(raw_content, filename=os.fspath(path_file))
        analyzer = AstImportAnalyzer(
            raw_content.splitlines(keepends=True), raw_content, tree
        )
        analyzer.visit(tree)
        return analyzer.imports_metadata

    def _process_py_files(
        self, files: list[str], root: str
    ) -> dict[str, ImportsCollectionFile]:
        """Parse the .py in the files found.

        Args:
            files: files found in the root directory
            root: root path where the files was found
        """
        imports_found: dict[str, ImportsCollectionFile] = {}
        for path_file in files:
            if not path_file.endswith(".py"):
                continue
            absolute_path = os.path.join(root, path_file)
            imports_found[absolute_path] = self._process_file(absolute_path)
        return imports_found

    def _process_file(self, path: str) -> ImportsCollectionFile:
        """Parse imports in a .py file.

        Args:
            path: path of the .py file

        Returns:
            The imports found in the file.
        """
        file_imports = self.get_ast_imports(path)
        self._imports[path] = file_imports
        return file_imports

    def _process_dir(self, path_dir: str) -> dict[str, ImportsCollectionFile]:
        """Parse every file found in the directory.

        Args:
            path_dir: absolute directory path
        """
        imports: dict[str, ImportsCollectionFile] = {}
        for root, _, files in os.walk(path_dir):
            imports.update(self._process_py_files(files, root))
        return imports

    def get_imports(
        self, path: StrPath
    ) -> dict[str, ImportsCollectionFile] | ImportsCollectionFile:
        """Get the imports in the path provided.

        Args:
            path: A directory or a ``.py`` file.

        Returns:
            A mapping of file path to imports when ``path`` is a directory, otherwise
            the imports found in the file.
        """
        path = os.fspath(path)
        self.is_valid(path)
        if os.path.isdir(path):
            return self._process_dir(path)
        return self._process_file(path)

    def get_file_imports(self, path: StrPath) -> ImportsCollectionFile:
        """Get the imports of a single ``.py`` file.

        Raises:
            WrongFileExtension: if the path is a file without the ``.py`` extension.
            IsADirectoryError: if the path is a directory.
        """
        path = os.fspath(path)
        self.is_valid(path)
        if os.path.isdir(path):
            raise IsADirectoryError(path)
        return self._process_file(path)

    def get_dir_imports(self, path: StrPath) -> dict[str, ImportsCollectionFile]:
        """Get the imports of every ``.py`` file in a directory (recursively).

        Raises:
            NotADirectoryError: if the path is not a directory.
        """
        path = os.fspath(path)
        if not os.path.isdir(path):
            raise NotADirectoryError(path)
        return self._process_dir(path)

    def imports_resume(self) -> dict[str, ImportsCollectionFile]:
        """Get all the imports parsed in the context."""
        return self._imports
