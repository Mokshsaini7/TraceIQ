"""File upload handler and security sanitizer.
Ensures zero code execution and enforces size and extension policies.
"""

import hashlib
import os
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile, HTTPException, status
from bugdiag.core.config import get_settings
from bugdiag.core.security import sanitize_filename, validate_file_safety
from bugdiag.core.logging import get_logger

logger = get_logger("file_processing")

class FileProcessingService:
    def __init__(self):
        self.settings = get_settings()
        self.upload_dir = Path(self.settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_upload_file(self, upload_file: UploadFile) -> Tuple[str, str, int, str]:
        """Validates, hashes, and safely persists an uploaded file.
        Returns (stored_filename, file_path, file_size, sha256_hash).
        """
        original_name = upload_file.filename or "unknown_file.txt"
        sanitized = sanitize_filename(original_name)

        # Read content safely in chunks
        hasher = hashlib.sha256()
        total_size = 0
        chunks = []

        while chunk := await upload_file.read(1024 * 64):
            total_size += len(chunk)
            if total_size > self.settings.MAX_FILE_SIZE_BYTES:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File exceeds maximum allowed size of {self.settings.MAX_FILE_SIZE_BYTES} bytes."
                )
            hasher.update(chunk)
            chunks.append(chunk)

        is_safe, reason = validate_file_safety(sanitized, total_size)
        if not is_safe:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=reason
            )

        file_hash = hasher.hexdigest()
        ext = Path(sanitized).suffix.lower()
        stored_filename = f"{file_hash[:16]}_{sanitized}"
        target_path = self.upload_dir / stored_filename

        with open(target_path, "wb") as f:
            for c in chunks:
                f.write(c)

        logger.info(f"Safely persisted uploaded file: {sanitized} -> {target_path} ({total_size} bytes)")
        return sanitized, str(target_path), total_size, file_hash
