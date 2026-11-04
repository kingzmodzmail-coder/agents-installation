#!/bin/bash
set -e

echo "Setting up Agents Installation environment..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Copy env example
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example. Please edit with your API keys."
fi

echo "Setup complete. Activate with: source venv/bin/activate"
