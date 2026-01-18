#!/bin/bash

# Setup script for applenotes-organization MCP server

set -e

echo "Setting up applenotes-organization MCP server..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.10 or later."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
if [ "$(echo "$PYTHON_VERSION < 3.10" | bc)" -eq 1 ]; then
    echo "Error: Python 3.10 or later is required. Current version: $PYTHON_VERSION"
    exit 1
fi

echo "✓ Python version: $(python3 --version)"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate
echo "✓ Virtual environment activated"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install the package in development mode
echo "Installing applenotes-organization..."
pip install -e .

echo ""
echo "✓ Installation complete!"
echo ""
echo "To start the MCP server, run:"
echo "  applenotes-mcp"
echo ""
echo "Important: Grant Full Disk Access to your terminal/IDE:"
echo "  System Settings → Privacy & Security → Full Disk Access"
echo ""
