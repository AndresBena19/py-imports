
![Py-Imports](https://github.com/AndresBena19/py-imports/blob/develop/img/icon-import-py.png?raw=true )
<p align="center">
    <em>Be aware about imports meta information </em>
</p>
<p align="center">
<a href="https://github.com/AndresBena19/py-imports/actions/workflows/ci.yml" target="_blank">
    <img src="https://github.com/AndresBena19/py-imports/actions/workflows/ci.yml/badge.svg?branch=develop" alt="CI">
</a>
<a href="https://codecov.io/gh/andresbena19/py-imports" target="_blank">
    <img src="https://img.shields.io/codecov/c/github/andresbena19/py-imports" alt="Coverage">
</a>
<a href="https://pypi.org/project/py-imports" target="_blank">
    <img src="https://img.shields.io/pypi/v/py-imports?color=%2334D058&label=pypi%20package" alt="Package version">
</a>
<a href="https://pypi.org/project/py-imports" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/py_imports.svg?color=%2334D058" alt="Supported Python versions">
</a>
<a href="https://results.pre-commit.ci/latest/github/AndresBena19/py-imports/develop">
    <img src="https://results.pre-commit.ci/badge/github/AndresBena19/py-imports/develop.svg" alt="pre-commit.ci status" style="max-width:100%;">
</a>
</p>


---

**Source Code**: <a href="https://github.com/andresbena19/py-imports" target="_blank"> https://github.com/andresbena19/py-imports
</a>
## Requirements

Python 3.11+

py-imports stands on the shoulders of giants:

* <a href="https://docs.python.org/3/library/ast.html" class="external-link" target="_blank">ast — Abstract Syntax Trees</a> to traverse python code.

## Installation

<div class="termy">

```console
$ pip install py-imports

---> 100%

All it's ready to begin
```

</div>

## Example

### Introspect it

* Create a file `main.py` with:

```Python
import logging
from py_imports.manager import PyImports
from .parse_local_dir import file_imports_from_dir_one

# Let's introspect myself
with PyImports() as manager:
    # A single file returns an ImportsCollectionFile
    collector_object = manager.get_file_imports(__file__)

    # A directory returns {file path: ImportsCollectionFile}
    # imports_by_file = manager.get_dir_imports("src/")

    # `get_imports` accepts either a file or a directory (str or pathlib.Path)
    # imports = manager.get_imports("src/")

# Get details about the absolute, relative and standard imports in the file
absolute_imports = collector_object.absolute_imports
relative_imports = collector_object.relative_imports
standard_imports = collector_object.imports

```

<details>
  <summary>Get meta information about absolute imports...<code>absolute_imports</code></summary>

   ```Python
     # Absolute imports
     #  --- from py_imports.manager import PyImports ---
     # If we introspect the object, we will get the following

     example_abs_import = absolute_imports[0]
     example_abs_import.children -> ['PyImports']
     example_abs_import.parent -> 'py_imports.manager'
     example_abs_import.statement -> 'from py_imports.manager import PyImports'
     example_abs_import.level -> 0
     example_abs_import.line -> 2

   ```
</details>

<details>
  <summary>Get meta information about relative imports...<code>relative_imports</code></summary>

   ```Python
     # relative imports
     #  --- from .parse_local_dir import file_imports_from_dir_one ---
     # If we introspect the object, we will get the following

     example_relative_import = relative_imports[0]
     example_abs_import.children -> ['file_imports_from_dir_one']
     example_abs_import.children_unused -> ['file_imports_from_dir_one']
     example_abs_import.parent -> 'parse_local_dir'
     example_abs_import.statement -> 'from .parse_local_dir import file_imports_from_dir_one'
     example_abs_import.level -> 1
     example_abs_import.line -> 3

   ```
</details>

<details>
  <summary>Get meta information about standard imports ...<code>standard_imports</code></summary>

   ```Python
        # standard imports
        #  --- import logging ---
        # If we introspect the object, we will get the following

        example_standard_import = standard_imports[0]
        example_standard_import.children -> ['logging']
        example_standard_import.children_unused -> ['logging']
        example_standard_import.statement -> 'import logging'
        example_standard_import.line -> 1

   ```
</details>


### Now you know more about you...
## Features
### Classify the imports found into three groups

<details>
  <summary>The util allow identifying and group the imports according  ...<code>relative imports, absolu...</code></summary>

   - ### Python Abstract Grammar
     The util allow identifying and group the imports according to the abstract grammar defined with python

          ...
          | Import(alias* names)
          | ImportFrom(identifier? module, alias* names, int? level)

   - ### Import types
     - ### Relative Imports

        Relative imports use leading dots. A single leading dot indicates a relative import, starting with the current package.
        Two or more leading dots indicate a relative import to the parent(s) of the current package, one level per dot after the first.

        - #### Schema syntax
          Relative imports must always use `from <> import`;`import <> `is always absolute.
          - **pydocs**: https://docs.python.org/3/reference/import.html#package-relative-imports
          - Metadata will be abstracted in `RelativeImportStatement` objects.
        - #### Ex.
          ```Python
          from .moduleY import spam
          from .moduleY import spam as ham
          from . import moduleY
          from ..subpackage1 import moduleY
          from ..subpackage2.moduleZ import eggs
          from ..moduleA import foo
          from ...package import bar
          from ...sys import path
          ```

     - ### Absolute Imports
        Absolute import involves full path i.e., from the project’s root folder to the desired module. An absolute import state that the resource
        to be imported using its full path from the project’s root folder.

        - #### Schema syntax
           Absolute imports may use either the `import <>` or `from <> import <>` syntax, but relative imports may only use the second form.
           - **PEP328**: https://www.python.org/dev/peps/pep-0328/
           - Metadata will be abstracted in `AbsoluteImportStatement` objects.
        - #### Ex.
          ```Python
          from moduleY import spam
          from moduleY import spam as ham

          # OR

          import XXX.YYY.ZZZ
          ```
     - ### Standard Imports
        Standard imports will be introspected and the data about it will be saved in an
        object named `ImportStatement`.

        - #### Schema syntax
           standard imports use  the `import <>`  syntax.
           - **PEP328**: https://www.python.org/dev/peps/pep-0328/
           - Metadata will be abstracted in `ImportStatement` objects.
        - #### Ex.
          ```Python
          import moduleY
          import moduleX
          ```
</details>

### If the imports are being used

<details>
  <summary>If some child it's not used in an import  ...<code>children_unused...</code></summary>

 - ### Unused imports
    If some child it's not used in an import, this will be added in  `children_unused` attribute in every concrete implementation that represent an imports.

    ```Python
    from ..subpackage1 import moduleY, moduleZ

    def foo() -> moduleZ:
        pass
    ```
    In this case the relative import  `from ..subpackage1 import moduleY, moduleZ` has a child that is not used in the file.
    ```Python
    ...  # After introspect the file

    relative_imports = imports_file.relative_imports
    relative_imports[0].children_unused -> ["moduleY"]

    # But the total of children present in this file
    relative_imports[0].children -> ["moduleY", "moduleZ"]
    ```
   **it's used `pyflakes` to determine the unused imports, because follow the same philosophy to get the
    information just using a static analysis.**
</details>

### If the imports are located inside an inner scope ex. function, class, etc.

<details>
  <summary>If the position of the import statement ...<code>in_inner_scope...</code></summary>

  - ### Imports in inner scopes
    An import is in an inner scope when it is defined inside a **function or a class**. In that case
    `in_inner_scope` is `True`, `outer_parent_node` holds the nearest enclosing `ast.FunctionDef`,
    `ast.AsyncFunctionDef` or `ast.ClassDef` node, and `scope` holds its dotted name (e.g. `"MyClass.method"`).

    Module-level guards such as `if TYPE_CHECKING:`, `try/except ImportError` or `if sys.version_info >= ...`
    do **not** create an inner scope: those imports keep `in_inner_scope == False`.

     ```Python
     class Service:
         def run(self):
             if ready:
                 from pkg import moduleY, moduleZ
      ```
    In this case the absolute import is located inside the method `run` of the class `Service`.

    ```Python
    ...  # After introspect the file

    absolute_imports = imports_file.absolute_imports
    absolute_imports[0].in_inner_scope -> True
    absolute_imports[0].scope -> "Service.run"
    absolute_imports[0].outer_parent_node -> ast.FunctionDef (name="run")
    ```
</details>

### Typed data model

Every import is an immutable (frozen, slotted) dataclass, also importable from the package root:

| Class | Statement | Extra fields |
|---|---|---|
| `ImportStatement` | `import a, b as c` | |
| `AbsoluteImportStatement` | `from a.b import c` | `module`, `level == 0` |
| `RelativeImportStatement` | `from ..a import b` | `module`, `level > 0` |

Common fields: `line`, `end_line`, `column`, `statement`, `names`, `scope`, `outer_parent_node`.
Each entry of `names` is an `ImportedName(name, asname, unused)`. The previous attributes are still available as
read-only properties: `children`, `aliases`, `children_unused`, `in_inner_scope`, `kind` and `parent` (alias of `module`).

```Python
from py_imports import PyImports

with PyImports() as manager:
    imports_file = manager.get_file_imports("main.py")

for statement in imports_file.all_imports:  # every import, in source order
    for imported in statement.names:
        print(statement.kind, statement.line, imported.name, imported.asname, imported.unused)
```

### Export the results as JSON

Every import object and `ImportsCollectionFile` has a `to_dict()` method returning plain, JSON-serializable data
(the AST node is replaced by its `scope` name).

```Python
import json

print(json.dumps(imports_file.to_dict(), indent=2))
# {"imports": [{"kind": "import", "line": 1, "end_line": 1, "column": 0,
#               "statement": "import numpy as np",
#               "names": [{"name": "numpy", "asname": "np", "unused": false}],
#               "in_inner_scope": false, "scope": null}],
#  "absolute_imports": [...], "relative_imports": [...]}
```

### Scanning directories

Directory scans walk sub-directories in sorted order and skip hidden directories (`.git`, `.venv`, `.tox`, ...),
virtual environments (any directory with a `pyvenv.cfg`), `__pycache__`, `node_modules` and `site-packages`.
Files that cannot be parsed (syntax errors, undecodable content) are skipped with a warning and listed in
`manager.parse_errors`, so one broken file no longer aborts the whole scan. Parsing a single file still raises.

## Notes

This library does not execute any part of the python  target code, this just make a static analysis over the code to describe the meta information about the imports in the file.
## Development

The project uses [uv](https://docs.astral.sh/uv/), [ruff](https://docs.astral.sh/ruff/) and [mypy](https://mypy-lang.org/).

```console
$ uv sync                      # create .venv with the dev dependencies
$ uv run pytest --cov          # tests + coverage
$ uv run ruff check . && uv run ruff format .
$ uv run mypy
$ uv run pre-commit install    # run the checks on every commit
```

## License

This project is licensed under the terms of the MIT license.
