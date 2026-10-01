# AI Interview Agent

AI Interview Agent is a full-stack interview practice application. It uses a coordinated set of AI agents to analyze a candidate profile, plan a role-specific interview, evaluate answers, ask relevant follow-ups, and prepare a final report.

## Features

- Create interviews from a job description, interview type, and difficulty.
- Optionally upload a PDF, DOCX, or TXT resume for profile analysis.
- Use Groq for interview planning, question generation, answer evaluation, follow-ups, and reporting.
- Use Tavily to research current role and technology context.
- Validate empty input and unsupported or unreadable resume files.
- Display safe, actionable errors for missing keys, provider failures, and backend connectivity issues.
- Keep API keys on the backend; the frontend never receives them.

## Agentic Architecture

The FastAPI backend coordinates six focused agents. Groq and Tavily credentials are loaded from `backend/.env` and are never sent to the browser.

## Agent Workflow

```text
Profile Analyzer Agent
				-> Interview Planner Agent
				-> Interviewer Agent
				-> Answer Evaluator Agent
				-> Follow-up Agent
				-> Final Report Agent
```

The Profile Analyzer compares the resume and job description, with role research from Tavily. The Interview Planner creates the requested question plan. The Interviewer asks one question at a time. After each answer, the Answer Evaluator scores the response and the Follow-up Agent decides whether clarification is useful. The Final Report Agent summarizes completed evaluations.

## Tech Stack

- Frontend: React, JavaScript, Vite, Lucide React
- Backend: Python, FastAPI, Uvicorn, Pydantic
- AI: Groq API
- Web research: Tavily API
- Resume parsing: pypdf, python-docx

## Project Structure

```text
backend/
	app/
		agents/       Profile, planning, interview, evaluation, follow-up, and report agents
		models/       Request schemas and validation
		routes/       Interview and resume API routes
		services/     Groq, Tavily, and resume parsing services
	.env.example
	requirements.txt
frontend/
	src/            React application and styles
	package.json
	vite.config.js
```

## Installation

Prerequisites: Python 3.10 or later, Node.js 20.19+ or 22.12+, and npm.

From the repository root, create the backend environment and install its dependencies:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
cd ..
```

Install frontend dependencies:

```powershell
cd frontend
npm install
cd ..
```

## Environment Setup

Create `backend/.env` from the example:

```powershell
Copy-Item backend/.env.example backend/.env
```

Then edit `backend/.env` locally:

```dotenv
GROQ_API_KEY=
TAVILY_API_KEY=
GROQ_MODEL=llama-3.3-70b-versatile
```

Add your own Groq and Tavily API keys to the blank values. Do not put keys in frontend files or commit `backend/.env`. The app and health endpoint remain available without keys; interview creation responds with a configuration message until both keys are configured.

## Backend Setup

From `backend/`:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

The API listens on `http://127.0.0.1:8000` by default. If the port is unavailable, choose another port with `--port 8001` and set `VITE_BACKEND_URL=http://127.0.0.1:8001` in the frontend environment.

## Frontend Setup

From `frontend/`:

```powershell
npm run dev
```

Vite prints the actual local URL. The frontend proxies `/api` and `/health` to `VITE_BACKEND_URL`, defaulting to `http://127.0.0.1:8000`.

## API Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Backend status and whether AI keys are configured |
| `POST` | `/api/resume/upload` | Extract text from a PDF, DOCX, or TXT resume |
| `POST` | `/api/interview/create` | Research the role, analyze the profile, and start an interview |
| `GET` | `/api/interview/history` | List in-memory interview sessions |
| `GET` | `/api/interview/{interview_id}` | Get an interview's status and current question |
| `POST` | `/api/interview/{interview_id}/answer` | Evaluate an answer and return a follow-up or next question |
| `POST` | `/api/interview/{interview_id}/finish` | Finish an interview and generate its report |
| `GET` | `/api/interview/{interview_id}/report` | Retrieve a completed report |

Interactive API documentation is available at `/docs` while the backend is running.

## How to Run

1. Configure `backend/.env` with both API keys.
2. Start FastAPI in one terminal from `backend/`.
3. Start Vite in another terminal from `frontend/`.
4. Open the URL printed by Vite and create an interview.

To check the backend, open `http://127.0.0.1:8000/health` and `http://127.0.0.1:8000/docs`.

## Screenshots

Add application screenshots here.

## Future Improvements

- Persist interview sessions and reports in a database.
- Add user accounts, exportable reports, and interview history views.
- Add automated tests for provider errors, parsing edge cases, and the complete interview lifecycle.
- Add deployment configuration and production observability.

## GitHub Setup

The repository excludes local environments, build output, and environment files. Only `backend/.env.example` should contain environment-variable names, with blank secret values.

```powershell
git add .
git status
git commit -m "Initial AI Interview Agent project"
git branch -M main
git remote add origin https://github.com/basukumar56258-cpu/Ai_Interview_Agent.git
git push -u origin main
```

Never push API keys, `backend/.env`, tokens, or credentials.

## Author

AI Interview Agent contributors
