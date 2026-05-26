#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://localhost}"
API_KEY="${API_KEY:-demo_employee_001}"

echo "Seeding demo traffic against: $BASE_URL"

curl -fsS "$BASE_URL/health" >/dev/null
curl -fsS "$BASE_URL/health" >/dev/null

curl -fsS -X POST "$BASE_URL/api/chat" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"message":"Quy định nghỉ phép năm của công ty là gì?","session_id":"seed-demo-001"}' >/dev/null

curl -fsS -X POST "$BASE_URL/api/chat" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"message":"Thủ tục xin nghỉ phép như thế nào?","session_id":"seed-demo-002"}' >/dev/null

echo "Demo traffic sent successfully."
