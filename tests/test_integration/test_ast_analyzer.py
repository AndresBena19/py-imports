"""Integration test cases to validate the properly parse of python imports"""
import ast
from typing import Callable

from py_imports.ast_analyzers import AstImportAnalyzer
from py_imports.manager import PyImports


class TestAstImportAnalyzer:
    """
    Test cases to validate AstImportAnalyzer behavior
    """

    entry_point = PyImports
    ast_analyzer = AstImportAnalyzer

    def test_properly_parse_and_object_generation_with_the_parse_imports(
        self,
        set_up_file: Callable,
    ) -> None:
        """
        Validate if the analyzer parser, register and generate correctly the imports found

        Expected results:
            * The import statement must be equal to the content in the file (line 1)
            * Must be found the object 'request' in the children imports
            * The imports must be a relative import with a level of 3

        """
        content_file = """from ... import request"""
        file_path = set_up_file(content_file)

        with open(file_path, "r", encoding="utf8") as file:
            data = file.readlines()
            file.seek(0)
            analyzer = self.ast_analyzer(data)
            tree = ast.parse(file.read())
            analyzer.visit(tree)

        imports = analyzer.imports_metadata

        assert imports.relative_imports[0].statement == content_file
        assert imports.relative_imports[0].children[0] == "request"
        assert imports.relative_imports[0].level == 3
