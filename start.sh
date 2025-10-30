#!/bin/bash

# AI Spot Admin Dashboard - Quick Start Script

echo "🤖 AI Spot Admin Dashboard - Quick Start"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate
echo ""

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found"
    echo "📋 Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your SMTP_PASSWORD"
    echo ""
fi

# Check if templates directory exists
if [ ! -d "templates" ]; then
    echo "❌ templates/ directory not found"
    exit 1
fi

if [ ! -f "templates/tablestandee.html" ]; then
    echo "❌ templates/tablestandee.html not found"
    exit 1
fi

echo "✅ All files in place"
echo ""

# Run the application
echo "🚀 Starting AI Spot Admin Dashboard..."
echo ""
echo "📍 Dashboard will open at: http://localhost:8501"
echo "👤 Login credentials:"
echo "   Username: admin"
echo "   Password: arijitwith"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
streamlit run app.py
