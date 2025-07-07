from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db, APIKey
from datetime import datetime

security = HTTPBearer()

def validate_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> APIKey:
    """
    Validate API key from Authorization header
    """
    api_key = credentials.credentials
    
    # Query the database for the API key
    db_api_key = db.query(APIKey).filter(APIKey.key == api_key).first()
    
    if not db_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    if db_api_key.is_active != "true":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is inactive"
        )
    
    # Update last used timestamp and usage count
    db_api_key.last_used = datetime.utcnow()
    db_api_key.usage_count += 1
    db.commit()
    
    return db_api_key
