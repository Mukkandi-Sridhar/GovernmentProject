# AP Civic AI Platform

AI-first civic infrastructure platform for Andhra Pradesh student welfare schemes.

## What this repository contains
- `apps/api`: FastAPI backend for crawl, extraction, verification, versioning, retrieval, and chat.
- `apps/web`: Next.js App Router frontend with public assistant and admin dashboard.
- `packages/contracts`: Shared Zod contracts and JSON schemas.
- `infra`: Docker Compose and Cloud Run deployment manifests.
- `docs`: Architecture, API, prompts, and operations runbook.

## Core guarantees
- No fabricated scheme data.
- Responses only from retrieved official content.
- Null-on-missing extraction behavior.
- Immutable version history and audit logs.
- Human approval gate before public retrieval.

## Local setup

### 1. Prerequisites
- Node.js 20+
- Python 3.11+
- Docker (optional)

### 2. Install dependencies
```bash
npm install
cd apps/api
python -m venv .venv
. .venv/Scripts/activate
pip install -e .[dev]
```

### 3. Configure environment
```bash
copy apps/api/.env.example apps/api/.env
copy apps/web/.env.example apps/web/.env.local
```

Set required values in `apps/api/.env`:
- `OPENAI_API_KEY`
- `EMBEDDING_PROVIDER=huggingface` to use free Hugging Face embeddings (`BAAI/bge-m3`)
- Optional: `HUGGINGFACE_API_TOKEN` for higher Hugging Face rate limits
- `ENABLE_AGENT_ORCHESTRATION=true` to enable LangGraph multi-agent intent routing (default is `false`)
- `USE_INMEMORY_DB=false` and Firebase/GCP credentials for production
- `DISABLE_AUTH=false` for production

### 4. Run locally
```bash
# terminal 1
cd apps/api
uvicorn app.main:app --reload --port 8000

# terminal 2
npm run dev --workspace @ap-civic/web
```

Web: `http://localhost:3000`
API docs: `http://localhost:8000/docs`

## Docker
```bash
cd infra
docker compose up --build
```

## Test and quality gates
```bash
cd apps/api
pytest

cd ../web
npm run test
npm run lint
npm run build
```

## Key API endpoints
Public:
- `POST /api/v1/chat/query`
- `GET /api/v1/chat/jobs/{job_id}`
- `GET /api/v1/schemes`
- `GET /api/v1/schemes/{scheme_id}`
- `GET /api/v1/schemes/{scheme_id}/versions`
- `GET /api/v1/schemes/{scheme_id}/versions/{version}/diff`

Admin:
- `POST /api/v1/admin/crawl/run`
- `POST /api/v1/admin/crawl/run-open-source`
- `GET /api/v1/admin/crawl/jobs`
- `POST /api/v1/admin/schemes/{scheme_id}/versions/{version}/approve`
- `POST /api/v1/admin/schemes/{scheme_id}/versions/{version}/flag`
- `POST /api/v1/admin/allowlist/hosts`
- `DELETE /api/v1/admin/allowlist/hosts/{host}`
- `GET /api/v1/admin/logs`
- `GET /api/v1/admin/anomalies`

System:
- `GET /health/live`
- `GET /health/ready`
- `GET /metrics`

