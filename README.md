# Background Remover API

🎨 A powerful REST API for removing backgrounds from images with AI-powered precision.

## 🌐 Live Demo (No API Key Needed)

- Open the homepage (`index.html`) and try the built-in demo. Upload an image and process it with no API key and no limits.

## ✨ Features

- 🖼️ AI Background Removal: Advanced background removal using state-of-the-art models
- 🚀 Fast Processing: Efficient image processing optimized for production
-  Easy Integration: Simple REST API
- 🎯 Multiple Formats: Support for JPEG, PNG, WebP, BMP, and TIFF
- 💻 Web Interface: User-friendly demo interface included
- 🧪 Demo Mode: No API key required, no limits

## 🚀 Quick Start

### Using the Demo

1. Open the app in your browser
2. Go to “Try Background Removal”
3. Upload an image and click “Remove Background”

### API Usage (Demo Mode)
# Background Remover API

AI-powered image background removal with a built-in web demo.

## Features

- No sign-in or API key required
- 5MB max upload size per image
- Model hint and alpha matting options
- Returns PNG (binary) or JSON with base64 image and processing metadata
- Demo UI included on the homepage

## Run locally

1) Install dependencies
```zsh
pip install -r requirements.txt
```

2) Start the server
```zsh
python main.py
# or
uvicorn main:app --reload --port 8000
```

3) Open the homepage in your browser and use “Try Background Removal”

## API

### POST /remove-background
Removes the background from an uploaded image.

Request (multipart/form-data):
- `file`: image file (<= 5MB)
- `model_hint`: one of `human` | `object` | `general` (default `general`)
- `alpha_matting`: boolean (default `true`)
- `alpha_matting_foreground_threshold`: integer 0–255 (default `240`)
- `alpha_matting_background_threshold`: integer 0–255 (default `10`)
- `alpha_matting_erode_structure_size`: integer 1–20 (default `10`)
- `alpha_matting_base_size`: integer 500–2000 (default `1000`)
- `return_json`: boolean (default `false`)

Responses:
- Binary PNG (default)
- JSON when `return_json=true`:
```json
{
  "image": "<base64 PNG>",
  "metadata": {
    "model_used": "u2netp",
    "processing_time": 2.34,
    "alpha_matting_enabled": true,
    "alpha_matting_used": false,
    "device": "cpu",
    "input_size": [width, height],
    "output_size": [width, height]
  }
}
```

Example usage:
```zsh
# Binary response (saved to processed.png)
curl -X POST http://localhost:8000/remove-background \
  -F file=@your_image.jpg \
  --output processed.png

# JSON response (base64 image + metadata)
curl -X POST http://localhost:8000/remove-background \
  -F file=@your_image.jpg \
  -F return_json=true
```

### GET /health
Basic health status and model availability.

## Notes

- Client-side and server-side validations enforce the 5MB image size limit.
- For production use, you can enable rate limits or add authentication if needed.

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

## 🔒 Security (Production)

- For demos, API keys are disabled and no limits are enforced.
- For production, re-enable API key validation and usage controls.

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
