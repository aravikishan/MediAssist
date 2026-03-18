#!/usr/bin/env bash
set -euo pipefail

echo "=== MediAssist - Medical Symptom Checker ==="
echo ""

# Create required directories
mkdir -p instance

# Install dependencies
if [ -f requirements.txt ]; then
    echo "[1/3] Installing dependencies..."
    pip install -q -r requirements.txt
fi

echo "[2/3] Initialising database..."
echo "[3/3] Starting server on port 8011..."
echo ""
echo "  Open http://localhost:8011 in your browser"
echo ""

python app.py
