#!/bin/bash

# Studio Voice Assistant Launcher
# Quick script to launch Studio with the virtual environment

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "Error: Virtual environment not found!"
    echo "Please run ./setup.sh first"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found!"
    echo "Please copy .env.example to .env and add your OpenAI API key"
    exit 1
fi

# Check if OpenAI API key is set
if ! grep -q "OPENAI_API_KEY=sk-" .env; then
    echo "Warning: OpenAI API key may not be set in .env"
    echo "Please make sure you have added your API key to the .env file"
    read -p "Press enter to continue anyway, or Ctrl+C to exit..."
fi

# Launch Studio
echo "Launching Studio..."
python3 studio.py
