from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Background Remover API",
    description="API for removing backgrounds from images with API key authentication",
    version="1.0.0"
)

logger.info("Starting Background Remover API...")

# Add CORS middleware - must be added before other middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for debugging
    allow_credentials=False,  # Must be False when using wildcard origins
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add explicit OPTIONS handler for preflight requests
@app.options("/{path:path}")
async def handle_options(path: str):
    """Handle preflight OPTIONS requests"""
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "86400"
        }
    )

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Background Remover API",
        "version": "1.0.0",
        "status": "running",
        "port": os.getenv("PORT", "8000")
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "message": "Background Remover API is running",
        "port": os.getenv("PORT", "8000")
    }

# Simple API key generation endpoint for testing
@app.post("/api-keys")
async def generate_api_key_test():
    """Generate a test API key"""
    return {
        "api_key": "test-key-123",
        "name": "Test Key",
        "status": "active"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
