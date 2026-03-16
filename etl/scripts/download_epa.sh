#!/usr/bin/env bash
# Download EPA licence data from data.epa.ie
set -euo pipefail

DATA_DIR="${1:-./data/epa}"
mkdir -p "$DATA_DIR"

echo "Downloading EPA licence data..."
# EPA LEAP database exports
curl -L -o "$DATA_DIR/licences.csv" \
  "https://data.epa.ie/api/3/action/datastore_dump?resource_id=epa-licences" \
  2>/dev/null || echo "Note: URL may need updating. Check data.epa.ie for current licence datasets."

echo "Done. Data saved to $DATA_DIR/"
