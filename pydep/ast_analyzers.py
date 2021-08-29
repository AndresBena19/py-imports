"""ast classes to parse py files"""
import ast
from typing import Any, Dict, Iterator, List


class AstImportAnalyzer(ast.NodeVisitor):
    """
    Capture the import statements in a py module file
    """

    # will be disable invalid-name alert in this class, because the builtin ast, does not
    # follow the snake_case format in his methods name
    # pylint: disable=C0103
    def __init__(self) -> None:
        super().__init__()
        self._imports: List = []
        self._imports_from: Dict = {
            "relative_imports": [],
            "absolute_imports": {},
        }

    def visit_Import(self, node: ast.Import) -> Any:
        """
        Capture the import statements that not used "from" keyword
        Args:
            node: ast node with the import data

        Examples:
            import x, y, z
        """
        imports: List[str] = [pkg_name.name for pkg_name in node.names]
        self._imports.append({"imports": imports, "line": node.lineno})
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
        """
        Capture the import statements that used "from" keyword
        Args:
            node: ast node with the import from data

        Examples:
            from .x import y --> level = 1
            from ..x import y --> level = 2

        Notes:
            Here is also capture the level, this will help us to determine if
            it was a absolute or relative import and how many packages traversed
            to import the object
        """
        imports: List[str] = [alias.name for alias in node.names]
        if node.level > 0:
            self._imports_from["relative_imports"].append(
                {
                    "level": node.level,
                    "imports": imports,
                    "line": node.lineno,
                    "module": node.module,
                }
            )

        else:
            self._imports_from["absolute_imports"][node.module] = {
                "level": node.level,
                "imports": imports,
                "line": node.lineno,
            }
        self.generic_visit(node)

    @property
    def imports(self) -> List[str]:
        """Get the import invoked with just statement import"""
        return self._imports

    @property
    def imports_from(self) -> Dict:
        """Get the import invoked with from and import statement"""
        return self._imports_from


class SetupAnalyzer(ast.NodeVisitor):
    """
    Capture the data from a setup.py in order to get information about the
    requirements used
    """

    requirement_setup_keys = ["install_requires", "extras_require"]
    setup_keyword = "setup"

    # will be disable invalid-name alert in this class, because the builtin ast, does not
    # follow the snake_case format in his methods name
    # pylint: disable=C0103
    def __init__(self) -> None:
        super().__init__()
        self._setup_requirements: List[str] = []

    def is_setup_py(self, node: ast.Call) -> bool:
        """
        Validate if the current statement call belong to a setup call inside
        setup.py
        Args:
            node: : ast node with the import data

        Notes:
            Must be validated if the node contains an id, because inside a
            setup.py could be more python statement

        """
        node_func_id: str = getattr(node.func, "id", None)
        return node_func_id == self.setup_keyword

    def get_setup_data(self, node: ast.Call) -> None:
        """Get the data from a setup call

        When is found a setup call the invocation is analyzed in order to get
        the parameters that contain what packages will be installed
        Args:
            node: ast node with the import data

        Notes:
            When setup is been call is analyzed what contains the next
            parameters
                * install_requires
                * extras_require
            Normally this parameters contain a list with the packages to
            install, but it's possible, that the value of the parameters will be
            another variables referencing another list o function that  return
            the list of packages

        Examples:
            setup(...,
                  install_requires=[
                    "flask==1.*",
                    "gitpython==3.1.0"
                  ],
                  tests_require=[
                    "codecov==2.0.15",
                    "coverage==4.5.2",
                  ]
        """
        target_parameters: Iterator = filter(
            lambda key: key.arg in self.requirement_setup_keys, node.keywords
        )
        for keyword in target_parameters:
            if isinstance(keyword.value, ast.List):
                requirements_in_setup: Iterator = map(
                    lambda key: key.value,  # type: ignore[attr-defined]
                    keyword.value.elts,
                )
                self._setup_requirements.extend(list(requirements_in_setup))

    def visit_Call(self, node: ast.Call) -> Any:
        """
        Capture every call and take actions when the call is made and object
        named "setup"
        Args:
            node:  ast node with the import data
        """
        if self.is_setup_py(node):
            self.get_setup_data(node)
        self.generic_visit(node)

    @property
    def requirements(self) -> List[str]:
        """Get setup requirements found"""
        return self._setup_requirements
