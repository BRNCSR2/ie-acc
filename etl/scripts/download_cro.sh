#!/usr/bin/env bash
set -euo pipefail

DATA_DIR="${1:-./data/cro}"
URL="https://opendata.cro.ie/dataset/bf6f837d-0946-4c14-9a99-82cd6980c121/resource/3fef41bc-b8f4-4b10-8434-ce51c29b1bba/download/companies.csv.zip"

echo "Downloading CRO company register..."
mkdir -p "$DATA_DIR"

if command -v curl &> /dev/null; then
    curl -L -o "$DATA_DIR/companies.csv.zip" "$URL"
elif command -v wget &> /dev/null; then
    wget -O "$DATA_DIR/companies.csv.zip" "$URL"
else
    echo "Error: curl or wget required"
    exit 1
fi

echo "Extracting..."
cd "$DATA_DIR"
unzip -o companies.csv.zip
echo "Done. CRO data at: $DATA_DIR/"
ls -lh "$DATA_DIR/"
