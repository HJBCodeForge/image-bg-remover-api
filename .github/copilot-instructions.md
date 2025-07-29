# Copilot Instructions for Background Remover API

## Project Architecture
- **Backend:** FastAPI (Python) REST API in root directory (`main.py`, `auth.py`, `database.py`, `models.py`, etc.)
- **Frontend:** Static HTML/CSS/JS in `/assets` (main entry: `index.html`, `dashboard.html`, JS: `auth.js`, CSS: `landing.css`)
- **Database:** SQLite (`bg_remover.db`) for user, API key, and usage tracking
- **Background Removal Engine:** Uses `rembg` and ONNX for AI-powered image processing
- **API Key Management:** Endpoints for key generation, listing, and deactivation; keys stored in DB
- **User Authentication:** JWT-based login, registration, and session management

## Developer Workflows
- **Run Locally:**
  - `python main.py` (serves API at http://localhost:8000)
  - Frontend is static; open `index.html` in browser or serve via backend
- **Install Dependencies:**
  - `pip install -r requirements.txt` (root)
- **Database:**
  - SQLite DB auto-creates tables on startup
  - Test users/API keys can be added via API or direct DB manipulation
- **Testing:**
  - Minimal tests in `test_improvements.py` (run with `python test_improvements.py`)
- **BackgroundRemover Engine:**
  - Standalone CLI in `/backgroundremover-main` (see its README for advanced usage)

## Key Patterns & Conventions
- **API Authentication:** All endpoints except key generation require `Authorization: Bearer <API_KEY>`
- **Frontend Auth Flow:**
  - Login/register via modal (see `auth.js`)
  - Redirect logic: dashboard only accessible when logged in (localStorage `authToken`)
- **Error Handling:**
  - Backend: robust null checks, clear error messages
  - Frontend: null checks for DOM elements, user-friendly error display
- **Deployment:**
  - Render.com config in `render.yaml`, Vercel config in `vercel.json`, Docker support
- **Image Formats:**
  - Input: JPEG, PNG, WebP, BMP, TIFF
  - Output: PNG (base64 or file)

## Integration Points
- **rembg/ONNX:** Used for image background removal (see `background_remover.py`)
- **Frontend/Backend:** Communicate via REST endpoints; API keys and JWT tokens passed in headers
- **External:** Optionally integrates with SendGrid for email (see `SENDGRID_SETUP.md`)

## Examples
- **Generate API Key:**
  ```bash
  curl -X POST "http://localhost:8000/api-keys" -H "Content-Type: application/json" -d '{"name": "My App"}'
  ```
- **Remove Background:**
  ```bash
  curl -X POST "http://localhost:8000/remove-background?return_json=true" -H "Authorization: Bearer <API_KEY>" -F "file=@your_image.jpg"
  ```

## Key Files & Directories
- `main.py`, `auth.py`, `database.py`, `models.py`: Backend API, auth, DB models
- `assets/js/auth.js`, `assets/css/landing.css`: Frontend logic and styles
- `backgroundremover-main/`: Standalone CLI and engine for background removal
- `bg_remover.db`: SQLite database
- `render.yaml`, `vercel.json`, `Dockerfile`: Deployment configs

---

For advanced engine usage, see `/backgroundremover-main/README.md`. For deployment, see `DEPLOYMENT_SUCCESS.md`. For API docs, visit `/docs` when running locally.
