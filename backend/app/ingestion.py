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
        raw = ""
        extraction_method = ""
        
        try:
            # Method 1: Try PyMuPDF (fitz) - most robust
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(stream=content, filetype="pdf")
                pages_text = []
                for page in doc:
                    try:
                        text = page.get_text()
                        if text and len(text.strip()) > 10:
                            pages_text.append(text)
                    except Exception:
                        continue
                
                if pages_text:
                    raw = "\n".join(pages_text)
                    extraction_method = "PyMuPDF"
                    doc.close()
                else:
                    raise ImportError("PyMuPDF extraction returned no text")
            except ImportError:
                extraction_method = "PyMuPDF not available"
                pass
            
            # Method 2: Try pdfplumber
            if not raw or len(raw.strip()) < 50:
                try:
                    import pdfplumber
                    with pdfplumber.open(io.BytesIO(content)) as pdf:
                        pages = []
                        for page in pdf.pages:
                            try:
                                text = page.extract_text()
                                if text and len(text.strip()) > 10:
                                    cleaned = re.sub(r'[^\x20-\x7E\n\r\t]', '', text)
                                    if len(cleaned.strip()) > 10:
                                        pages.append(cleaned)
                            except Exception:
                                continue
                        
                        if pages:
                            raw = "\n".join(pages)
                            extraction_method = "pdfplumber"
                        else:
                            raise ImportError("pdfplumber extraction failed")
                except ImportError:
                    extraction_method = "pdfplumber not available"
                    pass
            
            # Method 3: Try PyPDF2 with enhanced cleaning
            if not raw or len(raw.strip()) < 50:
                try:
                    reader = PdfReader(io.BytesIO(content))
                    pages = []
                    for page in reader.pages:
                        try:
                            text = page.extract_text()
                            if text and len(text.strip()) > 10:
                                # Aggressive cleaning
                                cleaned = re.sub(r'[^\x20-\x7E\n\r\t]', '', text)
                                # Remove PDF structure artifacts
                                cleaned = re.sub(r'\s*\d+\s*\.\s*\d+\s*', '', cleaned)
                                cleaned = re.sub(r'\s*endobj\s*', '', cleaned)
                                cleaned = re.sub(r'\s*stream\s*', '', cleaned)
                                cleaned = re.sub(r'\s*endstream\s*', '', cleaned)
                                cleaned = re.sub(r'\s*xref\s*', '', cleaned)
                                cleaned = re.sub(r'\s*startxref\s*', '', cleaned)
                                cleaned = re.sub(r'\s*<<\s*/\s*\w+\s*/\s*\w+\s*>>\s*', '', cleaned)
                                cleaned = re.sub(r'\s*/Type\s*/\w+\s*', '', cleaned)
                                cleaned = re.sub(r'\s/Subtype\s*/\w+\s*', '', cleaned)
                                cleaned = re.sub(r'\s/Rect\s*\[.*?\]\s*', '', cleaned)
                                if len(cleaned.strip()) > 10:
                                    pages.append(cleaned)
                        except Exception:
                            continue
                    
                    if pages:
                        raw = "\n".join(pages)
                        extraction_method = "PyPDF2"
                except Exception as e:
                    extraction_method = f"PyPDF2 failed: {str(e)}"
            
            # Method 4: OCR fallback for image-based PDFs
            if not raw or len(raw.strip()) < 50:
                try:
                    import pytesseract
                    from PIL import Image
                    import io
                    
                    # Try PyMuPDF to convert pages to images for OCR
                    try:
                        import fitz
                        doc = fitz.open(stream=content, filetype="pdf")
                        pages_text = []
                        for page in doc:
                            try:
                                # Convert page to image
                                pix = page.get_pixmap()
                                img_data = pix.tobytes("png")
                                image = Image.open(io.BytesIO(img_data))
                                
                                # OCR the image
                                text = pytesseract.image_to_string(image)
                                if text and len(text.strip()) > 10:
                                    pages_text.append(text)
                            except Exception:
                                continue
                        
                        if pages_text:
                            raw = "\n".join(pages_text)
                            extraction_method = "OCR"
                        doc.close()
                    except Exception as e:
                        extraction_method = f"OCR failed: {str(e)}"
                except ImportError:
                    extraction_method = "OCR not available (requires pytesseract and Pillow)"
                    pass
            
            # Method 5: Last resort - decode with extensive cleaning
            if not raw or len(raw.strip()) < 50:
                try:
                    raw = content.decode('utf-8', errors='ignore')
                    # Comprehensive PDF artifact removal - more aggressive
                    raw = re.sub(r'[^\x20-\x7E\n\r\t]', '', raw)
                    # Remove all PDF structure keywords
                    pdf_keywords = ['endobj', 'stream', 'endstream', 'xref', 'startxref', 'obj', 'R']
                    for keyword in pdf_keywords:
                        raw = re.sub(rf'\b{keyword}\b', '', raw, flags=re.IGNORECASE)
                    # Remove PDF dictionary structures
                    raw = re.sub(r'<<.*?>>', '', raw, flags=re.DOTALL)
                    # Remove PDF array structures
                    raw = re.sub(r'\[.*?\]', '', raw, flags=re.DOTALL)
                    # Remove PDF name objects
                    raw = re.sub(r'/\w+', '', raw)
                    # Remove PDF numeric references
                    raw = re.sub(r'\b\d+\s+\d+\s+R\b', '', raw)
                    raw = re.sub(r'\b\d+\s+obj\b', '', raw)
                    # Remove common PDF artifacts
                    raw = re.sub(r'/Type|/Subtype|/Rect|/Action|/Dest|/Parent|/First|/Last|/Count|/Title|/Prev|/Next|/StructParent|/F|/BS|/S|/W|/CA|/ca|/LW|/Filter|/Length|/BitsPerComponent|/ColorSpace|/Width|/Height|/ICCBased|/Separation', '', raw, flags=re.IGNORECASE)
                    # Remove hex-encoded content
                    raw = re.sub(r'[0-9A-Fa-f]{20,}', '', raw)
                    # Remove base64-like content
                    raw = re.sub(r'[A-Za-z0-9+/]{50,}={0,2}', '', raw)
                    # Remove repeated special characters
                    raw = re.sub(r'[<>{}\\]+', '', raw)
                    # Clean up whitespace
                    raw = re.sub(r'\s+', ' ', raw)
                    extraction_method = "raw_decode"
                except Exception as e:
                    raw = f"PDF parsing error: {str(e)}. Method used: {extraction_method}"
            
            # Final validation
            if not raw or len(raw.strip()) < 50:
                raw = f"Document content could not be properly extracted. The PDF may be image-based or corrupted. Extraction method: {extraction_method}. Please try a different file format."
            
        except Exception as e:
            raw = f"PDF parsing error: {str(e)}"
            
    elif name.endswith(".docx"):
        doc = Document(io.BytesIO(content))
        raw = "\n".join(p.text for p in doc.paragraphs)
    else:
        raw = content.decode("utf-8", errors="replace")

    # Clean the extracted text - aggressive PDF artifact removal
    raw = _strip_metadata(raw)
    
    # Remove all non-ASCII characters first
    raw = re.sub(r'[^\x20-\x7E\n\r\t]', '', raw)
    
    # Aggressive PDF artifact removal
    raw = re.sub(r'/\w+', '', raw)  # Remove all PDF name objects
    raw = re.sub(r'\b\d+\s+\d+\s+R\b', '', raw)  # Remove PDF references
    raw = re.sub(r'\b\d+\s+obj\b', '', raw)  # Remove object references
    raw = re.sub(r'<<.*?>>', '', raw, flags=re.DOTALL)  # Remove PDF dictionaries
    raw = re.sub(r'\[.*?\]', '', raw, flags=re.DOTALL)  # Remove PDF arrays
    raw = re.sub(r'\bendobj\b|\bstream\b|\bendstream\b|\bxref\b|\bstartxref\b', '', raw, flags=re.IGNORECASE)
    raw = re.sub(r'/Type|/Subtype|/Rect|/Action|/Dest|/Parent|/First|/Last|/Count|/Title|/Prev|/Next|/StructParent|/F|/BS|/S|/W|/CA|/ca|/LW|/Filter|/Length|/BitsPerComponent|/ColorSpace|/Width|/Height|/ICCBased|/Separation', '', raw, flags=re.IGNORECASE)
    raw = re.sub(r'/Pg\s+\d+\s+\d+\s+R', '', raw)  # Remove page references
    raw = re.sub(r'/K\s*\[.*?\]', '', raw, flags=re.DOTALL)  # Remove PDF arrays
    raw = re.sub(r'/H\d+', '', raw)  # Remove heading references
    raw = re.sub(r'/P\s+\d+\s+\d+\s+R', '', raw)  # Remove paragraph references
    raw = re.sub(r'/T\s*\([^)]*\)', '', raw)  # Remove text references
    raw = re.sub(r'/E\s*\([^)]*\)', '', raw)  # Remove element references
    raw = re.sub(r'/A\s*\[.*?\]', '', raw, flags=re.DOTALL)  # Remove action arrays
    raw = re.sub(r'[0-9A-Fa-f]{20,}', '', raw)  # Remove hex-encoded content
    raw = re.sub(r'[A-Za-z0-9+/]{50,}={0,2}', '', raw)  # Remove base64-like content
    raw = re.sub(r'[<>{}\\]+', '', raw)  # Remove special characters
    raw = re.sub(r'\s+', ' ', raw)  # Clean up whitespace
    
    # Ensure we have meaningful content
    if len(raw.strip()) < 50:
        raw = "Document content could not be properly extracted. Please check the file format and try again."
    
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
