"""Security, sanitization, and input safety utilities for BugDiag.
"""

import re
import os
import unicodedata
from pathlib import Path
from bugdiag.core.config import get_settings

def sanitize_filename(filename: str) -> str:
    """Sanitize uploaded filenames to prevent path traversal and shell injection.
    """
    clean_name = os.path.basename(filename)
    clean_name = unicodedata.normalize("NFKD", clean_name).encode("ascii", "ignore").decode("ascii")
    # Remove any characters other than alphanumerics, underscores, dashes, and periods
    clean_name = re.sub(r"[^\w\.-]", "_", clean_name)
    # Prevent hidden files or leading dots
    clean_name = clean_name.lstrip(".")
    if not clean_name:
        clean_name = "unnamed_attachment"
    return clean_name

def validate_file_safety(filename: str, file_size: int) -> tuple[bool, str]:
    """Validate uploaded file extension and size according to security policies.
    """
    settings = get_settings()

    if file_size > settings.MAX_FILE_SIZE_BYTES:
        return False, f"File size ({file_size} bytes) exceeds maximum limit of {settings.MAX_FILE_SIZE_BYTES} bytes."

    ext = Path(filename).suffix.lower()
    if ext not in settings.allowed_extensions_set:
        return False, f"File extension '{ext}' is not permitted. Allowed: {settings.ALLOWED_EXTENSIONS}"

    return True, "Valid"
