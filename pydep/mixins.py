"""Mixins"""
import os
from typing import List


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
            True ig the module is a local module present in the context of the
            parsed file, otherwise false
        """
        # pylint: disable=fixme
        # Todo this validation must be optimized base in the other possibilities to import
        #  a own package in the project
        import_ = import_stm.split(".")[0]
        result_pkg = filter(lambda pkg: pkg.get("pkg") == import_, internal_packages)
        result_modules = filter(lambda module: import_ == module, root_modules)
        return bool(list(result_pkg)) or bool(list(result_modules))
