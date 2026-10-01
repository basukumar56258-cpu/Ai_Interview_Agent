from io import BytesIO
from pathlib import Path

from docx import Document
from pypdf import PdfReader

MAX_RESUME_BYTES = 5 * 1024 * 1024
SUPPORTED_RESUME_TYPES = {".pdf", ".docx", ".txt"}


def extract_resume_text(filename: str | None, content: bytes) -> str:
	extension = Path(filename or "").suffix.lower()
	if extension not in SUPPORTED_RESUME_TYPES:
		raise ValueError("Unsupported file type. Upload a PDF, DOCX, or TXT resume.")
	if not content:
		raise ValueError("The uploaded resume is empty.")
	if len(content) > MAX_RESUME_BYTES:
		raise ValueError("Resume files must be 5 MB or smaller.")

	try:
		if extension == ".txt":
			text = content.decode("utf-8-sig")
		elif extension == ".pdf":
			text = "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(content)).pages)
		else:
			document = Document(BytesIO(content))
			text = "\n".join(paragraph.text for paragraph in document.paragraphs)
	except Exception as error:
		raise ValueError("This resume could not be read. Check the file and try again.") from error

	text = text.strip()
	if not text:
		raise ValueError("No readable text was found in the resume.")
	return text[:30000]
