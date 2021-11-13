
![Py-Imports](img/icon-py-imports.png)
<p align="center">
    <em>Parse imports from .py file in a flexible way</em>
</p>
<p align="center">
<a href="https://github.com/andresbena19/py-imports/actions?query=workflow%3ATest+event%3Apush+branch%3Amaster" target="_blank">
    <img src="https://github.com/tiangolo/fastapi/workflows/Test/badge.svg?event=push&branch=master" alt="Test">
</a>
<a href="https://codecov.io/gh/andresbena19/py-imports" target="_blank">
    <img src="https://img.shields.io/codecov/c/github/andresbena19/py-imports" alt="Coverage">
</a>

</p>

---

**Source Code**: <a href="https://github.com/andresbena19/py-imports" target="_blank"> https://github.com/andresbena19/py-imports
</a>
## Requirements

Python 3.7+

py-imports stands on the shoulders of giants:

* <a href="https://docs.python.org/3/library/ast.html" class="external-link" target="_blank">ast — Abstract Syntax Trees</a> to traverse python code.

## Installation

<div class="termy">

```console
$ pip install py-imports

---> 100%
```

</div>

## Example

### Introspect it

* Create a file `main.py` with:

```Python
from py_imports.manager import PyImports

with PyImports() as manager:
    manager.get_imports("module_file.py")
    manager.get_imports("module_file_two.py")
    imports = manager.imports_resume()

```

## License

This project is licensed under the terms of the MIT license.
