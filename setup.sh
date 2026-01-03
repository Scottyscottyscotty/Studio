#!/bin/bash

# Studio Voice Assistant Setup Script
# This script sets up the development environment for Studio

set -e  # Exit on error

echo "====================================="
echo "Studio Voice Assistant Setup"
echo "====================================="
echo ""

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Error: This application requires macOS"
    exit 1
fi

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    echo "Please install Python 3 from https://www.python.org/"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is required but not installed."
    echo "Please install pip3"
    exit 1
fi

echo "✓ pip3 found"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install PortAudio (required for pyaudio)
echo ""
echo "Checking for PortAudio..."
if ! command -v brew &> /dev/null; then
    echo "Warning: Homebrew not found. Please install PortAudio manually:"
    echo "  brew install portaudio"
    read -p "Press enter when PortAudio is installed..."
else
    if ! brew list portaudio &> /dev/null; then
        echo "Installing PortAudio via Homebrew..."
        brew install portaudio
    else
        echo "✓ PortAudio already installed"
    fi
fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your OpenAI API key"
    echo "   You can get an API key from: https://platform.openai.com/api-keys"
    read -p "Press enter to open .env file in default editor..."
    open .env
else
    echo "✓ .env file already exists"
fi

# Create recordings directory
mkdir -p ~/.studio/recordings
echo "✓ Recordings directory created"

echo ""
echo "====================================="
echo "Setup Complete!"
echo "====================================="
echo ""
echo "Next steps:"
echo "1. Make sure your OPENAI_API_KEY is set in the .env file"
echo "2. Make sure Capture One is installed on your system"
echo "3. Run 'source venv/bin/activate' to activate the virtual environment"
echo "4. Run 'python3 studio.py' to start Studio"
echo ""
echo "Note: You may need to grant microphone permissions when first running the app."
echo ""
