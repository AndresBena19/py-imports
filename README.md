
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
</p>


---

**Source Code**: <a href="https://github.com/andresbena19/py-imports" target="_blank"> https://github.com/andresbena19/py-imports
</a>
## Requirements :wrench: :hammer: :nut_and_bolt:

Python 3.7+

py-imports stands on the shoulders of giants:

* <a href="https://docs.python.org/3/library/ast.html" class="external-link" target="_blank">ast — Abstract Syntax Trees</a> to traverse python code.

## Installation :computer:

<div class="termy">

```console
$ pip install py-imports

---> 100%

All it's ready to begin 
```

</div>

## Example :paperclip:

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


### Now you know more about you... :lotus_position:
## Features :sunny:
### :sunglasses: Classify the imports found into three groups
      -  Python Abstract Grammar
          | Import(alias* names)
          | ImportFrom(identifier? module, alias* names, int? level)

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

### :sunglasses: Validate if the imports are being used 
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
    relative_imports[0].children_unused = ["moduleY"]
    
    # But the total of children present in this file 
    relative_imports[0].children = ["moduleY", "moduleZ"]
    ```
   :eyes: **it's used `pyflakes` to determine the unused imports, because follow the same philosophy to get the 
    information just using a static analysis.**
## Notes :bookmark:

This library does not execute any part of the python  target code, this just make a static analysis over the code to describe the meta information about the imports in the file.
## License :traffic_light:

This project is licensed under the terms of the MIT license.
