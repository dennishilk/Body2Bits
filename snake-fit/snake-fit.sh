#!/usr/bin/env bash
set -e

if [ ! -d ".venv" ]; then
  echo "❌ Game not installed."
  echo "👉 Run ./install.sh first"
  exit 1
fi

source .venv/bin/activate

echo "🐍 Launching Snake-Fit..."
python -m snakefit.game
