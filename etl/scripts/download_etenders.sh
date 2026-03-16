#!/usr/bin/env bash
# Download procurement data from data.gov.ie / eTenders
set -euo pipefail

DATA_DIR="${1:-./data/etenders}"
mkdir -p "$DATA_DIR"

echo "Downloading eTenders procurement data..."
# data.gov.ie hosts procurement CSVs
curl -L -o "$DATA_DIR/contracts.csv" \
  "https://data.gov.ie/dataset/etenders-contracts/resource/download" \
  2>/dev/null || echo "Note: URL may need updating. Check data.gov.ie for current eTenders datasets."

echo "Done. Data saved to $DATA_DIR/"
