from py_imports.manager import PyImports

# It's possible to get the data file by files
with PyImports() as manager:
    file_imports_from_dir_one = manager.get_imports("../examples/cases/")
    file_imports_from_dir_two = manager.get_imports("../examples/")


# It's possible just call the process and get a resume of all data parsed
with PyImports() as manager:
    manager.get_imports("../examples/cases/")
    manager.get_imports("../examples/")
    imports = manager.imports_resume()


