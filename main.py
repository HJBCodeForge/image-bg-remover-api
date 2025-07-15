from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status, Form
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import io
import os
import logging
from typing import List, Optional

from database import get_db, APIKey, generate_api_key, create_tables
from models import APIKeyCreate, APIKeyResponse, BackgroundRemovalResponse, ErrorResponse
from background_remover import BackgroundRemover
from auth import validate_api_key

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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "http://localhost:8000",
        "https://bg-remover-frontend-vfhc.onrender.com",
        "https://bg-remover-frontend-tau.vercel.app",
        "https://web-production-faaf.up.railway.app",
        "*"  # Allow all origins temporarily for debugging
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize background remover lazily
logger.info("Setting up background remover (lazy initialization)...")
bg_remover = None

def get_background_remover():
    """Get background remover instance with lazy initialization"""
    global bg_remover
    if bg_remover is None:
        logger.info("Initializing background remover on first use...")
        bg_remover = BackgroundRemover()
        logger.info("Background remover initialized successfully")
    return bg_remover

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Creating database tables...")
    create_tables()
    logger.info("Database tables created successfully")
    # Don't initialize background remover here - wait until first use

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Background Remover API",
        "version": "1.0.0",
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
        try:
            remover = get_background_remover()
            bg_health = remover.health_check()
        except Exception as e:
            bg_health = {"status": "error", "error": str(e)}
        
        return {
            "status": "healthy", 
            "service": "background-remover-api",
            "memory_mb": round(memory_info.rss / 1024 / 1024, 2),
            "memory_percent": round(process.memory_percent(), 2),
            "system_memory_total_mb": round(system_memory.total / 1024 / 1024, 2),
            "system_memory_available_mb": round(system_memory.available / 1024 / 1024, 2),
            "system_memory_used_percent": system_memory.percent,
            "background_remover": bg_health
        }
    except Exception as e:
        return {
            "status": "healthy", 
            "service": "background-remover-api",
            "error": str(e),
            "background_remover": {"status": "error", "error": "Not initialized"}
        }

@app.post("/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    api_key_data: APIKeyCreate,
    db: Session = Depends(get_db)
):
    """
    Generate a new API key
    """
    try:
        # Generate new API key
        new_key = generate_api_key()
        
        # Create database entry
        db_api_key = APIKey(
            key=new_key,
            name=api_key_data.name
        )
        
        db.add(db_api_key)
        db.commit()
        db.refresh(db_api_key)
        
        # Convert is_active string to boolean for response
        response_data = APIKeyResponse(
            id=db_api_key.id,
            key=db_api_key.key,
            name=db_api_key.name,
            created_at=db_api_key.created_at,
            last_used=db_api_key.last_used,
            usage_count=db_api_key.usage_count,
            is_active=db_api_key.is_active == "true"
        )
        
        return response_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating API key: {str(e)}"
        )

@app.get("/api-keys", response_model=List[APIKeyResponse])
async def list_api_keys(db: Session = Depends(get_db)):
    """
    List all API keys (for admin purposes)
    """
    try:
        api_keys = db.query(APIKey).all()
        
        response_data = []
        for api_key in api_keys:
            response_data.append(APIKeyResponse(
                id=api_key.id,
                key=api_key.key,
                name=api_key.name,
                created_at=api_key.created_at,
                last_used=api_key.last_used,
                usage_count=api_key.usage_count,
                is_active=api_key.is_active == "true"
            ))
        
        return response_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving API keys: {str(e)}"
        )

