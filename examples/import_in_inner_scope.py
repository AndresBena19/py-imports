"""Example to introspect a file that has an import inside a function."""
from pathlib import Path

from py_imports.manager import PyImports


file_path = Path(__file__).parent / "cases" / "in_inner_scope.py"

with PyImports() as manager:
    imports_file = manager.get_imports(file_path)

absolute_import_found = imports_file.absolute_imports[0]

print(absolute_import_found.in_inner_scope)  # True

# The outer parent node is the `foo` function definition
print(absolute_import_found.outer_parent_node.name)  # foo
