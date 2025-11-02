from fastapi import FastAPI, File, Form, UploadFile, HTTPException, status
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from datetime import datetime, timezone
import io
import os
import logging
import base64
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import background remover
from background_remover import BackgroundRemover

# Initialize background remover
background_remover = None

def get_background_remover():
    global background_remover
    if background_remover is None:
        logger.info("Initializing background remover on first use...")
        background_remover = BackgroundRemover()
        logger.info("Background remover initialized successfully")
    return background_remover

# Mount static files for assets
if os.path.exists("assets"):
    app.mount("/assets", StaticFiles(directory="assets"), name="assets")
else:
    logger.warning("Assets directory not found - static file serving disabled")

# Mount static files for images
if os.path.exists("images"):
    app.mount("/images", StaticFiles(directory="images"), name="images")
else:
    logger.warning("Images directory not found - static file serving disabled")

# Route handlers
@app.get("/")
async def root():
    """Serve the landing page"""
    return FileResponse("index.html")

@app.get("/favicon.ico")
async def favicon():
    """Serve favicon"""
    if os.path.exists("assets/favicon.ico"):
        return FileResponse("assets/favicon.ico")
    return HTTPException(status_code=404)

# All authentication-related endpoints have been removed to simplify the app

@app.post("/remove-background")
async def remove_background_endpoint(
    file: UploadFile = File(...),
    model_hint: str = Form("general"),
    alpha_matting: bool = Form(False),
    alpha_matting_foreground_threshold: int = Form(240),
    alpha_matting_background_threshold: int = Form(10),
    alpha_matting_erode_structure_size: int = Form(10),
    alpha_matting_base_size: int = Form(1000),
    return_json: bool = Form(False)
):
    import traceback
    try:
        logger.info(f"Processing background removal request for file: {file.filename}")
        
        # Read image file
        contents = await file.read()

        # Enforce 5MB max file size (5 * 1024 * 1024 bytes)
        max_bytes = 5 * 1024 * 1024
        if len(contents) > max_bytes:
            raise HTTPException(
                status_code=413,
                detail="Image too large. Maximum allowed size is 5MB."
            )
        
        # Get background remover instance
        remover = get_background_remover()
        
        # Process image
        logger.info("Starting background removal process...")
        try:
            processed_image, metadata = remover.remove_background(
                image=contents,
                model_hint=model_hint,
                alpha_matting=alpha_matting,
                alpha_matting_foreground_threshold=alpha_matting_foreground_threshold,
                alpha_matting_background_threshold=alpha_matting_background_threshold,
                alpha_matting_erode_structure_size=alpha_matting_erode_structure_size,
                alpha_matting_base_size=alpha_matting_base_size
            )
            
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            processed_image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            if return_json:
                # Return base64 encoded image and metadata
                return {
                    "image": base64.b64encode(img_byte_arr.getvalue()).decode(),
                    "metadata": metadata
                }
            else:
                # Return binary image
                return StreamingResponse(
                    io.BytesIO(img_byte_arr.getvalue()),
                    media_type="image/png"
                )
                
        except Exception as e:
            logger.error(f"Background removal failed: {e}")
            logger.error(traceback.format_exc())
            if "Cholesky" in str(e):
                raise HTTPException(
                    status_code=422,
                    detail="Image processing failed. Please try again with alpha matting disabled."
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Background removal failed: {str(e)}"
                )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.on_event("startup")
async def startup_event():
    logger.info("All dependencies loaded successfully - full functionality enabled")
    logger.info("Starting Background Remover API...")
    
    # Initialize background remover at startup
    get_background_remover()

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Background Remover API...")
    # Cleanup if needed
