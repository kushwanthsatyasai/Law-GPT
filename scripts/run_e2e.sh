#!/usr/bin/env bash
set -euo pipefail

API=${API:-http://localhost:8000}

echo "Waiting for backend..."
TRIES=0
until curl -s "$API/health" >/dev/null; do
  sleep 1
  TRIES=$((TRIES+1))
  if [ $TRIES -gt 60 ]; then
    echo "Backend not ready"; exit 1
  fi
done
echo "Backend healthy"

TOKEN=$(curl -s -X POST "$API/register" -H "Content-Type: application/json" -d '{"email":"test@example.com","password":"test123","role":"lawyer"}' | jq -r .access_token)

for f in sample_data/*.txt; do
  curl -s -X POST "$API/upload" -H "Authorization: Bearer $TOKEN" -F "file=@$f" -F "title=$(basename $f)" >/dev/null
done

curl -s -X POST "$API/ingest" -H "Authorization: Bearer $TOKEN" | jq .

RES=$(curl -s -X POST "$API/query" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"question":"What is about confidentiality?"}')
echo "$RES" | jq .
ANS=$(echo "$RES" | jq -r .answer)
if [ -z "$ANS" ] || [ "$ANS" = "null" ]; then
  echo "Empty answer"; exit 1
fi

echo "E2E OK"
