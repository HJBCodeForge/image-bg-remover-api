import os
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from jwt.exceptions import DecodeError, ExpiredSignatureError, InvalidTokenError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db, APIKey, User
import logging
import secrets
import string
import bcrypt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days

security = HTTPBearer()

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        logger.error(f"Password verification failed: {e}")
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.info(f"Created access token: {encoded_jwt[:10]}...")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Token creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create access token"
        )

def verify_token(token: str) -> dict:
    """Verify JWT token and return payload"""
    try:
        logger.info(f"Verifying token: {token[:10]}...")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info("Token verified successfully")
        return payload
    except ExpiredSignatureError:
        logger.error("Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (DecodeError, InvalidTokenError) as e:
        logger.error(f"Token validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    """Get current authenticated user"""
    logger.info("Getting current user from token")
    token = credentials.credentials
    logger.info(f"Token from credentials: {token[:10]}...")
    
    payload = verify_token(token)
    user_id: int = payload.get("sub")
    
    if user_id is None:
        logger.error("No user ID in token payload")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"Looking up user with ID: {user_id}")
    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        logger.error(f"User not found or inactive: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"Found user: {user.email}")
    return user

def get_optional_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> Optional[User]:
    """Get current user if authenticated, otherwise return None"""
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None

def validate_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> APIKey:
    """
    Validate API key from Authorization header
    """
    api_key = credentials.credentials
    logger.info(f"Validating API key: {api_key[:10]}...")
    
    # Query the database for the API key
    db_api_key = db.query(APIKey).filter(APIKey.key == api_key).first()
    
    if not db_api_key:
        logger.error("Invalid API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    if not db_api_key.is_active:
        logger.error("API key is inactive")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is inactive"
        )
    
    # Update last used timestamp and usage count
    db_api_key.last_used = datetime.now(timezone.utc)
    db_api_key.usage_count += 1
    db.commit()
    
    logger.info("API key validated successfully")
    return db_api_key

def validate_api_key_string(api_key: str, db: Session) -> bool:
    """
    Validate API key from string (for form data)
    """
    logger.info(f"Validating API key string: {api_key[:10]}...")
    
    # Query the database for the API key
    db_api_key = db.query(APIKey).filter(APIKey.key == api_key).first()
    
    if not db_api_key:
        logger.error("Invalid API key string")
        return False
    
    if not db_api_key.is_active:
        logger.error("API key string is inactive")
        return False
    
    # Update last used timestamp and usage count
    db_api_key.last_used = datetime.now(timezone.utc)
    db_api_key.usage_count += 1
    db.commit()
    
    logger.info("API key string validated successfully")
    return True

def generate_api_key() -> str:
    """Generate a new API key"""
    # Use a combination of letters and numbers
    alphabet = string.ascii_letters + string.digits
    # Generate a random string of 32 characters
    key = ''.join(secrets.choice(alphabet) for _ in range(32))
    # Add prefix for identification
    return f"bgr_{key}"
