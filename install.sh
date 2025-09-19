#!/bin/bash

# Emergent Playtest Designer - Quick Installation Script
# This script sets up the project for immediate use

set -e

echo "🚀 Emergent Playtest Designer - Quick Installation"
echo "=================================================="

# Check Python version
echo "📋 Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    echo "✅ Python $PYTHON_VERSION found"
    
    if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 9) else 1)'; then
        echo "✅ Python version is compatible (3.9+)"
    else
        echo "❌ Python 3.9+ required. Current version: $PYTHON_VERSION"
        exit 1
    fi
else
    echo "❌ Python 3 not found. Please install Python 3.9+ first."
    exit 1
fi

# Check pip
echo "📋 Checking pip installation..."
if command -v pip3 &> /dev/null; then
    echo "✅ pip3 found"
    PIP_CMD="pip3"
elif python3 -m pip --version &> /dev/null; then
    echo "✅ pip found via python3 -m pip"
    PIP_CMD="python3 -m pip"
else
    echo "❌ pip not found. Please install pip first."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
$PIP_CMD install --upgrade pip
$PIP_CMD install -r requirements-minimal.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data

# Set permissions
echo "🔐 Setting permissions..."
chmod +x cli_simple.py

# Test installation
echo "🧪 Testing installation..."
python3 cli_simple.py validate

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "📋 Quick Start Commands:"
echo "   Demo:           python3 cli_simple.py demo"
echo "   Test Game:      python3 cli_simple.py test-game /path/to/game"
echo "   Start Server:   python3 cli_simple.py server"
echo "   Validate:       python3 cli_simple.py validate"
echo ""
echo "🐳 Docker Option:"
echo "   docker-compose up -d"
echo ""
echo "📖 For more information, see QUICK_START.md"
echo ""
echo "🚀 Ready to ship! Run 'python3 cli_simple.py demo' to see it in action."
