# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Released]

## [1.3.0] - 19 Nov 2021

### Added
- The possibility to know if the imports are located inside inner scope ex. `function`, `class`, etc.
- Attribute `in_inner_scope` in every concrete class (`AbsoluteImportStatement`, `RelativeImportStatement`, `ImportFromStatement`) 
  to identify import inside a inner scope
- Attribute `outer_parent_node` that will contain the `AST` node referencing the structure that is around the import located in an inner scope. 

## [1.2.0] - 15 Nov 2021

### Added
- Add new classifiers in order to index the pypi package
  - `Topic :: Utilities`
  - ` Topic :: Software Development :: Libraries`
  - `Operating System :: Microsoft :: Windows`
  - `Operating System :: MacOS :: MacOS X`
  - `Operating System :: POSIX`

- Feature examples in README.md documentation in order to show the assumptions  taken to build the util and how to use it


## [1.1.0] - 14 Nov 2021

### Added
- CHANGELOG to track notable changes
- Metadata about unused imports in the concrete implementations (`AbsoluteImportStatement`, `RelativeImportStatement`, `ImportFromStatement`)

### Fixed
- Avoid silencing exceptions in `PyImports` context manager

## [1.0.0] - 13 Nov 2021

### Added

- Collector object `ImportsCollectionFile` to abstract the information about imports in the file
- `AbsoluteImportStatement`, `RelativeImportStatement`, `ImportFromStatement` concrete classes to describe each of the import types
- `AstImportAnalyzer` to traverse the abstract syntax tree python code
- Context manager `PyImports` to introspect imports in a file | directory
