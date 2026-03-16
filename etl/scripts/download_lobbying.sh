#!/usr/bin/env bash
# Download lobbying returns from lobbying.ie
set -euo pipefail

DATA_DIR="${1:-./data/lobbying}"
mkdir -p "$DATA_DIR"

echo "Downloading lobbying returns..."
# The lobbying register provides CSV exports via their open data portal
# URL may need to be updated if the API changes
curl -L -o "$DATA_DIR/returns.csv" \
  "https://www.lobbying.ie/app/OpenData/download" \
  2>/dev/null || echo "Note: Direct download may require manual export from lobbying.ie"

echo "Done. Data saved to $DATA_DIR/"
