from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path
from fastapi.responses import JSONResponse

from app.routes.interview import router as interview_router
from app.routes.resume import router as resume_router
from app.services.llm_service import AIServiceError, missing_api_keys

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

app = FastAPI(title="AI Interview Agent", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(interview_router)
app.include_router(resume_router)


@app.exception_handler(AIServiceError)
async def handle_ai_service_error(_: Request, error: AIServiceError) -> JSONResponse:
    return JSONResponse(status_code=error.status_code, content={"detail": str(error)})


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "app": "AI Interview Agent",
        "ai_configured": not missing_api_keys(),
    }
