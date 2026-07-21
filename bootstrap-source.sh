#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [[ ! -f .bootstrap/part00 ]]; then
  echo "Application source is already expanded."
  exit 0
fi

archive="$(mktemp --suffix=.tar.gz)"
trap 'rm -f "$archive"' EXIT

cat .bootstrap/part* | base64 --decode > "$archive"
tar -tzf "$archive" >/dev/null
tar -xzf "$archive" -C .

echo "Application source expanded successfully."
echo "Run: docker compose up -d --build"
