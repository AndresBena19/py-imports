"""Test integration validators"""
from typing import Dict, List, NoReturn, Optional


def validate_flask_import(  # type: ignore[return]
    imports: Dict, file_path: str
) -> Optional[NoReturn]:
    """
    Validate if the information about the next import are properly parses

    Example:
        import flask, keras

    Args:
        imports: Dict with the data import parse from a file
        file_path: File path of the file parsed
    """
    file_imports = imports.get(file_path)
    assert file_imports, "Any import was found"
    imports_without_from_statement_found: List[Dict] = file_imports.get("imports")
    import_found = imports_without_from_statement_found[0].get("imports")

    assert len(imports_without_from_statement_found) == 1
    assert import_found == ["flask"]
    assert imports_without_from_statement_found[0].get("line") == 1
