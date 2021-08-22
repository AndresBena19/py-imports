"""Integration test cases to validate the properly parse of python imports"""
from typing import Callable, Dict, List

from pydep.py_dependency import PyDependence


class TestPyDependence:
    """
    Test cases to validate the properly parse of imports in .py file
    """

    entry_point = PyDependence()

    def test_get_import_in_a_local_file(
        self,
        set_up_py_file: Callable[[str, str], str],
    ) -> None:
        """
        Validate if the import in a .py file are properly parse
        Args:
            set_up_py_file: Dynamic fixture to create .py test file

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
        file_path = set_up_py_file("""from flask import request""", "py")
        imports: Dict = self.entry_point.get_imports(file_path)

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
        set_up_py_file: Callable[[str, str], str],
    ) -> None:
        """
        Validate if the relative imports in a .py file are properly parse
        Args:
            set_up_py_file: Dynamic fixture to create .py test file

        Notes:
            Test case:
                from ... import request

        Expected results:
            * Must not exist any import without from
            * The Import must be an relative import with the level equal to 3
            * Must exist just one module been imported equal to request
            * The import must be placed in the first line
        """
        file_path = set_up_py_file("""from ... import request""", "py")
        imports: Dict = self.entry_point.get_imports(file_path)
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
        set_up_py_file: Callable[[str, str], str],
    ) -> None:
        """
        Validate if the imports without from statements in a .py file are
        properly parse
        Args:
            set_up_py_file: Dynamic fixture to create .py test file

        Notes:
            Test case:
                import flask, keras

        Expected results:
            * Must exist just one import in the file
            * Must exist just two module been imported from flask and keras
            * The import must be placed in the first line
        """
        file_path = set_up_py_file("""import flask, keras""", "py")
        imports: Dict = self.entry_point.get_imports(file_path)
        file_imports = imports.get(file_path)

        assert file_imports, "Any import was found"
        imports_without_from_statement_found: List[Dict] = file_imports.get("imports")
        import_found = imports_without_from_statement_found[0].get("imports")

        assert len(imports_without_from_statement_found) == 1
        assert import_found == ["flask", "keras"]
        assert imports_without_from_statement_found[0].get("line") == 1
