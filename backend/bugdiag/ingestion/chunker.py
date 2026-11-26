"""Configurable defect text chunking with stack-trace preservation.
"""

from typing import List, Dict, Any

class DefectChunker:
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 64):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_defect(
        self,
        title: str,
        description: str,
        stack_trace: str | None = None,
        resolution: str | None = None
    ) -> List[Dict[str, Any]]:
        """Segments a defect into semantically coherent chunks."""
        chunks = []
        chunk_idx = 0

        # Chunk 1: Summary (Title + initial description)
        summary_text = f"Title: {title}\nDescription: {description[:self.chunk_size]}"
        chunks.append({
            "chunk_index": chunk_idx,
            "chunk_type": "summary",
            "content": summary_text.strip(),
            "token_count": len(summary_text.split())
        })
        chunk_idx += 1

        # Chunk 2: Overlapping body if description exceeds chunk size
        if len(description) > self.chunk_size:
            start = self.chunk_size - self.chunk_overlap
            while start < len(description):
                end = min(start + self.chunk_size, len(description))
                body_slice = description[start:end]
                if len(body_slice.strip()) > 30:
                    chunks.append({
                        "chunk_index": chunk_idx,
                        "chunk_type": "description_segment",
                        "content": f"Context: {title}\nDetails: {body_slice.strip()}",
                        "token_count": len(body_slice.split())
                    })
                    chunk_idx += 1
                start += (self.chunk_size - self.chunk_overlap)

        # Chunk 3: Stack Trace preservation
        if stack_trace and stack_trace.strip():
            # Keep stack trace intact as a dedicated unit
            chunks.append({
                "chunk_index": chunk_idx,
                "chunk_type": "stack_trace",
                "content": f"Bug: {title}\nStack Trace:\n{stack_trace.strip()}",
                "token_count": len(stack_trace.split())
            })
            chunk_idx += 1

        # Chunk 4: Historical Resolution and remediation evidence
        if resolution and resolution.strip():
            chunks.append({
                "chunk_index": chunk_idx,
                "chunk_type": "resolution",
                "content": f"Defect: {title}\nHistorical Fix/Resolution: {resolution.strip()}",
                "token_count": len(resolution.split())
            })
            chunk_idx += 1

        return chunks
