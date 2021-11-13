from py_imports.manager import PyImports

# It's possible to get the data file by files
with PyImports() as manager:
    file_imports = manager.get_imports("../examples/cases/module_file.py")
    file_imports_two = manager.get_imports("../examples/cases/module_file_two.py")

# It's possible just call the process and get a resume of all data parsed
with PyImports() as manager:
    manager.get_imports("../examples/cases/module_file.py")
    manager.get_imports("../examples/cases/module_file_two.py")
    imports = manager.imports_resume()


