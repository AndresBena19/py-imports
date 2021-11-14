"""Integration test cases to validate the properly parse of python imports"""
from typing import Callable, List, Tuple

from py_imports.base.models import ImportStatement
from py_imports.manager import PyImports


class TestPyImports:
    """
    Test cases to validate the properly parse of imports in .py file
    """

    entry_point = PyImports

    def test_get_absolute_import_in_a_local_file(
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
            * Must not exist any relative import without from
            * The Import must be an absolute import, that mean the level is
              equals to 0
            * Must exist just one module been imported from flask
            * The module request must be present in the modules imported from
              flask
            * The import must be placed in the first line
        """
        file_path = set_up_file("""from flask import request""")
        with self.entry_point() as handler:  # type: ignore
            imports = handler.get_imports(file_path)  # type: ignore

            assert imports, "Any import was found"
            assert imports.absolute_imports, "Any absolute import was found"

            absolute_import = imports.absolute_imports[0]

            assert len(imports.relative_imports) == 0
            assert absolute_import.parent == "flask"
            assert absolute_import.level == 0
            assert len(absolute_import.children) == 1
            assert absolute_import.children[0] == "request"
            assert absolute_import.line == 1

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
        with self.entry_point() as handler:  # type: ignore
            imports = handler.get_imports(file_path)  # type: ignore

            assert imports, "Any import was found"
            assert imports.relative_imports, "Any relative import was found"

            relative_import = imports.relative_imports[0]
            assert len(imports.imports) == 0
            assert relative_import.level == 3
            assert relative_import.children[0] == "request"

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
        with self.entry_point() as handler:  # type: ignore
            imports = handler.get_imports(file_path)  # type: ignore

            assert imports, "Any import was found"
            imports_without_from_statement_found: List[ImportStatement] = imports.imports
            import_found = imports_without_from_statement_found[0].children

            assert len(imports_without_from_statement_found) == 1
            assert import_found[0] == "flask"
            assert imports_without_from_statement_found[0].line == 1

    def test_get_import_in_a_local_directory(
        self, py_package: Tuple[str, List[str]]
    ) -> None:
        """
        Validate if it's correctly parse the .py files found in a folder or package

        Notes:
            Test case:
                file # 1
                    **empty**

                file #2
                    import django

                file #3
                    import flask
                    from module1 import django

        Expected results:
            * The amount of file parser must be the same of .py files found
              in the folder|package

            File #1
                * There is nothing here
            File #2
                * Must exist a import statement with a child module named 'django'
            File #3
                * Must exist a import statement with a child module named 'flask'
                * Must exist and absolute import with a child named 'django' and with a
                  parent named 'module1'
        """
        dir_path, file_paths = py_package
        [first_file, second_file, third_file] = file_paths

        with self.entry_point() as handler:  # type: ignore
            handler.get_imports(dir_path)
            imports = handler.imports_resume()  # type: ignore

            assert len(imports.keys()) == len(file_paths)
            assert len(imports[first_file].imports) == 0
            assert len(imports[first_file].absolute_imports) == 0
            assert len(imports[first_file].relative_imports) == 0

            assert imports[second_file].imports[0].children[0] == "django"

            assert imports[third_file].imports[0].children[0] == "flask"
            assert imports[third_file].absolute_imports[0].children[0] == "django"
            assert imports[third_file].absolute_imports[0].parent == "module1"

    def test_get_imports_in_a_local_file_with_unused_imports(
        self,
        set_up_file: Callable,
    ) -> None:
        """
        Validate if the metadata about unused import are properly defined

        Notes:
            Cases:
                import flask
                from module1.doo import django, foo

                flask()

        Expected results:
            * Must be 2 statement not used in the file
            * django and foo are the two imports not used in the file
        """
        file_path = set_up_file(
            """import flask\nfrom module1.doo import django, foo\nflask()"""
        )

        with self.entry_point() as handler:  # type: ignore
            imports = handler.get_imports(file_path)  # type: ignore

            assert imports, "Any import was found"
            import_unused_found = imports.absolute_imports[0].children_unused

            assert len(import_unused_found) == 2
            assert import_unused_found == ["django", "foo"]
