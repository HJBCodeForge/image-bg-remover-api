# Background Remover API

🎨 A powerful REST API for removing backgrounds from images with AI-powered precision.

## 🌐 Live Demo

- **Frontend:** https://bg-remover-frontend-vfhc.onrender.com
- **Backend API:** https://bg-remover-api-052i.onrender.com
- **API Documentation:** https://bg-remover-api-052i.onrender.com/docs

## ✨ Features

- 🔑 **API Key Management**: Generate and manage API keys for secure access
- 🖼️ **AI Background Removal**: Advanced background removal using rembg + ONNX
- 📊 **Usage Tracking**: Monitor API key usage and statistics
- 🚀 **Fast Processing**: Efficient image processing optimized for production
- 🔒 **Secure Authentication**: Token-based authentication with rate limiting
- 📦 **Easy Integration**: RESTful API with comprehensive documentation
- 🎯 **Multiple Formats**: Support for JPEG, PNG, WebP, BMP, and TIFF
- 💻 **Web Interface**: User-friendly demo interface included

## 🚀 Quick Start

### Using the Live API

1. **Visit the demo:** https://bg-remover-frontend-vfhc.onrender.com
2. **Generate an API key** using the web interface
3. **Upload an image** and test background removal
4. **Use the API** in your own applications

### API Usage

```bash
# Generate API key
curl -X POST "https://bg-remover-api-052i.onrender.com/api-keys" \
  -H "Content-Type: application/json" \
  -d '{"name": "My App"}'

# Remove background
curl -X POST "https://bg-remover-api-052i.onrender.com/remove-background?return_json=true" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@your_image.jpg"
```

## 🏃‍♂️ Local Development

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/HJBCodeForge/image-bg-remover-api.git
   cd image-bg-remover-api
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the API:
   ```bash
   python main.py
   ```

4. Visit: http://localhost:8000

## 📋 API Endpoints

### Authentication
All endpoints (except key generation) require an API key:
```
Authorization: Bearer YOUR_API_KEY
```

### Core Endpoints

- `POST /api-keys` - Generate new API key
- `GET /api-keys` - List all API keys
- `POST /remove-background` - Remove background from image
- `DELETE /api-keys/{id}` - Deactivate API key
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

### Background Removal

**Request:**
```bash
POST /remove-background?return_json=true
Content-Type: multipart/form-data
Authorization: Bearer YOUR_API_KEY

file: [image file]
```

**Response:**
```json
{
  "success": true,
  "message": "Background removed successfully",
  "processed_image_url": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "processing_time": 2.34
}
```

## 🛠️ Technical Details

### Built With
- **FastAPI** - Modern web framework for APIs
- **rembg** - AI background removal library
- **ONNX Runtime** - Optimized inference engine
- **SQLite** - Database for API key management
- **Pillow** - Image processing library

### Supported Formats
- **Input:** JPEG, PNG, WebP, BMP, TIFF
- **Output:** PNG with transparency

### Performance
- **Processing Time:** 1-5 seconds per image
- **File Size Limit:** 10MB per image
- **Concurrent Requests:** Supported

## 🔧 Configuration

### Environment Variables
- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 8000)
- `ENVIRONMENT` - Environment mode (development/production)

### Database
- Uses SQLite for simplicity and portability
- Automatic table creation on startup
- Persistent storage across restarts

## 🚀 Deployment

This project is deployed on Render.com with both backend and frontend services.

### Files
- `render.yaml` - Render deployment configuration
- `requirements.txt` - Python dependencies
- `main.py` - Application entry point

### Architecture
- **Backend:** Python web service
- **Frontend:** Static site service
- **Database:** SQLite (persistent across deployments)

## 📖 Documentation

- **API Docs:** https://bg-remover-api-052i.onrender.com/docs
- **Deployment Guide:** See `DEPLOYMENT_SUCCESS.md`
- **Live Demo:** https://bg-remover-frontend-vfhc.onrender.com

## 🔒 Security

- API key authentication required
- Rate limiting and usage tracking
- Input validation and sanitization
- CORS protection configured
- Secure error handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📜 License

This project is open source and available under the MIT License.

## 🆘 Support

- Check the [API documentation](https://bg-remover-api-052i.onrender.com/docs)
- Try the [live demo](https://bg-remover-frontend-vfhc.onrender.com)
- Review the deployment guide in `DEPLOYMENT_SUCCESS.md`

---

**🎉 Ready to remove backgrounds? Try the live demo now!**

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
