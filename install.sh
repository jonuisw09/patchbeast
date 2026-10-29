#!/usr/bin/env bash
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
python3 -m pip install --break-system-packages "$DIR" 2>/dev/null || python3 -m pip install "$DIR"
echo "PatchBeast installed. Run: patchbeast"