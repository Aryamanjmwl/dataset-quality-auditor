"""I/O helpers for Dataset Quality Auditor."""

from pathlib import Path


def resolve_existing_file(path: str | Path) -> Path:
    """Return a resolved file path after validating that it exists."""
    file_path = Path(path).expanduser().resolve()
    if not file_path.is_file():
        msg = f"Expected an existing file path: {file_path}"
        raise FileNotFoundError(msg)
    return file_path
