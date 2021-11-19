# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- The possibility to know if the imports is located inside a function, class or other python structure definition
- Attributes `outer_parent_node`, `in_inner_scope` in every concrete class (`AbsoluteImportStatement`, `RelativeImportStatement`, `ImportFromStatement`)

## [Released]

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
