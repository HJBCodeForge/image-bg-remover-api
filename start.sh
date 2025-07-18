#!/bin/bash

# Railway startup script to handle PORT environment variable
PORT=${PORT:-8000}

echo "Starting application on port $PORT..."

exec uvicorn main:app --host 0.0.0.0 --port $PORT
