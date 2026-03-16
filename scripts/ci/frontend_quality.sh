#!/usr/bin/env bash
set -euo pipefail

cd frontend
npm ci
npx eslint src/
npx tsc --noEmit
npm test -- --run
