# Dependency Update Summary

## Date: July 24, 2025

### Updates Applied

1. **FastAPI Lifecycle Management**
   - Replaced deprecated `@app.on_event("startup")` with modern `lifespan` context manager
   - Moved startup logic into the lifespan handler for better resource management

2. **DateTime Handling**
   - Updated all `datetime.utcnow()` calls to `datetime.now(timezone.utc)` 
   - `datetime.utcnow()` is deprecated and will be removed in future Python versions
   - Now using timezone-aware datetime objects throughout the application

3. **Package Version Updates in requirements.txt**
   - `fastapi>=0.116.1` (was 0.104.1)
   - `uvicorn>=0.35.0` (was 0.24.0)
   - `python-multipart>=0.0.9` (was 0.0.6)
   - `pillow>=11.0.0` (was 10.0.1)
   - `pydantic>=2.11.7` (was 2.5.0)
   - `numpy>=1.26.4,<2.0` (pinned to 1.x for compatibility)

4. **NumPy Compatibility**
   - Downgraded from numpy 2.3.1 to 1.26.4 to maintain compatibility with:
     - scikit-image
     - pandas
     - matplotlib
     - other scientific packages that don't yet support numpy 2.x

5. **SQLAlchemy DateTime Defaults**
   - Updated datetime column defaults to use lambda functions with timezone-aware datetime
   - Changed from `default=datetime.utcnow` to `default=lambda: datetime.now(timezone.utc)`

### Files Modified
- `/main.py` - Updated imports, lifespan handler, and datetime calls
- `/auth.py` - Updated datetime imports and usage
- `/database.py` - Updated datetime imports and column defaults
- `/requirements.txt` - Updated package versions

### Testing
- Backend server starts successfully on localhost:8000
- API endpoints respond correctly
- All dependencies load without errors
- Full functionality mode enabled

### Notes
- The numpy 2.x incompatibility warnings with some packages are expected
- These packages will be updated to support numpy 2.x in future releases
- For now, numpy 1.26.4 provides the best compatibility across all dependencies
