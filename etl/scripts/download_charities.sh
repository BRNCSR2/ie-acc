#!/usr/bin/env bash
# Download charities register from the Charities Regulator
set -euo pipefail

DATA_DIR="${1:-./data/charities}"
mkdir -p "$DATA_DIR"

echo "Downloading charities register..."
# The Charities Regulator provides bulk XLSX via their website
curl -L -o "$DATA_DIR/charities.xlsx" \
  "https://www.charitiesregulator.ie/media/1936/public-register-of-charities.xlsx" \
  2>/dev/null || echo "Note: URL may have changed. Check charitiesregulator.ie for current download link."

echo "Done. Data saved to $DATA_DIR/"
