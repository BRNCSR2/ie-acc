#!/usr/bin/env bash
# Download Oireachtas members data from api.oireachtas.ie
set -euo pipefail

DATA_DIR="${1:-./data/oireachtas}"
mkdir -p "$DATA_DIR"

echo "Downloading Oireachtas members..."
curl -L -o "$DATA_DIR/members.json" \
  "https://api.oireachtas.ie/v1/members?date_start=1900-01-01&limit=1000" \
  2>/dev/null

echo "Done. Data saved to $DATA_DIR/"
