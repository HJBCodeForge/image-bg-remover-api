#!/bin/bash

# Test Docker build locally before pushing to Railway

echo "🔧 Testing Docker build locally..."

# Build the Docker image
docker build -t bg-remover-test .

if [ $? -eq 0 ]; then
    echo "✅ Docker build successful!"
    
    echo "🚀 Testing container run..."
    
    # Test running the container
    docker run -p 8000:8000 -e PORT=8000 bg-remover-test &
    CONTAINER_PID=$!
    
    # Wait for the app to start
    sleep 10
    
    # Test the health endpoint
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Container is running successfully!"
        echo "🎉 Ready to deploy to Railway!"
    else
        echo "❌ Container failed to start properly"
        echo "🔍 Check the logs above for errors"
    fi
    
    # Clean up
    kill $CONTAINER_PID 2>/dev/null
    docker rm $(docker ps -aq --filter ancestor=bg-remover-test) 2>/dev/null
    docker rmi bg-remover-test 2>/dev/null
    
else
    echo "❌ Docker build failed!"
    echo "🔍 Check the error messages above"
    exit 1
fi
