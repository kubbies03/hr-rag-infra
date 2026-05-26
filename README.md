# Android HR Chatbot — RAG System

Backend server for an Android HR application. Handles employee status queries and internal policy questions using a hybrid RAG pipeline, serving JSON responses to the Android client via API.

## Overview

- Employee status questions are answered from live HR data.
- Policy and procedure questions are answered from ingested internal documents.
- Out-of-scope questions are politely declined.

The Android app authenticates users via Firebase Auth and sends requests to this server with a Bearer token. The server uses a three-stage intent classifier, vector retrieval, optional reranking, and Gemini-based answer generation.

## Architecture

```mermaid
flowchart TD
    A[Android App / Browser / Swagger] --> B[Nginx Reverse Proxy]
    B --> C[FastAPI HR RAG Backend]
    C --> D[SQLite Database]
    C --> E[ChromaDB Vector Store]
    C --> F[Gemini API]
```

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI, Uvicorn |
| LLM | Google Gemini 2.5 Flash |
| Embeddings | Gemini Embedding API |
| Reranker | Optional Gemini reranker |
| Vector store | ChromaDB |
| Database | SQLite, SQLAlchemy |
| Authentication | Firebase Auth, demo API key |
| Notifications | Firebase Cloud Messaging |

## Features

- Hybrid intent classification with embedding k-NN, regex, and LLM fallback
- Reranked RAG for policy questions
- Role-based document access filtering
- SQLite fallback for local development
- Conversation history persistence
- Request logging with latency tracking

## Requirements

- Python 3.11+
- Google Gemini API key
- Firebase service account, optional for production auth and Firestore
- Docker + Docker Compose for Linux-style deployment

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `GOOGLE_API_KEY` | Gemini API key | required |
| `GEMINI_EMBEDDING_MODEL` | Gemini embedding model | `models/gemini-embedding-001` |
| `GEMINI_EMBEDDING_BATCH_SIZE` | Batch size for document embedding requests | `100` |
| `GEMINI_EMBEDDING_TIMEOUT` | Timeout for Gemini embedding calls, seconds | `30` |
| `RERANKER_PROVIDER` | Reranker backend | `gemini` |
| `USE_RERANKER` | Enable reranking | `false` |
| `RERANKER_TIMEOUT` | Timeout for Gemini reranking calls, seconds | `20` |
| `RERANKER_MAX_DOC_CHARS` | Max chars per candidate chunk sent to reranker | `1200` |
| `RERANKER_MIN_SCORE` | Minimum reranker score | `0.3` |
| `DATABASE_URL` | SQLite connection string | `sqlite:///data/sqlite/hr.db` |
| `CHROMA_PERSIST_DIR` | ChromaDB storage directory | `data/chroma` |
| `DOCS_DIR` | Source documents directory | `data/docs` |
| `FIREBASE_PROJECT_ID` | Firebase project ID | required for production |
| `FIREBASE_CREDENTIALS_PATH` | Path to service account JSON | `firebase-service-account.json` |

## Authentication

### Demo mode

Pass one of the demo keys in the `X-API-Key` header.

| Key | Role |
|---|---|
| `demo_employee_001` | employee |
| `demo_hr_001` | hr |
| `demo_manager_001` | manager |
| `demo_admin_001` | admin |

### Production mode

The Android app obtains a Firebase ID token after login and attaches it to every request:

```http
Authorization: Bearer <firebase_id_token>
```

## API Reference

### Chat

```http
POST /api/chat
X-API-Key: demo_employee_001
Content-Type: application/json

{
  "message": "What is the annual leave policy?",
  "session_id": "sess_001"
}
```

