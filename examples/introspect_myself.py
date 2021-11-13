"""Example to introspect the same file that execution the introspection"""
from py_imports.manager import PyImports


MYSELF = "introspect_myself.py"

# Let's introspect myself
with PyImports() as manager:
    manager.get_imports(MYSELF)
    imports = manager.imports_resume()


# Now yo have access to the import used in each file
print(imports)

# Get details about the absolute, relative and standard import in the file
collector_object = imports.get(MYSELF)
absolute_imports = collector_object.absolute_imports
relative_imports = collector_object.relative_imports
imports = collector_object.imports

# It's obvious that in this file, theare just one absolute import
# from py_imports.manager import PyImports
# If we introspect the object, wi will get the next
print(absolute_imports[0])
