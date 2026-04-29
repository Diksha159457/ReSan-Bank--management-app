#!/bin/bash

# ReSan Bank - Quick Start Script
# This script sets up and runs the application

# Get the project root directory (parent of scripts folder)
cd "$(dirname "$0")/.." || exit

echo "🏦 ReSan Bank - Starting..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python found: $(python3 --version)"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install/update dependencies
echo ""
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Check for .env file
echo ""
if [ -f "config/.env" ]; then
    echo "✓ config/.env file found - SMS may be enabled"
    # Copy to root for the app to read
    cp config/.env .env
elif [ -f ".env" ]; then
    echo "✓ .env file found - SMS may be enabled"
else
    echo "ℹ️  No .env file - running in dev mode (OTP in console)"
    echo "   To enable SMS: cp config/.env.example config/.env and add Twilio credentials"
fi

# Check if data file exists
if [ ! -f "resan_data.json" ]; then
    echo ""
    echo "📄 Creating initial data file..."
    echo '{"accounts":{},"transactions":{}}' > resan_data.json
    echo "✓ Data file created"
fi

# Create uploads directory if it doesn't exist
if [ ! -d "uploads" ]; then
    mkdir uploads
    echo "✓ Uploads directory created"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Starting ReSan Bank..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "   🌐 App will be available at: http://localhost:8000"
echo "   📚 API docs available at: http://localhost:8000/docs"
echo ""
echo "   Press Ctrl+C to stop the server"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run the application
python3 main.py
