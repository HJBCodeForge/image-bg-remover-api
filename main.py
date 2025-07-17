from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status, Form, Request
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import io
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
    from database import get_db, APIKey, User, generate_api_key, create_tables, hash_password, verify_password
    from models import (
        APIKeyCreate, APIKeyResponse, BackgroundRemovalResponse, ErrorResponse,
        UserCreate, UserLogin, UserResponse, TokenResponse
    )
    from background_remover import BackgroundRemover
    from auth import validate_api_key, create_access_token, get_current_user, get_optional_user
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
    """Serve the main HTML interface"""
    return FileResponse("index.html")

@app.get("/api")
async def api_info():
    """API information endpoint"""
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

# ==================== USER AUTHENTICATION ENDPOINTS ====================

@app.post("/auth/register", response_model=TokenResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    if not FULL_FUNCTIONALITY:
        raise HTTPException(status_code=503, detail="User registration not available in limited mode")
    
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
        db_user.last_login = datetime.utcnow()
        db.commit()
        
        user_response = UserResponse(
            id=db_user.id,
            email=db_user.email,
            name=db_user.name,
            created_at=db_user.created_at,
            last_login=db_user.last_login,
            is_active=db_user.is_active,
            api_calls_count=db_user.api_calls_count
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
    if not FULL_FUNCTIONALITY:
        raise HTTPException(status_code=503, detail="User login not available in limited mode")
    
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
        db_user.last_login = datetime.utcnow()
        db.commit()
        
        user_response = UserResponse(
            id=db_user.id,
            email=db_user.email,
            name=db_user.name,
            created_at=db_user.created_at,
            last_login=db_user.last_login,
            is_active=db_user.is_active,
            api_calls_count=db_user.api_calls_count
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
        api_calls_count=current_user.api_calls_count
    )

@app.get("/auth/api-keys", response_model=List[APIKeyResponse])
async def get_user_api_keys(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get API keys for the current user"""
    api_keys = db.query(APIKey).filter(APIKey.user_id == current_user.id).all()
    return [APIKeyResponse(
        id=key.id,
        key=key.key,
        name=key.name,
        created_at=key.created_at,
        last_used=key.last_used,
        usage_count=key.usage_count,
        is_active=key.is_active,
        user_id=key.user_id
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

@app.delete("/auth/api-keys/{key_id}")
async def delete_user_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an API key owned by the current user"""
    api_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.user_id == current_user.id
    ).first()
    
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    db.delete(api_key)
    db.commit()
    
    return {"message": "API key deleted successfully"}

# ==================== END USER AUTHENTICATION ENDPOINTS ====================

# Mount static files for assets (only if directory exists)
if os.path.exists("assets"):
    app.mount("/assets", StaticFiles(directory="assets"), name="assets")
else:
    logger.warning("Assets directory not found - static file serving disabled")

# Favicon handler
@app.get("/favicon.ico")
async def favicon():
    """Serve favicon or return 404"""
    return FileResponse("assets/favicon.ico") if os.path.exists("assets/favicon.ico") else HTTPException(status_code=404)

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

# Contact form endpoint
@app.post("/contact")
async def send_contact_message(
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...)
):
    """
    Send contact form message via email
    """
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        import os
        
        # Email configuration
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        sender_email = os.getenv("SENDER_EMAIL", "noreply@hjbcodeforge.com")
        sender_password = os.getenv("SENDER_PASSWORD", "")
        recipient_email = os.getenv("RECIPIENT_EMAIL", "support@hjbcodeforge.com")
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"Contact Form Message from {name}"
        
        # Email body
        body = f"""
New contact form submission:

Name: {name}
Email: {email}

Message:
{message}

---
Sent from Background Remover API contact form
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Log the message for debugging
        logger.info(f"Contact form submission from {name} ({email}): {message}")
        
        # Check if email credentials are configured
        if not sender_password:
            logger.warning("Email credentials not configured - email functionality disabled")
            return JSONResponse(
                content={
                    "success": True,
                    "message": "Message received! We'll get back to you soon. (Email forwarding not configured)"
                },
                headers={
                    "Access-Control-Allow-Origin": "*"
                }
            )
        
        # Send email via SMTP
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully to {recipient_email}")
            
            return JSONResponse(
                content={
                    "success": True,
                    "message": "Message sent successfully! We'll get back to you as soon as possible."
                },
                headers={
                    "Access-Control-Allow-Origin": "*"
                }
            )
            
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed - check email credentials")
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Email service temporarily unavailable. Please email us directly at support@hjbcodeforge.com"
                },
                status_code=503,
                headers={
                    "Access-Control-Allow-Origin": "*"
                }
            )
        except smtplib.SMTPException as smtp_error:
            logger.error(f"SMTP error: {smtp_error}")
            return JSONResponse(
                content={
                    "success": False,
                    "message": "Failed to send message. Please try again or email us directly at support@hjbcodeforge.com"
                },
                status_code=500,
                headers={
                    "Access-Control-Allow-Origin": "*"
                }
            )
        
    except Exception as e:
        logger.error(f"Contact form error: {e}")
        return JSONResponse(
            content={
                "success": False,
                "message": "Failed to send message. Please try again or email us directly."
            },
            status_code=500,
            headers={
                "Access-Control-Allow-Origin": "*"
            }
        )

# Email configuration test endpoint
@app.get("/email-config-test")
async def email_config_test():
    """Test endpoint to check email configuration"""
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    sender_email = os.getenv("SENDER_EMAIL", "noreply@hjbcodeforge.com")
    sender_password = os.getenv("SENDER_PASSWORD", "")
    recipient_email = os.getenv("RECIPIENT_EMAIL", "support@hjbcodeforge.com")
    
    config_status = {
        "smtp_server": smtp_server,
        "smtp_port": smtp_port,
        "sender_email": sender_email,
        "sender_password_configured": bool(sender_password),
        "recipient_email": recipient_email,
        "email_functionality": "enabled" if sender_password else "disabled - no password configured"
    }
    
    return JSONResponse(content=config_status)

# Debug email sending endpoint
@app.post("/debug-email")
async def debug_email_sending():
    """Debug endpoint to test email sending with detailed logging"""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        # Get configuration
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        sender_email = os.getenv("SENDER_EMAIL", "noreply@hjbcodeforge.com")
        sender_password = os.getenv("SENDER_PASSWORD", "")
        recipient_email = os.getenv("RECIPIENT_EMAIL", "support@hjbcodeforge.com")
        
        logger.info(f"Debug email test - SMTP: {smtp_server}:{smtp_port}")
        logger.info(f"Debug email test - Sender: {sender_email}")
        logger.info(f"Debug email test - Recipient: {recipient_email}")
        logger.info(f"Debug email test - Password configured: {bool(sender_password)}")
        
        # Create test message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = "DEBUG: Email Test from Background Remover API"
        
        body = f"""
This is a DEBUG email test.

Configuration:
- SMTP Server: {smtp_server}:{smtp_port}
- Sender Email: {sender_email}
- Recipient Email: {recipient_email}
- Password Length: {len(sender_password) if sender_password else 0} characters

If you receive this email, the configuration is working correctly.
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Try to send
        logger.info("Debug email test - Attempting SMTP connection...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        
        logger.info("Debug email test - Starting TLS...")
        server.starttls()
        
        logger.info("Debug email test - Attempting login...")
        server.login(sender_email, sender_password)
        
        logger.info("Debug email test - Sending message...")
        server.send_message(msg)
        
        logger.info("Debug email test - Closing connection...")
        server.quit()
        
        logger.info("Debug email test - SUCCESS!")
        
        return JSONResponse(
            content={
                "success": True,
                "message": "Debug email sent successfully!",
                "config": {
                    "smtp_server": smtp_server,
                    "smtp_port": smtp_port,
                    "sender_email": sender_email,
                    "recipient_email": recipient_email,
                    "password_length": len(sender_password) if sender_password else 0
                }
            }
        )
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"Debug email test - SMTP Authentication Error: {e}")
        return JSONResponse(
            content={
                "success": False,
                "error": "SMTP Authentication Error",
                "details": str(e),
                "likely_cause": "Wrong Gmail address or App Password"
            },
            status_code=500
        )
    except smtplib.SMTPException as e:
        logger.error(f"Debug email test - SMTP Error: {e}")
        return JSONResponse(
            content={
                "success": False,
                "error": "SMTP Error",
                "details": str(e)
            },
            status_code=500
        )
    except Exception as e:
        logger.error(f"Debug email test - General Error: {e}")
        return JSONResponse(
            content={
                "success": False,
                "error": "General Error",
                "details": str(e)
            },
            status_code=500
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
