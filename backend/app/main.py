from __future__ import annotations

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .parser import ResumeDocument, extract_text_from_bytes, parse_resume


app = FastAPI(
    title="Resume Parser API",
    description="NLP-inspired resume parsing service for extracting structured candidate data.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/parse")
async def parse_resume_endpoint(
    resume_text: str = Form(default=""),
    resume_file: UploadFile | None = File(default=None),
) -> dict[str, object]:
    extracted_text = resume_text.strip()
    filename = None

    if resume_file:
        file_bytes = await resume_file.read()
        if not file_bytes:
            raise HTTPException(status_code=400, detail="Uploaded resume file is empty.")

        filename = resume_file.filename or "resume.txt"
        extracted_text = extract_text_from_bytes(filename, file_bytes)

    if not extracted_text:
        raise HTTPException(status_code=400, detail="Provide resume text or upload a resume file.")

    return parse_resume(ResumeDocument(text=extracted_text, filename=filename))
