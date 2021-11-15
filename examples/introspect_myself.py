"""Example to introspect the same file that is execution the introspection"""
import logging

from py_imports.manager import PyImports

from .parse_local_dir import file_imports_from_dir_one


MYSELF = "main.py"

# Let's introspect myself
with PyImports() as manager:
    imports_file = manager.get_imports(MYSELF)


# Get details about the absolute, relative and standard imports in the file
collector_object = imports_file.get(MYSELF)
absolute_imports = collector_object.absolute_imports
relative_imports = collector_object.relative_imports
standard_imports = collector_object.imports

# Absolute imports
#  --- from py_imports.manager import PyImports ---
# If we introspect the object, we will get the next
example_abs_import = absolute_imports[0]


# relative imports
#  --- from .parse_local_dir import file_imports_from_dir_one ---
# If we introspect the object, we will get the next
example_relative_import = relative_imports[0]

# standard imports
#  --- import logging ---
# If we introspect the object, we will get the next
example_standard_import = standard_imports[0]

# Now you know more about you...
