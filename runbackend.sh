#!/usr/bin/env bash
# Bash direct runner for Mission Mirror
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================================"
echo "  Launching MISSION MIRROR Server..."
echo "========================================================"

python3 run.py

