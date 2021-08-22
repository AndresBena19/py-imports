"""
Custom exceptions for pydep
"""


class RequiredBaseDirError(Exception):
    """
    Exception to handle when is missing the base dir
    """


class WrongFileExtension(Exception):
    """
    Exception to handle when the file provided is not the extension expected
    """