@app.post("/remove-background")
async def remove_background(
    file: UploadFile = File(...),
    model_hint: Optional[str] = Form(None),
    alpha_matting: bool = Form(True),
    alpha_matting_foreground_threshold: int = Form(240),
    alpha_matting_background_threshold: int = Form(10),
    alpha_matting_erode_structure_size: int = Form(10),
    alpha_matting_base_size: int = Form(1000),
    return_json: bool = Form(False),
    api_key: APIKey = Depends(validate_api_key)
):
    """
    Remove background from image using BackgroundRemover-main
    
    Parameters:
    - file: Image file to process
    - model_hint: Model preference ('human', 'object', 'general')
    - alpha_matting: Enable alpha matting for better edges (default: True)
    - alpha_matting_foreground_threshold: Foreground threshold (default: 240)
    - alpha_matting_background_threshold: Background threshold (default: 10)
    - alpha_matting_erode_structure_size: Erosion size (default: 10)
    - alpha_matting_base_size: Base size for processing (default: 1000)
    - return_json: Return JSON response with base64 image (default: False)
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=ErrorResponse(
                    success=False,
                    error="Invalid file type",
                    details="Please upload an image file"
                ).dict()
            )
        
        # Read image bytes
        image_bytes = await file.read()
        
        # Check file size (limit to 5MB for free tier)
        max_size = 5 * 1024 * 1024  # 5MB
        if len(image_bytes) > max_size:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=ErrorResponse(
                    success=False,
                    error="File too large",
                    details=f"File size must be less than {max_size // (1024 * 1024)}MB"
                ).dict()
            )
        
        # Remove background using BackgroundRemover-main
        remover = get_background_remover()
        processed_image_bytes, model_used, processing_time = remover.remove_background(
            image_bytes, 
            model_hint=model_hint,
            alpha_matting=alpha_matting,
            alpha_matting_foreground_threshold=alpha_matting_foreground_threshold,
            alpha_matting_background_threshold=alpha_matting_background_threshold,
            alpha_matting_erode_structure_size=alpha_matting_erode_structure_size,
            alpha_matting_base_size=alpha_matting_base_size
        )
        
        if return_json:
            # Return JSON response with processing info
            import base64
            
            processed_image_base64 = base64.b64encode(processed_image_bytes).decode('utf-8')
            
            return BackgroundRemovalResponse(
                success=True,
                message="Background removed successfully",
                processed_image_url=f"data:image/png;base64,{processed_image_base64}",
                processing_time=processing_time,
                model_used=model_used
            )
        else:
            # Return image file directly
            return StreamingResponse(
                io.BytesIO(processed_image_bytes),
                media_type="image/png",
                headers={
                    "Content-Disposition": f"attachment; filename=processed_{file.filename.replace('.', '_')}.png",
                    "X-Processing-Time": str(processing_time),
                    "X-Model-Used": model_used
                }
            )
            
    except Exception as e:
        # Clean up memory on error
        import gc
        gc.collect()
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                success=False,
                error="Processing failed",
                details=str(e)
            ).dict()
        )

@app.get("/models")
async def get_models():
    """Get available background removal models"""
    try:
        remover = get_background_remover()
        return {
            "available_models": remover.get_available_models(),
            "default_model": remover.default_model
        }
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": f"Failed to get models: {str(e)}"}
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Simple processing failed: {str(e)}",
                "traceback": traceback.format_exc()
            }
        )

@app.delete("/api-keys/{api_key_id}")
async def deactivate_api_key(
    api_key_id: int,
    db: Session = Depends(get_db)
):
    """
    Deactivate an API key
    """
    try:
        db_api_key = db.query(APIKey).filter(APIKey.id == api_key_id).first()
        
        if not db_api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        
        db_api_key.is_active = "false"
        db.commit()
        
        return {"message": "API key deactivated successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deactivating API key: {str(e)}"
        )

@app.get("/test-rembg")
async def test_rembg():
    """Test endpoint to check rembg initialization"""
    try:
        # Test basic rembg import
        from rembg import remove
        
        # Test session creation
        from rembg import new_session
        
        # Try to create a simple session
        session = new_session('u2net')
        
        return {
            "status": "success",
            "message": "rembg is working properly",
            "session_created": True
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": f"rembg test failed: {str(e)}",
            "traceback": traceback.format_exc()
        }

if __name__ == "__main__":
    import uvicorn
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Use Render's PORT environment variable or default to 8000
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))  # Render always sets PORT
    
    print(f"Starting server on {host}:{port}")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    
    uvicorn.run(
        app, 
        host=host, 
        port=port,
        log_level="info"
    )
