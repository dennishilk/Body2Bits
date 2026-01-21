#!/usr/bin/env bash
set -e

echo "🐍 Snake-Fit Installer"
echo "----------------------"

# Check Python
if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ Python 3 not found. Please install Python 3."
  exit 1
fi

# Create venv
if [ ! -d ".venv" ]; then
  echo "📦 Creating virtual environment..."
  python3 -m venv .venv
else
  echo "✅ Virtual environment already exists."
fi

source .venv/bin/activate

echo "📦 Upgrading pip..."
pip install --upgrade pip

echo "📦 Installing dependencies..."
pip install pygame

echo "🎮 Making starter executable..."
chmod +x snake-fit.sh

echo
echo "✅ Installation complete!"
echo "👉 Start the game with: ./snake-fit.sh"