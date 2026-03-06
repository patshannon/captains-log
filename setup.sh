#!/usr/bin/env bash
set -e

VENV_DIR=".venv"

if [ -d "$VENV_DIR" ]; then
  echo "Virtual environment already exists at $VENV_DIR"
else
  echo "Creating virtual environment..."
  python3 -m venv "$VENV_DIR"
fi

echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Setup complete! Activate the environment with:"
echo "  source $VENV_DIR/bin/activate"
