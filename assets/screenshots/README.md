# Demo Screenshot Checklist

Capture these artifacts after a successful Ubuntu deployment:

1. `docker compose ps`
2. `GET /health` response
3. `POST /api/chat` response with sources
4. Grafana `HR RAG Overview` dashboard
5. Prometheus targets page
6. Generated backup archive in `backups/`
7. Nginx reverse proxy serving `/health`

Suggested filenames:

- `01-docker-compose-ps.png`
- `02-health-response.png`
- `03-chat-response.png`
- `04-grafana-dashboard.png`
- `05-prometheus-targets.png`
- `06-backup-archive.png`
- `07-nginx-health.png`