### Other endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/health` | No | Service health check |
| `POST` | `/api/chat` | Yes | Main chat endpoint |
| `POST` | `/api/documents/ingest` | admin | Upload and index a document |
| `POST` | `/api/documents/ingest-all` | admin | Ingest every file in `data/docs/` |
| `GET` | `/api/documents/stats` | Yes | Vector store statistics |
| `GET` | `/api/employees` | hr / manager / admin | List employees |
| `GET` | `/api/employees/on-leave` | hr / manager / admin | Employees currently on leave |
| `GET` | `/api/logs` | admin | Query history and latency log |
| `POST` | `/api/notify` | hr / admin | Send push notification via FCM |

Legacy aliases `/api/docs/ingest`, `/api/docs/ingest-all`, and `/api/docs/stats` are also supported for backward compatibility.

## Deployment Architecture

```text
Client / Browser / Android App
            |
            v
      Nginx Reverse Proxy
            |
            v
       FastAPI RAG Backend
            |
            v
  SQLite + ChromaDB + Docs Volumes
            |
            v
         Gemini API
```

## Docker Deployment

This repo now includes the minimum deploy package described in `deploy.md`:

- `Dockerfile`
- `docker-compose.yml`
- `nginx/nginx.conf`
- `scripts/backup.sh`
- `scripts/restore.sh`

### 1. Prepare environment

Create a `.env` file in the project root before starting containers.

```bash
cp .env.example .env
```

Then fill in at least:

```text
GOOGLE_API_KEY=...
FIREBASE_PROJECT_ID=...
FIREBASE_CREDENTIALS_PATH=firebase-service-account.json
```

If you do not use Firebase in deployment yet, keep the API key and document volumes ready for demo mode.

### 2. Build and start

```bash
docker compose up -d --build
docker compose ps
```

### 3. Test health

```bash
curl http://localhost/health
curl http://localhost/docs
```

Nginx listens on port `80` and proxies traffic to the FastAPI container on port `8000`.

### 3a. Ingest documents after first deploy

Copy your `.pdf`, `.docx`, or `.txt` files into `data/docs/`, then ingest them:

```bash
docker compose exec rag-api python -c "from app.services.ingest_service import ingest_directory; import json; print(json.dumps(ingest_directory(), ensure_ascii=False, indent=2))"
curl http://localhost/health
```

For a public API test through Nginx:

```bash
curl -X POST "http://localhost/api/chat" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo_employee_001" \
  -d '{"message":"What is the annual leave policy?","session_id":"deploy-test-001"}'
```

### 4. Persistent storage

The deployment mounts the following persistent volumes:

- `./data/sqlite:/app/data/sqlite`
- `./data/chroma:/app/data/chroma`
- `./data/docs:/app/data/docs`

This keeps employee data, vector embeddings, and source documents after container restarts.

The GitHub infra repo does not ship runtime `data/` contents. The container image creates empty `data/sqlite`, `data/chroma`, and `data/docs` directories automatically, and Docker bind mounts will populate them on the host at runtime.

### 5. Backup and restore

Create a backup:

```bash
./scripts/backup.sh
```

On Windows PowerShell:

```powershell
.\scripts\backup.ps1
```

Restore from an archive:

```bash
./scripts/restore.sh backups/hr-rag-backup-YYYY-MM-DD-HHMM.tar.gz
```

On Windows PowerShell:

```powershell
.\scripts\restore.ps1 .\backups\hr-rag-backup-YYYY-MM-DD-HHMM.tar.gz
```

### 6. Monitoring

The Compose stack also includes:

- `prometheus` on `http://localhost:9090`
- `grafana` on `http://localhost:3000`
- `node-exporter` in the Ubuntu monitoring override
- `cadvisor` in the Ubuntu monitoring override

Grafana is preconfigured with a Prometheus datasource.

Default Grafana credentials:

```text
username: admin
password: admin
```

Prometheus scrapes:

- `rag-api:8000/metrics`
- `prometheus:9090`

The default config stays Windows-safe and demo-friendly.

On Windows or Docker Desktop, run the default stack:

```bash
docker compose up -d --build
```

On Ubuntu, run the full monitoring target:

