#!/bin/bash

# Render startup script
echo "🚀 Starting Background Remover API on Render..."

# Set environment variables
export HOST=${HOST:-0.0.0.0}
export PORT=${PORT:-10000}
export ENVIRONMENT=${ENVIRONMENT:-production}

echo "Host: $HOST"
echo "Port: $PORT"
echo "Environment: $ENVIRONMENT"

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Run the application with uvicorn directly
echo "Starting uvicorn server..."
uvicorn main:app --host $HOST --port $PORT --log-level info
