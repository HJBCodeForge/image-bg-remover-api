# Background Remover API

A powerful REST API for removing backgrounds from images with API key authentication.

## Features

- 🔑 **API Key Management**: Generate and manage API keys for secure access
- 🖼️ **Background Removal**: Advanced AI-powered background removal using the rembg library
- 📊 **Usage Tracking**: Monitor API key usage and statistics
- 🚀 **Fast Processing**: Efficient image processing with PIL and rembg
- 🔒 **Secure**: Token-based authentication with usage tracking
- 📦 **Easy Integration**: RESTful API that can be easily integrated into any application

## Quick Start

### Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables (optional):
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

4. Run the API:
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

### API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation.

## API Endpoints

### 1. Generate API Key
```http
POST /api-keys
Content-Type: application/json

{
  "name": "My App API Key"
}
```

**Response:**
```json
{
  "id": 1,
  "key": "bgr_abc123...",
  "name": "My App API Key",
  "created_at": "2025-07-07T10:00:00Z",
  "last_used": null,
  "usage_count": 0,
  "is_active": true
}
```

### 2. Remove Background
```http
POST /remove-background
Authorization: Bearer bgr_abc123...
Content-Type: multipart/form-data

file: [image file]
return_json: false (optional, default: false)
```

**Response (Binary Image):**
- Returns a PNG image with transparent background
- Headers include processing time and API key info

**Response (JSON, when return_json=true):**
```json
{
  "success": true,
  "message": "Background removed successfully",
  "processed_image_url": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "processing_time": 2.34
}
```

### 3. List API Keys
```http
GET /api-keys
```

### 4. Deactivate API Key
```http
DELETE /api-keys/{api_key_id}
```

## Usage Examples

### Python Client Example
```python
import requests

# 1. Generate API key
response = requests.post("http://localhost:8000/api-keys", 
                        json={"name": "My App"})
api_key = response.json()["key"]

# 2. Remove background from image
with open("image.jpg", "rb") as f:
    files = {"file": f}
    headers = {"Authorization": f"Bearer {api_key}"}
    
    response = requests.post("http://localhost:8000/remove-background",
                           files=files, headers=headers)
    
    # Save processed image
    with open("processed_image.png", "wb") as output:
        output.write(response.content)
```

### JavaScript/Frontend Example
```javascript
// 1. Generate API key (do this once, server-side)
const apiKeyResponse = await fetch('/api-keys', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ name: 'Web App' })
});
const { key } = await apiKeyResponse.json();

// 2. Remove background from uploaded image
const formData = new FormData();
formData.append('file', imageFile);
formData.append('return_json', 'true');

const response = await fetch('/remove-background', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${key}` },
  body: formData
});

const result = await response.json();
// result.processed_image_url contains the base64 image data
```

### cURL Example
```bash
# 1. Generate API key
curl -X POST "http://localhost:8000/api-keys" \
     -H "Content-Type: application/json" \
     -d '{"name": "Test Key"}'

# 2. Remove background
curl -X POST "http://localhost:8000/remove-background" \
     -H "Authorization: Bearer bgr_your_api_key_here" \
     -F "file=@image.jpg" \
     --output processed_image.png
```

## Configuration

### Environment Variables

- `SECRET_KEY`: Secret key for security (change in production)
- `DATABASE_URL`: Database connection string (default: SQLite)
- `API_HOST`: Host to bind the API (default: 0.0.0.0)
- `API_PORT`: Port to run the API (default: 8000)

### Database

The API uses SQLite by default, but can be configured to use PostgreSQL or MySQL by changing the `DATABASE_URL` in the `.env` file.

## Deployment

### Docker (Recommended)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

### Production Considerations

1. Change the `SECRET_KEY` in production
2. Use a proper database (PostgreSQL/MySQL) instead of SQLite
3. Configure CORS origins properly
4. Use a reverse proxy (nginx) for SSL termination
5. Monitor API usage and implement rate limiting if needed

## Supported Image Formats

- JPEG/JPG
- PNG
- WebP
- BMP
- TIFF

## Output Format

All processed images are returned as PNG files with transparent backgrounds.

## Error Handling

The API returns detailed error messages in JSON format:

```json
{
  "success": false,
  "error": "Invalid image file",
  "details": "Please upload a valid image file (JPEG, PNG, etc.)"
}
```

## License

This project is open source and available under the MIT License.
