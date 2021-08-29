"""Mixins"""
import ast
import copy
import os
import textwrap
from typing import Dict, Iterable, List, Tuple

from pyflakes import checker
from pyflakes.messages import UnusedImport


class UnUsedImportMixin:
    """
    Mixin that provide features to validate if an import was used in the file
    """

    @staticmethod
    def get_unused_import(file_path: str) -> List:
        """
        Get modules of packages not used but was imported
        Args:
            file_path: File path to analyze

        Returns:
                List of the packages/modules not used in the file
        """
        unused = []
        with open(file_path, "r", encoding="utf-8") as file:
            data = file.read()
            tree = ast.parse(data)
            file_tokens = checker.make_tokens(textwrap.dedent(data))

        analysis_result = checker.Checker(tree, file_tokens=file_tokens)
        for alert in analysis_result.messages:
            if isinstance(alert, UnusedImport):
                unused.append(alert.message_args[0])
        return unused

    def clean_unused_imports(self, imports: List, import_from: Dict, path: str) -> Tuple:
        """
        Filter and exclude unused imports from the report get it in the imports
        and imports from variables
        Args:
            imports: Imports with the schema "import x,y,z, found
            import_from: Imports withe the schema "from x import y, z found
            path: Path of the file

        Returns:
            The same objects provided but without the unused imports
        """
        unused_imports = self.get_unused_import(path)
        unused_without_from = filter(lambda imp: "." not in imp, unused_imports)
        unused_with_from = filter(lambda imp: "." in imp, unused_imports)

        self.clean_import_without_from(imports, unused_without_from)
        self.clean_absolute_imports(import_from, unused_with_from)
        self.clean_relative_imports(import_from, unused_with_from)

        return imports, import_from

    @staticmethod
    def clean_import_without_from(imports: List, unused_without_from: Iterable) -> None:
        """
        Filter an exclude unused imports from imports statement that dont used from prefix
        Args:
            imports: Imports with the schema "import x,y,z, found
            unused_without_from: Unused imports found in the file

        Returns:
            The same objects "imports" provided but without the unused imports

        """
        for index, import_ in enumerate(copy.deepcopy(imports)):
            imports_without_from = import_.get("imports")
            used_imports = list(
                filter(lambda pkg: pkg not in unused_without_from, imports_without_from)
            )
            if used_imports:
                import_["imports"] = used_imports
            else:
                # If it's not found data, all the record and his metadata is deleted
                del imports[index]

    @staticmethod
    def clean_absolute_imports(imports_from: Dict, unused_with_from: Iterable) -> None:
        """
        Filter an exclude unused imports from absolute imports found
        Args:
            unused_with_from: Unused imports found in the file
            imports_from: Imports with the schema "from x import y, z found
        """
        absolute_imports = copy.deepcopy(imports_from.get("absolute_imports", {}))
        for package, metadata in absolute_imports.items():
            package_dot_notation = [
                f"{package}.{module}" for module in metadata.get("imports")
            ]
            used_imports_from = list(
                filter(lambda pkg: pkg not in unused_with_from, package_dot_notation)
            )

            if not used_imports_from:
                # If any module of implementation is used, all the imports is exclude from
                # the dict
                del imports_from["absolute_imports"][package]
            else:
                transform_imports = [imp.split(".")[-1] for imp in used_imports_from]
                imports_from["absolute_imports"][package]["imports"] = transform_imports

    @staticmethod
    def clean_relative_imports(imports_from: Dict, unused_with_from: Iterable) -> None:
        """
         Filter an exclude unused imports from absolute imports found
        Args:
            imports_from: Imports with the schema "from .x import y, z found
            unused_with_from: Unused imports found in the file
        """
        relative_imports = copy.deepcopy(imports_from.get("relative_imports", {}))
        for index, metadata in enumerate(relative_imports):
            main_module = metadata.get("module")
            level = metadata.get("level")
            package_dot_notation = [
                f"{'.' * level}{main_module}.{module}"
                for module in metadata.get("imports")
            ]
            rel_used_imports_from = list(
                filter(lambda pkg: pkg not in unused_with_from, package_dot_notation)
            )

            if not rel_used_imports_from:
                del imports_from["relative_imports"][index]
            else:
                transform_imports = [imp.split(".")[-1] for imp in rel_used_imports_from]
                imports_from["relative_imports"][index]["imports"] = transform_imports


class InternalPackagesMixin:
    """
    Mixin that provide features to validate if a module or package is a internal

    Notes:
        internal: a own packages created in the project
    """

    flag_file = "__init__.py"

    def get_internal_packages(self, dir_path: str) -> List:
        """
        Get python packages base in the dir path provided
        Args:
            dir_path: Root path to search python packages

        Returns:
            List with the python packages found
        """
        internal_packages = []
        level = 0
        for root, _, files in os.walk(dir_path):
            if self.flag_file in files:
                internal_packages.append({"pkg": root.split("/")[-1], "level": level})
            level += 1
        return internal_packages

    @staticmethod
    def get_root_modules(dir_path: str) -> List:
        """Get .py files found in the directory path provided
        Args:
            dir_path: Root path to search python files

        Returns:
            List with the python files found in the directory path
        """
        paths_found = os.listdir(dir_path)
        return [file.split(".")[0] for file in paths_found if file.endswith(".py")]

    @staticmethod
    def is_internal_package(
        import_stm: str,
        internal_packages: List,
        root_modules: List,
    ) -> bool:
        """
        Validate if the module provided belong to a local module in the project
        Args:
            root_modules: Root modules found base in the base dir defined
            internal_packages: Internal packages of the project
            import_stm: Module to validate

        Returns:
            True if the module is a local module present in the context of the
            parsed file, otherwise false
        """
        # pylint: disable=fixme
        # Todo this validation must be optimized base in the other possibilities to import
        #  an own package in the project
        import_ = import_stm.split(".")[0]
        result_pkg = filter(lambda pkg: pkg.get("pkg") == import_, internal_packages)
        result_modules = filter(lambda module: import_ == module, root_modules)
        return bool(list(result_pkg)) or bool(list(result_modules))

    def clean_internal_imports(
        self,
        imports_from: Dict,
        internal_packages: List,
        root_modules: List,
    ) -> None:
        """
        Filter and exclude import that make reference to a internal package
        Args:
            imports_from: Imports with the schema "from x import y, z" found
            root_modules: Root modules found base in the base dir defined
            internal_packages: Internal packages of the project
        """
        absolute_imports = copy.deepcopy(imports_from.get("absolute_imports", {}))
        for import_stm, _ in absolute_imports.items():
            if self.is_internal_package(import_stm, internal_packages, root_modules):
                imports_from["absolute_imports"].pop(import_stm)
