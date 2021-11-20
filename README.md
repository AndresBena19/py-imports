
![Py-Imports](https://github.com/AndresBena19/py-imports/blob/develop/img/icon-import-py.png?raw=true )
<p align="center">
    <em>Be aware about imports meta information </em>
</p>
<p align="center">
<a href="https://github.com/andresbena19/py-imports/actions?query=workflow%3ATest+event%3Apush+branch%3Amaster" target="_blank">
    <img src="https://github.com/tiangolo/fastapi/workflows/Test/badge.svg?event=push&branch=master" alt="Test">
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
<a href="https://results.pre-commit.ci/latest/github/pre-commit/pre-commit/master">
    <img src="https://results.pre-commit.ci/badge/github/pre-commit/pre-commit/master.svg" alt="pre-commit.ci status" style="max-width:100%;">
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

myself = "main.py"

# Let's introspect myself
with PyImports() as manager:
    imports_file = manager.get_imports(myself)

# Now you have access to the imports used in each file 
imports_file
{
 'main.py': <py_imports.base.models.ImportsCollectionFile object at 0x10b889220>
}

# Get details about the absolute, relative and standard imports in the file
collector_object = imports_file.get(myself)
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
    If some imports are located inside an inner scope, the import object will contain a boolean field 
    named `in_inner_scope` indicating that is located outside his default position (the top of the file or in the global scope),
    also will be included an attribute named `outer_parent_node` that will contain the `AST` node, to allow the user get more information
    about the data structure node parent that is around the import.

     ```Python 
     def foo():
        from pkg import moduleY, moduleZ
     ...
      ```
    In this case the absolute import is located inside a function named `foo`.
    
    ```Python
    ...  # After introspect the file
    
    absolute_imports = imports_file.absolute_imports
    absolute_imports[0].in_inner_scope -> True
    
    # it's possible to get the ast node parent with
    absolute_imports[0].outer_parent_node -> ast.AST object
</details>

## Notes

This library does not execute any part of the python  target code, this just make a static analysis over the code to describe the meta information about the imports in the file.
## License

This project is licensed under the terms of the MIT license.
