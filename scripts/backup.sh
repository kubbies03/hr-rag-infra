#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="$ROOT_DIR/backups"
TIMESTAMP="$(date +%Y-%m-%d-%H%M)"
ARCHIVE="$BACKUP_DIR/hr-rag-backup-$TIMESTAMP.tar.gz"

mkdir -p "$BACKUP_DIR"

tar -czf "$ARCHIVE" \
  -C "$ROOT_DIR" \
  data/sqlite \
  data/chroma \
  data/docs \
  monitoring \
  .env.example \
  docker-compose.yml \
  nginx/nginx.conf

echo "Backup created: $ARCHIVE"
