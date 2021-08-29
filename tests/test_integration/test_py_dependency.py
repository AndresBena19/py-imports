"""Integration test cases to validate the properly parse of python imports"""
import os
from typing import Callable, Dict, List, Tuple

from git import Repo
from pytest_mock import MockFixture

from py._path.local import LocalPath

from pydep.py_dependency import PyDependence, PyGitDependence
from tests.test_integration.validators import validate_flask_import


class TestPyDependence:
    """
    Test cases to validate the properly parse of imports in .py file
    """

    entry_point = PyDependence

    def test_get_import_in_a_local_file(
        self,
        set_up_file: Callable,
    ) -> None:
        """
        Validate if the import in a .py file are properly parse
        Args:
            set_up_file: Dynamic fixture to create .py test file

        Notes:
            Test case:
                from flask import request

        Expected results:
            * Must not exist any import without from
            * The Import must be an absolute import, that mean the level is
              equals to 0
            * Must exist just one module been imported from flask
            * The module request must be present in the modules imported from
              flask
            * The import must be placed in the first line
        """
        file_path = set_up_file("""from flask import request""")
        handler = self.entry_point()
        imports: Dict = handler.get_imports(file_path)

        file_imports = imports.get(file_path)

        assert file_imports, "Any import was found"
        imports_statements_found: List[Dict] = file_imports.get("imports")
        imports_from_statement_found: Dict = file_imports.get("imports_from")
        absolute_import_found = imports_from_statement_found.get("absolute_imports")

        assert absolute_import_found, "Any absolute import was found"
        imports_in_flask_package = absolute_import_found.get("flask")

        assert len(imports_statements_found) == 0
        assert imports_in_flask_package.get("level") == 0
        assert len(imports_in_flask_package.get("imports")) == 1
        assert "request" in imports_in_flask_package.get("imports")
        assert imports_in_flask_package.get("line") == 1

    def test_get_relative_import_in_a_local_file(
        self,
        set_up_file: Callable,
    ) -> None:
        """
        Validate if the relative imports in a .py file are properly parse
        Args:
            set_up_file: Dynamic fixture to create .py test file

        Notes:
            Test case:
                from ... import request

        Expected results:
            * Must not exist any import without from
            * The Import must be an relative import with the level equal to 3
            * Must exist just one module been imported equal to request
            * The import must be placed in the first line
        """
        file_path = set_up_file("""from ... import request""")
        handler = self.entry_point()
        imports: Dict = handler.get_imports(file_path)
        file_imports = imports.get(file_path)

        assert file_imports, "Any import was found"
        imports_statements_found: List = file_imports.get("imports")
        imports_from_statement_found = file_imports.get("imports_from")
        absolute_imports_found = imports_from_statement_found.get("relative_imports")[0]

        assert len(imports_statements_found) == 0
        assert absolute_imports_found.get("level") == 3
        assert absolute_imports_found.get("imports")[0] == "request"

    def test_get_import_without_statement_from_in_a_local_file(
        self,
        set_up_file: Callable,
    ) -> None:
        """
        Validate if the imports without from statements in a .py file are
        properly parse
        Args:
            set_up_file: Dynamic fixture to create .py test file

        Notes:
            Test case:
                import flask

        Expected results:
            * Must exist just one import in the file
            * Must exist just two module been imported from flask
            * The import must be placed in the first line
        """
        file_path = set_up_file("""import flask""")
        handler = self.entry_point()
        imports: Dict = handler.get_imports(file_path)
        validate_flask_import(imports, file_path)

    def test_get_import_excluding_internal_imports(
        self,
        py_package: Tuple,
    ) -> None:
        """
        Validate if the imports that make reference to an internal package are excluded
        Args:
            py_package: Fixture to instantiate a python package scenario

        Notes:
            This case is base in python package

            File 1:
                import django

            File 2:
                from module1 import django
                import flask

        Expected results:
            * Module1 must be excluded from the imports found
            * Must exist just one import in the file
            * Must exist just two module been imported from flask and keras
            * The import must be placed in the first line
        """
        package_dir, main_file_path = py_package
        handler = self.entry_point(omit_internal_imports=True, base_dir=package_dir)
        imports = handler.get_imports(main_file_path)
        validate_flask_import(imports, main_file_path)

    def test_get_import_without_unused_imports(
        self,
        set_up_file: Callable,
    ) -> None:
        """
        Validate if the imports that are not used in the .py are excluded
        Args:
            set_up_file: Dynamic fixture to create .py test file

        Notes:
            Test case:
                import django
                from x import flask, keras

        Expected results:
            * django and x.flask must be excluded because they are not used in the file
            * Any basic import or relative import must be found
            * Must be returned just the package call "x" because the module/implementation
              called keras was called
        """
        file_path = set_up_file("""import django\nfrom x import flask, keras\nkeras()""")
        handler = self.entry_point(omit_unused_imports=True)
        imports: Dict = handler.get_imports(file_path)
        file_imports = imports.get(file_path)

        assert file_imports, "Data no returned"
        assert file_imports.get("imports", []) == []

        imports_from: Dict = file_imports.get("imports_from", {})
        assert imports_from, "Data of import_from no returned"
        assert imports_from.get("relative_imports") == []
        assert imports_from.get("absolute_imports", {}).get("x")


class TestPyGitDependence:
    """
    Test cases to validate the imports parse when is used a git repository as
    source
    """

    REPOSITORY_NAME = "genetic-algorithm-equation"
    REPOSITORY_URL = f"git@github.com:AndresBena19/{REPOSITORY_NAME}.git"
    REPOSITORY_DIR = f"../repositories/{REPOSITORY_NAME}/"
    entry_point = PyGitDependence

    def test_get_imports_in_a_git_project(
        self,
        tmpdir: LocalPath,
        set_up_file: Callable[[str, str], str],
        set_up_git_repository: Callable[[str, str], Repo],
        mocker: MockFixture,
    ) -> None:
        """
        Validate if imports are parse properly in a git context
        Args:
            tmpdir: Temporary directory
            set_up_file: Dynamic fixture to create files
            set_up_git_repository: Dynamic fixture to initialize a git repository
            mocker: Fixture to mock objects

        Expected results:
            * Must exist just one import in the file
            * Must exist just two module been imported from flask and keras
            * The import must be placed in the first line
        """

        file_path = set_up_file(
            """import flask""", os.path.join(tmpdir.strpath, "example.py")
        )
        git_repository = set_up_git_repository(file_path, tmpdir.strpath)

        mocker.patch.object(
            self.entry_point, "clone_and_check_out", return_value=git_repository
        )
        dep = self.entry_point(git_url=self.REPOSITORY_URL)
        imports: Dict = dep.get_imports()
        validate_flask_import(imports, file_path)
