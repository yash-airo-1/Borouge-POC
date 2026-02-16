import fitz
import io
from typing import Optional


def extract_text_from_pdf(file_content: bytes) -> str:
    """
    Extract text from a PDF file.

    Args:
        file_content: Raw bytes of the PDF file

    Returns:
        Extracted text as string
    """
    try:
        pdf_document = fitz.open(stream=file_content, filetype="pdf")
        text = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            text += page.get_text()
        pdf_document.close()
        return text
    except Exception as e:
        raise ValueError(f"Error extracting text from PDF: {str(e)}")


def extract_text_from_file(file_content: bytes, file_type: str) -> str:
    """
    Extract text from uploaded file (PDF, DOCX, or TXT).

    Args:
        file_content: Raw bytes of the file
        file_type: File extension (pdf, docx, txt)

    Returns:
        Extracted text as string
    """
    file_type = file_type.lower()

    if file_type == "pdf":
        return extract_text_from_pdf(file_content)
    elif file_type == "txt":
        return file_content.decode("utf-8", errors="ignore")
    elif file_type == "docx":
        # Basic DOCX support - try to extract text
        try:
            import docx
            doc = docx.Document(io.BytesIO(file_content))
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except:
            # Fallback: return as text
            return file_content.decode("utf-8", errors="ignore")
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
