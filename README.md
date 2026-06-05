# GradeOps

**AI-powered exam grading system with a TA review dashboard.**

GradeOps automates the grading of handwritten or scanned exam submissions using an LLM pipeline, and surfaces results in a structured review interface for instructors and teaching assistants.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Environment Variables](#environment-variables)
  - [Running with Docker](#running-with-docker)
  - [Running Locally](#running-locally)
- [Grading Pipeline](#grading-pipeline)
- [API Reference](#api-reference)
- [Database Migrations](#database-migrations)
- [OCR Service](#ocr-service)
- [Contributing](#contributing)

---

## Overview

GradeOps is a full-stack web application that lets instructors upload exam PDFs, define rubrics, and trigger an AI grading pipeline. Teaching assistants can then review, approve, or override AI-generated grades through a dedicated queue interface. Final grades can be exported in bulk.

---

## Architecture

```
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│   React Client  │────▶│  FastAPI Backend      │────▶│  Supabase       │
│   (Vite + TW)   │     │  (Python 3.11+)       │     │  (Postgres +    │
│                 │     │                      │     │   Storage)      │
└─────────────────┘     │  ┌────────────────┐  │     └─────────────────┘
                        │  │ LangGraph      │  │
                        │  │ Grading        │  │     ┌─────────────────┐
                        │  │ Pipeline       │──┼────▶│  LLM Provider   │
                        │  └────────────────┘  │     │  OpenAI /       │
                        │                      │     │  Anthropic / xAI│
                        └──────────────────────┘     └─────────────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │  OCR Microservice    │
                        │  (FastAPI, port 8001)│
                        └──────────────────────┘
```

---

## Features

- **Exam management** — upload exam PDFs and organise by course
- **Rubric builder** — define question-level criteria and maximum marks
- **Answer region mapping** — identify which regions of a page correspond to each question
- **AI grading pipeline** — LangGraph graph that preprocesses, grades, scores confidence, justifies, and checks for plagiarism
- **Multi-provider LLM support** — routes between OpenAI (GPT-4o), Anthropic (Claude), and xAI (Grok) with automatic fallback
- **TA review queue** — approve or override AI grades with keyboard shortcuts and inline image preview
- **Plagiarism detection** — semantic similarity check using vector embeddings (pgvector)
- **Grade export** — bulk CSV/spreadsheet export of finalised grades
- **Role-based access control** — Instructor and TA roles with protected routes
- **Dark mode** — full UI dark mode support

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, Vite, Tailwind CSS 4, Zustand, TanStack Query, React Router 7 |
| Backend | FastAPI, SQLAlchemy 2, LangGraph, LangChain |
| LLM | OpenAI GPT-4o · Anthropic Claude · xAI Grok (configurable + fallback) |
| Database | PostgreSQL via Supabase (with pgvector extension) |
| Storage | Supabase Storage (exam PDFs + answer images) |
| Auth | JWT (PyJWT + bcrypt) |
| OCR | Standalone FastAPI microservice (pluggable model) |
| Containerisation | Docker + Docker Compose |

---

## Project Structure

```
gradeOps-new/
├── client/                     # React frontend
│   ├── src/
│   │   ├── api/                # Axios API clients
│   │   ├── components/         # Shared UI components
│   │   │   ├── dashboard/      # Grade review UI (ReviewCard, AnswerImagePane, etc.)
│   │   │   └── ui/             # Primitives (Button, Modal, Sidebar, etc.)
│   │   ├── hooks/              # Custom hooks (useWebSocket, useGradeQueue, etc.)
│   │   ├── pages/              # Route-level pages
│   │   │   ├── Dashboard.jsx
│   │   │   ├── ExamUpload.jsx
│   │   │   ├── GradeExport.jsx
│   │   │   ├── Login.jsx
│   │   │   ├── ReviewQueue.jsx
│   │   │   └── RubricSetup.jsx
│   │   └── store/              # Zustand state (auth, exam, grade)
│   └── package.json
│
├── server/                     # FastAPI backend
│   ├── main.py                 # App entry point, pipeline worker loop
│   ├── app/
│   │   ├── api/routes/         # REST endpoints (auth, exams, grades, etc.)
│   │   ├── core/               # Config, Supabase client, security, deps
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── pipeline/           # LangGraph grading graph
│   │   │   ├── graph.py        # Graph definition
│   │   │   ├── nodes/          # preprocessor, grader, confidence, justifier,
│   │   │   │                   #   plagiarism, output
│   │   │   ├── prompts/        # Grading & justification prompt templates
│   │   │   └── state.py        # GradeState TypedDict
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   └── services/           # Business logic (grade, exam, submission, etc.)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── ocr-service/                # Standalone OCR microservice
│   ├── app.py                  # FastAPI app (POST /infer)
│   ├── inference.py            # OCR model wrapper
│   └── requirements.txt
│
└── supabase/
    ├── migrations/             # Ordered SQL migrations (001–010)
    └── seed.sql
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (recommended)
- A [Supabase](https://supabase.com) project with:
  - PostgreSQL database
  - Storage buckets: `exam-pdfs` and `answer-images`
  - `pgvector` extension enabled (migration `001_pgvector.sql`)

---

### Environment Variables

Create a `.env` file in `server/` based on the following:

```env
# Application
DEBUG=False
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=postgresql+psycopg2://user:password@host:5432/dbname

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret

# LLM (at least one provider required)
LLM_PROVIDER=openai                   # primary provider
LLM_FALLBACK_ORDER=anthropic,openai,xai

OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o

ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-latest

XAI_API_KEY=xai-...
XAI_MODEL=grok-2-latest

# OCR Microservice
OCR_API_URL=http://localhost:8001

# Security
SECRET_KEY=change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Plagiarism
PLAGIARISM_THRESHOLD=0.85
```

---

### Running with Docker

```bash
cd server
docker-compose up --build
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

---

### Running Locally

**Backend**

```bash
cd server
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend**

```bash
cd client
npm install
npm run dev
```

The client will start on `http://localhost:5173`.

**OCR Service**

```bash
cd ocr-service
pip install -r requirements.txt
uvicorn app:app --port 8001 --reload
```

Set `OCR_MOCK_MODE=false` once the real OCR model is wired into `inference.py`.

---

## Grading Pipeline

The AI grading pipeline is built with **LangGraph** and runs as a background worker inside the FastAPI process. The graph executes the following nodes in order:

```
preprocess → grade → confidence ──(needs re-eval?)──▶ grade (loop)
                                  │
                                  └──▶ justify → plagiarism → output
```

| Node | Responsibility |
|------|---------------|
| `preprocessor` | Fetches answer image from storage, calls OCR service |
| `grader` | Sends extracted text + rubric to LLM, returns awarded marks |
| `confidence` | Evaluates LLM confidence; triggers re-evaluation if below threshold |
| `justifier` | Generates a human-readable justification for the awarded marks |
| `plagiarism` | Computes semantic embedding similarity against other submissions |
| `output` | Persists the grade record to the database |

Jobs are polled from a `pipeline_jobs` table every 1.5 seconds.

---

## API Reference

Interactive Swagger docs are available at `/docs` when the server is running.

| Resource | Base Path |
|----------|-----------|
| Auth | `/auth` |
| Exams | `/exams` |
| Rubrics | `/rubrics` |
| Submissions | `/submissions` |
| Answer Regions | `/answer-regions` |
| Grades | `/grades` |
| Pipeline | `/pipeline` |
| Export | `/export` |
| Health | `/health` |

---

## Database Migrations

Migrations are plain SQL files in `supabase/migrations/` and should be run in numbered order against your Supabase project (via the Supabase dashboard SQL editor or the Supabase CLI).

```
001_pgvector.sql            — Enable pgvector extension
002_users.sql               — Users table
003_exams.sql               — Exams table
004_rubrics.sql             — Rubrics table
005_submissions.sql         — Submissions table
006_answer_regions.sql      — Answer regions table
007_grades.sql              — Grades table
008_pipeline_jobs_and_grade_audit.sql
009_fix_users_rls.sql
010_add_password_hash_to_users.sql
```

---

## OCR Service

The OCR microservice is a separate FastAPI app that the backend calls during the preprocessing pipeline node.

**Endpoint:** `POST /infer`

```json
// Request
{
  "image": "<base64-encoded image>",
  "question_id": "Q1"
}

// Response
{
  "extracted_text": "Student's handwritten answer...",
  "confidence": 0.87,
  "question_id": "Q1"
}
```

Plug your own OCR model into `ocr-service/inference.py`. The service runs on port `8001` by default and is health-checked by the main API on startup.

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

Please run `black` and `flake8` on backend changes, and `eslint` on frontend changes before submitting.
