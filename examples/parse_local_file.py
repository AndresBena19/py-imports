"""Examples to parse imports in a single file."""
from pathlib import Path

from py_imports.manager import PyImports


CASES_DIR = Path(__file__).parent / "cases"

# It's possible to get the data file by file
with PyImports() as manager:
    file_imports = manager.get_imports(CASES_DIR / "module_file.py")
    file_imports_two = manager.get_imports(CASES_DIR / "module_file_two.py")

# It's possible just call the process and get a resume of all data parsed
with PyImports() as manager:
    manager.get_imports(CASES_DIR / "module_file.py")
    manager.get_imports(CASES_DIR / "module_file_two.py")
    imports = manager.imports_resume()

print(list(imports))
