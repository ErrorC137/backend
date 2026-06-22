"""In-memory document ingestion — no disk persistence."""

from __future__ import annotations

import io
import re
from dataclasses import dataclass, field

from PyPDF2 import PdfReader
from docx import Document


SECTION_PATTERNS = {
    "abstract": r"(?is)(?:^|\n)\s*(?:abstract|summary)\s*[:\-]?\s*(.+?)(?=\n\s*(?:introduction|1[\.\)]|keywords|background|index terms)\b)",
    "introduction": r"(?is)(?:^|\n)\s*(?:1[\.\)]?\s*)?introduction\s*[:\-]?\s*(.+?)(?=\n\s*(?:2[\.\)]|related work|methods?|materials)\b)",
    "methods": r"(?is)(?:^|\n)\s*(?:2[\.\)]?\s*)?(?:methods?|methodology|materials and methods|experimental)\s*[:\-]?\s*(.+?)(?=\n\s*(?:3[\.\)]|results?|findings|discussion)\b)",
    "results": r"(?is)(?:^|\n)\s*(?:3[\.\)]?\s*)?(?:results?|findings)\s*[:\-]?\s*(.+?)(?=\n\s*(?:4[\.\)]|discussion|conclusion|references)\b)",
    "conclusion": r"(?is)(?:^|\n)\s*(?:4[\.\)]?\s*)?(?:conclusions?|discussion)\s*[:\-]?\s*(.+?)(?=\n\s*(?:references|acknowledg|appendix|bibliography)\b|$)",
}


@dataclass
class ParsedDocument:
    raw_text: str
    abstract: str
    methodology: str
    claims_outcomes: str
    document_type: str = "scientific_paper"
    parsing_confidence: float = 0.5
    sections_found: list[str] = field(default_factory=list)


def _strip_metadata(text: str) -> str:
    text = re.sub(r"(?i)(corresponding author|affiliation|university of)[^\n]{0,120}", "", text)
    text = re.sub(r"(?i)(email|@)[^\s]{3,80}", "", text)
    text = re.sub(r"(?i)^\s*arxiv:[^\n]+\n", "", text)
    return text


def _extract_section(text: str, pattern: str) -> str | None:
    match = re.search(pattern, text)
    return match.group(1).strip() if match else None


def _infer_document_type(text: str, filename: str) -> str:
    lower = text[:3000].lower()
    name = filename.lower()
    if "patent" in name or re.search(r"(?i)claim\s+\d+\.", text[:5000]):
        return "patent_draft"
    if "preprint" in lower or "arxiv" in lower or "biorxiv" in lower:
        return "preprint"
    if re.search(r"(?i)(technical report|white paper)", text[:2000]):
        return "technical_report"
    return "scientific_paper"


def _fallback_chunk_extraction(text: str) -> tuple[str, str, str]:
    """Handle papers without standard section headers (common in preprints/exports)."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if len(p.strip()) > 40]
    if not paragraphs:
        chunk = text.strip()
        third = max(len(chunk) // 3, 1)
        return chunk[:third], chunk[third : third * 2], chunk[third * 2 :]

    n = len(paragraphs)
    abstract = paragraphs[0]
    if n >= 4:
        methodology = "\n\n".join(paragraphs[1 : n // 2])
        claims = "\n\n".join(paragraphs[n // 2 :])
    elif n == 3:
        methodology = paragraphs[1]
        claims = paragraphs[2]
    else:
        methodology = paragraphs[1] if n > 1 else paragraphs[0]
        claims = paragraphs[-1]
    return abstract, methodology, claims


def _extract_sections(text: str) -> tuple[str, str, str, list[str], float]:
    found: list[str] = []
    abstract = _extract_section(text, SECTION_PATTERNS["abstract"])
    if abstract:
        found.append("abstract")

    methods = _extract_section(text, SECTION_PATTERNS["methods"])
    if methods:
        found.append("methods")

    results = _extract_section(text, SECTION_PATTERNS["results"])
    conclusion = _extract_section(text, SECTION_PATTERNS["conclusion"])
    claims_parts = [p for p in (results, conclusion) if p]
    claims = "\n\n".join(claims_parts) if claims_parts else None

    if results:
        found.append("results")
    if conclusion:
        found.append("conclusion")

    if abstract and methods and claims:
        confidence = 0.95
    elif abstract and (methods or claims):
        confidence = 0.75
    elif abstract:
        confidence = 0.55
        abstract, methods, claims = _fallback_chunk_extraction(text)
        found.append("fallback_chunking")
    else:
        abstract, methods, claims = _fallback_chunk_extraction(text)
        found = ["fallback_chunking"]
        confidence = 0.45

    return abstract, methods or text[800:3500].strip(), claims or text[-2000:].strip(), found, confidence


def parse_upload(filename: str, content: bytes) -> ParsedDocument:
    name = filename.lower()
    if name.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
        raw = "\n".join(pages)
    elif name.endswith(".docx"):
        doc = Document(io.BytesIO(content))
        raw = "\n".join(p.text for p in doc.paragraphs)
    else:
        raw = content.decode("utf-8", errors="replace")

    raw = _strip_metadata(raw)
    doc_type = _infer_document_type(raw, filename)
    abstract, methodology, claims, sections_found, confidence = _extract_sections(raw)

    return ParsedDocument(
        raw_text=raw,
        abstract=abstract,
        methodology=methodology,
        claims_outcomes=claims,
        document_type=doc_type,
        parsing_confidence=round(confidence, 2),
        sections_found=sections_found,
    )
