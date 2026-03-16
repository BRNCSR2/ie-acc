#!/usr/bin/env bash
# Download Property Price Register data
set -euo pipefail

DATA_DIR="${1:-./data/ppr}"
mkdir -p "$DATA_DIR"

echo "Downloading Property Price Register data..."
# PSRA publishes all residential property sales since 2010
curl -L -o "$DATA_DIR/sales.csv" \
  "https://www.propertypriceregister.ie/website/npsra/ppr/npsra-ppr.nsf/Downloads/PPR-ALL.zip/\$FILE/PPR-ALL.zip" \
  2>/dev/null || echo "Note: URL may need updating. Check propertypriceregister.ie for current download."

# Extract if zip was downloaded
if [ -f "$DATA_DIR/PPR-ALL.zip" ]; then
  cd "$DATA_DIR"
  unzip -o PPR-ALL.zip
  echo "Extracted PPR data."
fi

echo "Done. Data saved to $DATA_DIR/"
