"""Read resumes / JDs from .txt, .md, .pdf (pypdf) or .docx (python-docx)."""
from __future__ import annotations

from pathlib import Path


def read_text(path: str | Path) -> str:
    p = Path(path)
    suf = p.suffix.lower()
    if suf == ".pdf":
        from pypdf import PdfReader
        return "\n".join(page.extract_text() or "" for page in PdfReader(str(p)).pages)
    if suf == ".docx":
        import docx
        return "\n".join(par.text for par in docx.Document(str(p)).paragraphs)
    return p.read_text(encoding="utf-8", errors="replace")
