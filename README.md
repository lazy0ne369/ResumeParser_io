# ResumeParser_io

A full-stack resume parsing application that transforms unstructured resumes into structured, recruiter-friendly data.

The project combines a FastAPI backend for document/text parsing with a React + Vite frontend for an interactive review workflow.

## Key Features

- Parse resumes from pasted text or uploaded files (`.pdf`, `.docx`, `.txt`).
- Extract structured sections such as summary, education, skills, projects, and experience.
- Detect contact info, links, skill buckets, timelines, and learning signals.
- Modern responsive UI with light/dark theme toggle.
- Download parsed output as JSON.
- Fast local development with frontend proxy to backend API.

## Tech Stack

- Frontend: React 19, Vite, Framer Motion, Axios, Lucide React
- Backend: FastAPI, Uvicorn, PyPDF2, python-docx, python-multipart

## Project Structure

```text
resume_parser/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── parser.py
│   │   └── __init__.py
│   └── requirements.txt
└── frontend/
    ├── src/
    ├── package.json
    └── vite.config.js
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm 9+

## Local Setup

### 1. Backend setup

```bash
cd backend
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS/Linux
# source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend will run at `http://127.0.0.1:8000`.

### 2. Frontend setup

In a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend will run at `http://127.0.0.1:5173`.

## API

### Health check

- `GET /api/health`

Response:

```json
{
  "status": "ok"
}
```

### Parse resume

- `POST /api/parse`
- Form fields:
  - `resume_text` (optional string)
  - `resume_file` (optional file)

At least one of `resume_text` or `resume_file` is required.

Example using text:

```bash
curl -X POST http://127.0.0.1:8000/api/parse \
  -F "resume_text=John Doe\nSoftware Engineer\nSkills: Python, React"
```

Example using file:

```bash
curl -X POST http://127.0.0.1:8000/api/parse \
  -F "resume_file=@./sample_resume.pdf"
```

## Build Frontend

```bash
cd frontend
npm run build
```

Build output is generated in `frontend/dist`.

## Troubleshooting

- If you see a blank page, check browser console and ensure frontend dependencies are installed.
- Ensure backend is running on port `8000` when using frontend dev server.
- If file upload parsing fails, verify PDF/DOCX is readable and not password protected.

## Roadmap Ideas

- Add authentication and user workspaces.
- Add model-assisted ranking/scoring for job-role matching.
- Export parsed output to CSV and ATS-friendly schema.
- Add unit/integration tests and CI pipeline.

## License

This project is open-source and available under the MIT License.
