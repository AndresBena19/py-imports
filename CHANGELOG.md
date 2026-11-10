# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Released]

## [2.0.0] - 10 Nov 2026

### Changed
- **Breaking:** require Python 3.11+ (3.7–3.10 are end-of-life); `pyflakes>=3.0` (tested up to 4.1).
- Packaging moved from Poetry to PEP 621 metadata (`[project]`) built with `hatchling`; dev workflow uses `uv` (`uv.lock`).
- Linting/formatting consolidated into `ruff` (replaces flake8, black, isort, pylint and bandit); mypy runs in strict mode.
- GitHub Actions: a single `ci.yml` (lint + test matrix on Linux/macOS/Windows × 3.11–3.14 + Codecov) and a `release.yml` publishing via `pypa/gh-action-pypi-publish` (trusted publishing ready).
- `statement` now holds the exact source of the import (whole multi-line import, without trailing comments) instead of only its first physical line.
- Package ships a `py.typed` marker and an MIT `LICENSE` file.

### Added
- `PyImports.get_file_imports()` and `PyImports.get_dir_imports()` with precise return types.
- `pathlib.Path` / `os.PathLike` paths are accepted everywhere.

### Fixed
- Crash with pyflakes 3.x/4.x (`checker.make_tokens` no longer exists).
- Crash on import: `typing_extensions` was used but never declared as a dependency.
- `children_unused` was wrong for dotted (`import os.path` -> `"path"`) and aliased (`import a as b` -> `"a as b"`) imports.
- Files are read honoring PEP 263 encoding declarations and UTF-8 BOM.
- `PyImports.__enter__` is correctly typed (`Self`), so no `# type: ignore` is needed with `with PyImports() as m:`.
- Coverage config was never read (`.converagerc` typo); CI "backward compatibility" job only ran `pytest --version` instead of the tests.
- Examples now run from any working directory.

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
