"""Core feature to get imports"""
import ast
import logging
import os
from types import TracebackType
from typing import Dict, List, NoReturn, Optional, Type, TypeVar, Union, cast

from typing_extensions import Literal

from py_imports.ast_analyzers import AstImportAnalyzer
from py_imports.base.models import ImportsCollectionFile
from py_imports.exceptions import WrongFileExtension
from py_imports.mixins import UnUsedImportMixin


_PyImports = TypeVar("_PyImports", bound="PyImports")

logger = logging.getLogger(__name__)


class PyImports(UnUsedImportMixin):
    """
    Parse and capture every import data statement in a directory, file
    """

    def __init__(
        self,
    ) -> None:
        """Parse the imports from a directory or file
        Examples:
                1. Parse imports in an specific local directory
                    ...
                    with PyImports() as manager:
                        manager.get_imports(path=DIR_PATH)

                2. Parse imports in an specific local file
                    ...
                    with PyImports() as manager:
                        manager.get_imports(path=FILE_PATH)
        """
        self._imports: Dict[str, ImportsCollectionFile] = {}

    def __enter__(self) -> _PyImports:
        return cast(_PyImports, self)

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Literal[False]:
        return False

    @staticmethod
    def is_valid(path: str) -> Union[NoReturn, bool]:
        """Validate if the configuration provided has all the required parameters"""

        if os.path.isfile(path) and not path.endswith(".py"):
            raise WrongFileExtension("The file path provided must be .py")

        return True

    @staticmethod
    def get_ast_imports(path_file: str) -> ImportsCollectionFile:
        """Parse .py file to get imports

        Parse the .py file with the ast library in order to get the imports
        statement execute in a specific file
        Args:
            path_file: absolute path file to parse
        """
        with open(path_file, "r", encoding="utf-8") as file:
            file_content = file.readlines()
            file.seek(0)
            raw_content = file.read()
            analyzer = AstImportAnalyzer(file_content, raw_content)
            tree = ast.parse(raw_content)
            analyzer.visit(tree)

        return analyzer.imports_metadata

    def _process_py_files(
        self, files: List[str], root: str
    ) -> Dict[str, ImportsCollectionFile]:
        """Parse the .py in the files found

        Args:
            files: files found in the root directory
            root: root path where the files was found
        """
        imports_found: Dict[str, ImportsCollectionFile] = {}
        py_files = filter(lambda file: file.endswith(".py"), files)

        for path_file in py_files:
            absolute_path = os.path.join(root, path_file)
            file_imports = self._process_file(absolute_path)
            imports_found.update({absolute_path: file_imports})
            self._imports.update({absolute_path: file_imports})
        return imports_found

    def _process_file(self, path: str) -> ImportsCollectionFile:
        """Parse imports in a .py file
        Args:
            path: path of the .py file

        Returns:
            Dict: with the imports and from imports found

        """
        file_imports = self.get_ast_imports(path)
        self._imports.update({path: file_imports})
        return file_imports

    def _process_dir(self, path_dir: str) -> Dict[str, ImportsCollectionFile]:
        """Parse every file found in the directory
        Args:
            path_dir: absolute directory path
        """
        imports: Dict[str, ImportsCollectionFile] = {}
        for root, _, files in os.walk(path_dir):
            file_imports = self._process_py_files(files, root)
            imports.update(file_imports)
        return imports

    def get_imports(
        self, path: str
    ) -> Union[Dict[str, ImportsCollectionFile], ImportsCollectionFile, NoReturn]:
        """Get the imports in the context provided

        Returns:
            Dict: The imports found in the directory or files
        """
        imports: Union[Dict[str, ImportsCollectionFile], ImportsCollectionFile] = {}
        if self.is_valid(path):
            if os.path.isdir(path):
                imports = self._process_dir(path)
            else:
                imports = self._process_file(path)
        return imports

    def imports_resume(self) -> Dict[str, ImportsCollectionFile]:
        """Get all the imports parsed in the context"""
        return self._imports
