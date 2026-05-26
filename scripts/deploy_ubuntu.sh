#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR"
docker compose -f docker-compose.yml -f docker-compose.ubuntu-monitoring.yml up -d --build

echo "Ubuntu monitoring stack is up."
echo "Nginx:      http://localhost"
echo "Prometheus: http://localhost:9090"
echo "Grafana:    http://localhost:3000"
