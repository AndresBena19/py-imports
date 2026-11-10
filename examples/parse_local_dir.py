"""Examples to parse imports in a directory."""
from pathlib import Path

from py_imports.manager import PyImports


EXAMPLES_DIR = Path(__file__).parent

# It's possible to get the data directory by directory
with PyImports() as manager:
    file_imports_from_dir_one = manager.get_imports(EXAMPLES_DIR / "cases")
    file_imports_from_dir_two = manager.get_imports(EXAMPLES_DIR)

# It's possible just call the process and get a resume of all data parsed
with PyImports() as manager:
    manager.get_imports(EXAMPLES_DIR / "cases")
    manager.get_imports(EXAMPLES_DIR)
    imports = manager.imports_resume()

print(list(imports))