```bash
docker compose -f docker-compose.yml -f docker-compose.ubuntu-monitoring.yml up -d --build
```

Or use the helper script:

```bash
./scripts/deploy_ubuntu.sh
```

The Ubuntu monitoring override adds:

- `node-exporter:9100`
- `cadvisor:8080`
- `monitoring/prometheus.linux.yml`

That Linux Prometheus config scrapes:

- `rag-api:8000/metrics`
- `prometheus:9090`
- `node-exporter:9100`
- `cadvisor:8080`

Grafana also provisions the `HR RAG Overview` dashboard automatically from `monitoring/grafana/dashboards/hr-rag-overview.json`.

To generate API traffic for the dashboard during a demo:

```bash
./scripts/seed_demo_traffic.sh
```

### 7. Telemetry

Chroma telemetry is disabled in both configuration and client initialization:

```text
ANONYMIZED_TELEMETRY=False
```

The client is also wired to a local no-op telemetry implementation so startup does not emit Chroma telemetry noise during demos or deploy verification.

This keeps deployment logs cleaner and avoids unnecessary telemetry noise in demos.

## Extending Intent Classification

Edit `app/data/intent_examples.json` and restart the server to add new phrasings or new intent groups.

## Gemini Embedding Migration

This copy of the project uses Gemini embeddings instead of a local HuggingFace embedding model.

- Linux deploy no longer needs a separate local embedding model for retrieval.
- Reranking is disabled by default so Linux deploy only needs FastAPI + ChromaDB + Gemini API access.
- If you want higher retrieval precision later, enable `USE_RERANKER=true` to use the Gemini reranker.
- Existing Chroma vectors generated by the old embedding model are not compatible with Gemini query vectors.
- Re-ingest the documents in `data/docs/` before testing retrieval on this copy.

## Project Structure

```text
hr-rag-infra/
├── app/
│   ├── api/
│   ├── core/
│   ├── data/
│   ├── db/
│   ├── prompts/
│   ├── services/
│   └── main.py
├── assets/
│   └── screenshots/
├── data/
│   ├── docs/
│   ├── chroma/
│   └── sqlite/
├── monitoring/
├── nginx/
├── scripts/
├── .env.example
├── docker-compose.yml
├── docker-compose.ubuntu-monitoring.yml
├── Dockerfile
├── README.md
└── requirements.txt
```

## Troubleshooting

### `502 Bad Gateway` from Nginx

If `rag-api` was recreated and Nginx still cached the old upstream IP, restart Nginx:

```bash
docker compose restart nginx
```

### `chromadb: ok (0 chunks)` in `/health`

The service is running, but no documents were indexed yet. Copy files into `data/docs/` and run the ingest command in section `3a`.

### Grafana shows `No data`

Verify the Ubuntu monitoring stack is running:

```bash
docker compose -f docker-compose.yml -f docker-compose.ubuntu-monitoring.yml ps
curl http://localhost:9090/api/v1/query?query=up
```

If Prometheus has data, restart Grafana:

```bash
docker compose -f docker-compose.yml -f docker-compose.ubuntu-monitoring.yml restart grafana
```

### Docker permission denied on Ubuntu

Use `sudo docker compose ...` or add the current user to the Docker group:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

## Demo Evidence

Use [assets/screenshots/README.md](assets/screenshots/README.md) as the checklist for GitHub and CV screenshots after deployment.

## Known Limitations

- In-process cache is not shared across multiple workers
- No request throttling on the chat endpoint
- CORS currently allows all origins
- Gemini latency varies with upstream load
- Legacy `.doc` files still require Windows COM automation

## Future Improvements

- Add HTTPS termination with Let's Encrypt or Cloudflare Tunnel
- Add alerting rules for uptime, disk pressure, and latency spikes
- Export structured logs to Loki or ELK
- Replace demo auth with production Firebase-first flows in deployment docs
- Add CI to validate Compose, Prometheus, and Grafana provisioning on every push
