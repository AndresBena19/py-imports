"""Example to introspect a file that has import inside a function"""

from py_imports.manager import PyImports


file_path = "./cases/in_inner_scope.py"
# Let's introspect myself
with PyImports() as manager:
    imports_file = manager.get_imports(file_path)


absolute_import_found = imports_file.absolute_imports[0]

print(absolute_import_found.in_inner_scop)

# The function parent name must be foo
print(absolute_import_found.in_inner_scope)
