from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status, Form, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import io
import os
import logging
from typing import Optional

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

# Try to import optional dependencies
try:
    from database import get_db, APIKey, generate_api_key, create_tables
    from models import APIKeyCreate, APIKeyResponse, BackgroundRemovalResponse, ErrorResponse
    from background_remover import BackgroundRemover
    from auth import validate_api_key
    FULL_FUNCTIONALITY = True
    logger.info("All dependencies loaded successfully - full functionality enabled")
except ImportError as e:
    logger.warning(f"Some dependencies missing: {e} - running in limited mode")
    FULL_FUNCTIONALITY = False

# Initialize background remover lazily
logger.info("Setting up background remover (lazy initialization)...")
bg_remover = None

def get_background_remover():
    """Get background remover instance with lazy initialization"""
    global bg_remover
    if bg_remover is None:
        try:
            logger.info("Initializing background remover on first use...")
            if FULL_FUNCTIONALITY:
                bg_remover = BackgroundRemover()
                logger.info("Background remover initialized successfully")
            else:
                logger.warning("Background remover not available - dependencies missing")
                raise HTTPException(status_code=503, detail="Background remover not available")
        except Exception as e:
            logger.error(f"Failed to initialize background remover: {e}")
            raise HTTPException(status_code=503, detail="Background remover initialization failed")
    return bg_remover

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    if FULL_FUNCTIONALITY:
        try:
            logger.info("Creating database tables...")
            create_tables()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            # Don't fail startup, just log the error
    else:
        logger.info("Running in limited mode - database initialization skipped")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Background Remover API",
        "version": "1.0.0",
        "status": "running",
        "mode": "full" if FULL_FUNCTIONALITY else "limited",
        "port": os.getenv("PORT", "8000"),
        "last_updated": "2025-07-15T17:33:00Z",  # Force deployment indicator
        "endpoints": {
            "generate_api_key": "POST /api-keys",
            "list_api_keys": "GET /api-keys",
            "remove_background": "POST /remove-background",
            "health": "GET /health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint with memory info and BackgroundRemover status"""
    try:
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        # Get system memory info
        system_memory = psutil.virtual_memory()
        
        # Get BackgroundRemover health status
        bg_health = {}
        if FULL_FUNCTIONALITY:
            try:
                if bg_remover is not None:
                    bg_health = {
                        "status": "initialized",
                        "memory_usage": "active"
                    }
                else:
                    bg_health = {
                        "status": "not_initialized",
                        "memory_usage": "none"
                    }
            except Exception as e:
                bg_health = {
                    "status": "error",
                    "error": str(e)
                }
        else:
            bg_health = {
                "status": "disabled",
                "reason": "dependencies_missing"
            }
        
        return {
            "status": "healthy",
            "message": "Background Remover API is running",
            "mode": "full" if FULL_FUNCTIONALITY else "limited",
            "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
            "port": os.getenv("PORT", "8000"),
            "memory": {
                "process_memory_mb": round(memory_info.rss / 1024 / 1024, 2),
                "system_memory_total_gb": round(system_memory.total / 1024 / 1024 / 1024, 2),
                "system_memory_available_gb": round(system_memory.available / 1024 / 1024 / 1024, 2),
                "system_memory_percent": system_memory.percent
            },
            "background_remover": bg_health
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

# API key generation endpoint
@app.post("/api-keys")
async def generate_api_key_endpoint(
    key_name: str = Form(...)
):
    """Generate a new API key"""
    if not FULL_FUNCTIONALITY:
        # Fallback to simple key generation
        try:
            import secrets
            import string
            
            # Generate a random API key
            alphabet = string.ascii_letters + string.digits
            api_key = ''.join(secrets.choice(alphabet) for _ in range(32))
            
            return {
                "api_key": api_key,
                "name": key_name,
                "status": "active",
                "created_at": "2024-01-01T00:00:00Z",
                "note": "Limited mode - key not stored in database"
            }
        except Exception as e:
            logger.error(f"API key generation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Full functionality with database
    try:
        from database import get_db
        db = next(get_db())
        
        logger.info(f"Generating API key with name: {key_name}")
        
        # Generate API key
        api_key = generate_api_key()
        
        # Create API key record
        db_api_key = APIKey(
            key=api_key,
            name=key_name,
            is_active=True
        )
        db.add(db_api_key)
        db.commit()
        db.refresh(db_api_key)
        
        logger.info(f"API key generated successfully: {api_key[:8]}...")
        
        return APIKeyResponse(
            id=db_api_key.id,
            key=api_key,
            name=key_name,
            created_at=db_api_key.created_at,
            last_used=None,
            usage_count=0,
            is_active=True
        )
    except Exception as e:
        logger.error(f"Failed to generate API key: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate API key: {str(e)}")

# List API keys endpoint
@app.get("/api-keys")
async def list_api_keys():
    """List all API keys"""
    if not FULL_FUNCTIONALITY:
        return {
            "api_keys": [],
            "note": "Limited mode - API key listing not available"
        }
    
    try:
        from database import get_db
        db = next(get_db())
        
        logger.info("Listing API keys")
        
        # Get all API keys
        api_keys = db.query(APIKey).all()
        
        # Convert to response format
        response_keys = []
        for key in api_keys:
            response_keys.append({
                "api_key": key.key[:8] + "..." + key.key[-4:],  # Show partial key for security
                "name": key.name,
                "status": "active" if key.is_active else "inactive",
                "created_at": key.created_at.isoformat()
            })
        
        return {"api_keys": response_keys}
    except Exception as e:
        logger.error(f"Failed to list API keys: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list API keys: {str(e)}")

# Background removal endpoint
@app.post("/remove-background")
async def remove_background(
    file: UploadFile = File(...),
    alpha_matting: bool = Form(False),
    alpha_matting_foreground_threshold: int = Form(270),
    alpha_matting_background_threshold: int = Form(10),
    alpha_matting_erode_structure_size: int = Form(10),
    alpha_matting_base_size: int = Form(1000),
    api_key: str = Form(...)
):
    """Remove background from image"""
    if not FULL_FUNCTIONALITY:
        raise HTTPException(
            status_code=503,
            detail="Background removal not available in limited mode"
        )
    
    try:
        from database import get_db
        from auth import validate_api_key_string
        db = next(get_db())
        
        logger.info(f"Processing background removal request for file: {file.filename}")
        
        # Validate API key
        if not validate_api_key_string(api_key, db):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
        
        # Validate file
        if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PNG, JPG, and JPEG files are supported"
            )
        
        # Read file content
        content = await file.read()
        
        # Get background remover instance
        remover = get_background_remover()
        
        # Process image
        logger.info("Starting background removal process...")
        result_image, metadata = remover.remove_background(
            content,
            alpha_matting=alpha_matting,
            alpha_matting_foreground_threshold=alpha_matting_foreground_threshold,
            alpha_matting_background_threshold=alpha_matting_background_threshold,
            alpha_matting_erode_structure_size=alpha_matting_erode_structure_size,
            alpha_matting_base_size=alpha_matting_base_size
        )
        
        logger.info("Background removal completed successfully")
        
        # Convert PIL Image to bytes
        img_byte_arr = io.BytesIO()
        result_image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        # Return processed image
        return StreamingResponse(
            img_byte_arr,
            media_type="image/png",
            headers={
                "Content-Disposition": f"attachment; filename=processed_{file.filename.replace('.jpg', '.png').replace('.jpeg', '.png')}",
                "Access-Control-Allow-Origin": "*"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Background removal failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Background removal failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
