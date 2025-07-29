from fastapi import FastAPI, File, Form, UploadFile, HTTPException, status, Depends
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
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
from database import get_db, User, APIKey
from models import UserCreate, UserLogin, UserResponse, TokenResponse, APIKeyCreate, APIKeyResponse
from auth import create_access_token, get_current_user, hash_password, verify_password

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

@app.get("/dashboard")
async def dashboard():
    """Serve the dashboard page"""
    return FileResponse("dashboard.html")

@app.get("/favicon.ico")
async def favicon():
    """Serve favicon"""
    if os.path.exists("assets/favicon.ico"):
        return FileResponse("assets/favicon.ico")
    return HTTPException(status_code=404)

# Authentication endpoints
@app.post("/auth/register", response_model=TokenResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = hash_password(user.password)
        db_user = User(
            email=user.email,
            name=user.name,
            password_hash=hashed_password
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Create access token
        access_token = create_access_token(data={"sub": str(db_user.id)})
        
        # Update last login
        db_user.last_login = datetime.now(timezone.utc)
        db.commit()
        
        user_response = UserResponse(
            id=db_user.id,
            email=db_user.email,
            name=db_user.name,
            created_at=db_user.created_at,
            last_login=db_user.last_login,
            is_active=db_user.is_active,
            api_calls_count=db_user.api_calls_count if db_user.api_calls_count is not None else 0
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/auth/login", response_model=TokenResponse)
async def login_user(user: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token"""
    try:
        # Check if user exists
        db_user = db.query(User).filter(User.email == user.email).first()
        if not db_user or not verify_password(user.password, db_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        if not db_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is inactive"
            )
        
        # Create access token
        access_token = create_access_token(data={"sub": str(db_user.id)})
        
        # Update last login
        db_user.last_login = datetime.now(timezone.utc)
        db.commit()
        
        user_response = UserResponse(
            id=db_user.id,
            email=db_user.email,
            name=db_user.name,
            created_at=db_user.created_at,
            last_login=db_user.last_login,
            is_active=db_user.is_active,
            api_calls_count=db_user.api_calls_count if db_user.api_calls_count is not None else 0
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
        is_active=current_user.is_active,
        api_calls_count=current_user.api_calls_count if current_user.api_calls_count is not None else 0
    )

@app.get("/auth/api-keys", response_model=List[APIKeyResponse])
async def get_user_api_keys(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get API keys for the current user"""
    api_keys = db.query(APIKey).filter(APIKey.user_id == current_user.id).all()
    return [APIKeyResponse(
        id=key.id,
        key=key.key if key.key is not None else '',
        name=key.name if key.name is not None else '',
        created_at=key.created_at,
        last_used=key.last_used,
        usage_count=key.usage_count if key.usage_count is not None else 0,
        is_active=bool(key.is_active) if key.is_active is not None else True,
        user_id=key.user_id if key.user_id is not None else current_user.id
    ) for key in api_keys]

@app.post("/auth/api-keys", response_model=APIKeyResponse)
async def create_user_api_key(
    key_data: APIKeyCreate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Create a new API key for the current user"""
    try:
        # Generate API key
        from auth import generate_api_key
        api_key = generate_api_key()
        
        # Create API key record
        db_api_key = APIKey(
            key=api_key,
            name=key_data.name,
            user_id=current_user.id,
            is_active=True
        )
        db.add(db_api_key)
        db.commit()
        db.refresh(db_api_key)
        
        return APIKeyResponse(
            id=db_api_key.id,
            key=api_key,
            name=key_data.name,
            created_at=db_api_key.created_at,
            last_used=None,
            usage_count=0,
            is_active=True,
            user_id=current_user.id
        )
    except Exception as e:
        logger.error(f"Failed to create API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to create API key")

@app.post("/remove-background")
async def remove_background_endpoint(
    file: UploadFile = File(...),
    api_key: str = Form(...),
    model_hint: str = Form("general"),
    alpha_matting: bool = Form(True),
    alpha_matting_foreground_threshold: int = Form(240),
    alpha_matting_background_threshold: int = Form(10),
    alpha_matting_erode_structure_size: int = Form(10),
    alpha_matting_base_size: int = Form(1000),
    return_json: bool = Form(False)
):
    import traceback
    try:
        # Validate API key
        logger.info(f"Processing background removal request for file: {file.filename}")
        logger.info("Validating API key string: " + api_key[:10] + "...")
        
        # Get database session
        from database import get_db
        db = next(get_db())
        
        # Import and use the correct validation function
        from auth import validate_api_key_string
        if not validate_api_key_string(api_key, db):
            raise HTTPException(
                status_code=401,
                detail="Invalid API key"
            )
        
        logger.info("API key string validated successfully")
        
        # Read image file
        contents = await file.read()
        
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
