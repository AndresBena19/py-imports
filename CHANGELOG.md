# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## Added
- CHANGELOG to track notable changes
- add metadata about unused imports in the concrete implementations (`AbsoluteImportStatement`, `RelativeImportStatement`, `ImportFromStatement`)


## [1.0.0] - 13 Nov 2021

### Added

- add collector object `ImportsCollectionFile` to abstract the information about imports in the file
- add `AbsoluteImportStatement`, `RelativeImportStatement`, `ImportFromStatement` concrete classes to describe each of the import types
- add `AstImportAnalyzer` to traverse the abstract syntax tree python code
- context manager `PyImports` to introspect imports in a file|dir 
