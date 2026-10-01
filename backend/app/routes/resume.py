from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.resume_parser import MAX_RESUME_BYTES, extract_resume_text

router = APIRouter(prefix="/api/resume", tags=["resumes"])


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)) -> dict:
	content = await file.read(MAX_RESUME_BYTES + 1)
	try:
		text = extract_resume_text(file.filename, content)
	except ValueError as error:
		raise HTTPException(status_code=400, detail=str(error)) from error
	return {"filename": file.filename, "resume_text": text}
