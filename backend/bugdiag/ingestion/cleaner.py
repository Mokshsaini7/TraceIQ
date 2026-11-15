"""Data cleaning, normalization, and deduplication hashing for historical defects.
"""

import re
import html
import hashlib
from typing import Dict, Any, Optional

ANSI_ESCAPE_PATTERN = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
MULTIPLE_SPACES_PATTERN = re.compile(r"[ \t]+")
MULTIPLE_NEWLINES_PATTERN = re.compile(r"\n{3,}")

def clean_text(raw_text: Optional[str]) -> str:
    """Cleans raw text by unescaping HTML, stripping ANSI colors, and collapsing excess whitespace."""
    if not raw_text:
        return ""

    text = str(raw_text)
    # Remove ANSI terminal codes
    text = ANSI_ESCAPE_PATTERN.sub("", text)
    # Unescape HTML entities
    text = html.unescape(text)
    # Remove null bytes and carriage returns
    text = text.replace("\x00", "").replace("\r\n", "\n").replace("\r", "\n")
    # Normalize excessive newlines
    text = MULTIPLE_NEWLINES_PATTERN.sub("\n\n", text)
    # Strip leading/trailing whitespaces
    return text.strip()

def normalize_stack_trace(stack_trace: Optional[str]) -> Optional[str]:
    """Normalizes file path slashes and standardizes stack trace indentation."""
    if not stack_trace:
        return None

    cleaned = clean_text(stack_trace)
    # Normalize Windows backslashes in paths to forward slashes for cross-platform indexing
    lines = []
    for line in cleaned.splitlines():
        line = line.strip()
        if line:
            lines.append(line)
    return "\n".join(lines) if lines else None

def compute_content_hash(source_repo: str, original_id: str, title: str, description: str) -> str:
    """Computes a canonical SHA-256 hash for deduplicating defect reports."""
    canonical_str = f"{source_repo.strip().lower()}|{original_id.strip()}|{title.strip().lower()}|{clean_text(description)[:200]}"
    return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()
