"""Small, defensive document parser. Uploaded content is never written to disk."""
from __future__ import annotations

from io import BytesIO


class DocumentParseError(ValueError):
    """Raised when an uploaded document cannot provide useful text."""


def extract_text(filename: str, content: bytes) -> str:
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if suffix == "txt":
        text = content.decode("utf-8", errors="replace")
    elif suffix == "pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise DocumentParseError("PDF support needs pypdf. Run: pip install -r requirements.txt") from exc
        try:
            text = "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(content)).pages)
        except Exception as exc:
            raise DocumentParseError("We could not read that PDF. Try exporting it as a text-based PDF or TXT.") from exc
    elif suffix == "docx":
        try:
            from docx import Document
        except ImportError as exc:
            raise DocumentParseError("DOCX support needs python-docx. Run: pip install -r requirements.txt") from exc
        try:
            text = "\n".join(paragraph.text for paragraph in Document(BytesIO(content)).paragraphs)
        except Exception as exc:
            raise DocumentParseError("We could not read that DOCX file. Try saving it again or use TXT.") from exc
    else:
        raise DocumentParseError("Use a PDF, DOCX, or TXT resume.")

    text = " ".join(text.split())
    if len(text) < 40:
        raise DocumentParseError("There was not enough readable text. Scanned PDFs need OCR before analysis.")
    return text
