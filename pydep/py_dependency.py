"""Core feature to get imports"""
import ast
import logging
import os
import shutil
from typing import Any, Dict, List, NoReturn, Optional, Union

from git import Repo

from pydep.ast_analyzers import AstImportAnalyzer
from pydep.base.models import ImportsCollectionFile
from pydep.exceptions import WrongFileExtension
from pydep.mixins import UnUsedImportMixin


logger = logging.getLogger(__name__)


class PyDependence(UnUsedImportMixin):
    """
    Parse and capture every import data statement in a directory, file
    """

    error_messages = {
        "required_git": "Must be provided a git url, if the attribute: {attr} "
        "was provided.",
        "required": "Must be provided at least a git url or path reference to "
        "local dir or file",
    }

    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        """Parse the imports from a directory or file

        Args:
            path: Path of the file to parse
            **kwargs: Extra config arguments

        Examples:
                1. Parse imports in an specific local directory
                    ...
                    dep = PyDependence(path=DIR_PATH)
                    dep.get_imports()

                2. Parse imports in an specific local file
                    ...
                    dep = PyDependence(path=FILE_PATH)
                    dep.get_imports()
        """
        self.base_dir: str = kwargs.get("base_dir", "")

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
            data = file.readlines()
            file.seek(0)
            analyzer = AstImportAnalyzer(data)
            tree = ast.parse(file.read())
            analyzer.visit(tree)

        return analyzer.imports_metadata

    def _process_py_files(self, files: List[str], root: str) -> Dict:
        """Parse the .py in the files found

        Args:
            files: files found in the root directory
            root: root path where the files was found
        """
        imports_found = {}
        py_files = filter(lambda file: file.endswith(".py"), files)

        for path_file in py_files:
            absolute_path = os.path.join(root, path_file)
            imports = self._process_file(absolute_path)
            imports_found.update({absolute_path: imports})
        return imports_found

    def _process_file(self, path: str) -> ImportsCollectionFile:
        """Parse imports in a .py file
        Args:
            path: path of the .py file

        Returns:
            Dict: with the imports and from imports found

        """
        return self.get_ast_imports(path)

    def _process_dir(self, path_dir: str) -> Dict:
        """Parse every file found in the directory
        Args:
            path_dir: absolute directory path
        """
        imports: Dict = {}
        for root, _, files in os.walk(path_dir):
            file_imports = self._process_py_files(files, root)
            imports.update(file_imports)
        return imports

    def get_imports(self, path: str) -> Union[Dict, ImportsCollectionFile, NoReturn]:
        """Get the imports in the context provided

        Returns:
            Dict: The imports found in the directory or files
        """
        imports: Union[Dict, ImportsCollectionFile] = {}
        if self.is_valid(path):
            if os.path.isdir(path):
                imports = self._process_dir(path)
            else:
                imports = self._process_file(path)
        return imports


class PyGitDependence(PyDependence):
    """
    Parse and capture imports data statement when is provided a git repository
    """

    def __init__(
        self,
        git_url: str,
        commit_id: Optional[str] = None,
        branch: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Parse imports in the context of a git repository
        Args:
            git_url: Git url of the repository to analyze
            commit_id: Hash id to parse a specific context on git timeline
            path: Path of the Directory/file to parse
            branch: Branch name to parse specific git branch context
            **kwargs:

        Keyword Args:
            omit_builtins: Bool to define if the builtins imports must be
                           omitted
            omit_internal_imports: Bool to define if will be omitted the imports that make
                                  relation to any own package

        Examples:
                1. Parse imports in an repository
                    ...
                    dep = PyDependence(git_url=REPOSITORY_URL)
                    dep.get_imports()

                2. Parse imports in an repository but in the context of the
                   specific commit id
                    ...
                    dep = PyDependence(git_url=REPOSITORY_URL, commit_id=COMMIT)
                    dep.get_imports()

                3. Parse imports in a but in the context of the specific branch
                    ...
                    dep = PyDependence(git_url=REPOSITORY_URL, branch="develop")
                    dep.get_imports()

        Raises:
            AssertError: If `branch` is provided but the git url not
            AssertError: If `commit_id` is provided but the git url not
        """

        self.git_url: str = git_url
        self.branch: Optional[str] = branch
        self.commit_id: Optional[str] = commit_id

        self.repository_name = self.git_url.split("/")[-1]
        self.repo = self.clone_and_check_out()

        super().__init__(**kwargs)

    def clone_and_check_out(self) -> Repo:
        """Clone a checkout

        The repository will be cloned and depending if the commit or branch was
        provided the context to analyze will change

        Returns:
            Repo: repository instance with the context provided
        """
        repo = Repo.clone_from(
            self.git_url,
            os.path.join("tmp", self.repository_name),
            branch=self.branch,
        )
        if self.commit_id:
            repo.git.checkout(self.commit_id)
        return repo

    @staticmethod
    def delete_repository(path: str) -> None:
        """delete the repository dir"""
        try:
            shutil.rmtree(path)
        except OSError:
            logger.exception("Error during repository deletion")

    def get_imports(  # type: ignore[override]
        self, path: str = ""
    ) -> Union[Dict, ImportsCollectionFile, NoReturn]:
        """Get the imports in the git context
        Returns:
            Dict: all the import found in the file or files

        Note:
            If the path is not provided will the parse imports will be executed over
            all the repository.
        """
        if not path:
            path = self.repo.working_dir
            logger.info("Will be parse the entire repository")

        imports = super().get_imports(path)
        self.delete_repository(path)
        return imports
