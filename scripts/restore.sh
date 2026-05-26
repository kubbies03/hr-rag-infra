#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <backup-archive.tar.gz>"
  exit 1
fi

ARCHIVE="$1"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ ! -f "$ARCHIVE" ]]; then
  echo "Backup archive not found: $ARCHIVE"
  exit 1
fi

mkdir -p \
  "$ROOT_DIR/data/sqlite" \
  "$ROOT_DIR/data/chroma" \
  "$ROOT_DIR/data/docs"

tar -xzf "$ARCHIVE" -C "$ROOT_DIR"

echo "Restore completed from: $ARCHIVE"

