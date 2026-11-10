"""Example to introspect the same file that is executing the introspection."""
import logging  # noqa: F401 (intentionally unused, shows up in `children_unused`)
from pathlib import Path

from py_imports.manager import PyImports


MYSELF = Path(__file__)

# Let's introspect myself
with PyImports() as manager:
    collector_object = manager.get_imports(MYSELF)

# Get details about the absolute, relative and standard imports in the file
absolute_imports = collector_object.absolute_imports
relative_imports = collector_object.relative_imports
standard_imports = collector_object.imports

# Absolute imports
#  --- from pathlib import Path ---
example_abs_import = absolute_imports[0]
print(example_abs_import.parent, example_abs_import.children)  # pathlib ['Path']

# Standard imports
#  --- import logging ---
example_standard_import = standard_imports[0]
print(example_standard_import.children_unused)  # ['logging']

# Now you know more about you...
