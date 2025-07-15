from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status, Form, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import io
import os
import logging
from typing import List, Optional

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
        "port": os.getenv("PORT", "8000"),
        "endpoints": {
            "generate_api_key": "POST /api-keys",
            "list_api_keys": "GET /api-keys",
            "remove_background": "POST /remove-background",
            "health": "GET /health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        return {
            "status": "healthy", 
            "message": "Background Remover API is running",
            "port": os.getenv("PORT", "8000"),
            "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

# Simple API key generation endpoint for testing
@app.post("/api-keys")
async def generate_api_key_test():
    """Generate a test API key"""
    try:
        import secrets
        import string
        
        # Generate a random API key
        alphabet = string.ascii_letters + string.digits
        api_key = ''.join(secrets.choice(alphabet) for _ in range(32))
        
        return {
            "api_key": api_key,
            "name": "Test Key",
            "status": "active",
            "created_at": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"API key generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Placeholder for background removal endpoint
@app.post("/remove-background")
async def remove_background_placeholder():
    """Placeholder for background removal"""
    return {
        "message": "Background removal endpoint - coming soon",
        "status": "placeholder"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
