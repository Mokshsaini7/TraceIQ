"""Safe static content reader for uploaded attachments.
Strictly non-executing; reads content as text or extracts metadata safely.
"""

from pathlib import Path
from typing import Optional
from bugdiag.core.logging import get_logger

logger = get_logger("file_parser")

def read_file_safely(file_path: str, max_chars: int = 50000) -> Optional[str]:
    """Reads an uploaded file as pure text, respecting length limits.
    Never executes or evaluates file contents.
    """
    path = Path(file_path)
    if not path.is_file():
        logger.warning(f"File not found: {file_path}")
        return None

    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(max_chars)
            return content
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return None
