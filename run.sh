#!/bin/bash

# Background Remover API - Setup and Run Script

echo "🚀 Setting up Background Remover API..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists, if not copy from example
if [ ! -f ".env" ]; then
    echo "⚙️  Setting up environment variables..."
    cp .env .env.backup 2>/dev/null || true
    echo "Environment file created. Please review .env file for configuration."
fi

echo "✅ Setup complete!"
echo ""
echo "🏃‍♂️ Starting the API server..."
echo "📖 API Documentation will be available at: http://localhost:8000/docs"
echo "🌐 API Root will be available at: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the API
python main.py
