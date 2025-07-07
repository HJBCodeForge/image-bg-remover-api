#!/bin/bash

echo "🔧 Background Remover API - Deployment Configuration"
echo "=================================================="

# Get user inputs
read -p "Enter your GitHub username: " GITHUB_USERNAME
read -p "Enter your GitHub repository name: " REPO_NAME
read -p "Enter your Render app name (or press Enter to skip): " RENDER_APP_NAME

# Update demo.html with the correct API URL
if [ ! -z "$RENDER_APP_NAME" ]; then
    echo "📝 Updating demo.html with Render URL..."
    sed -i.bak "s|https://your-api-name.onrender.com|https://${RENDER_APP_NAME}.onrender.com|g" demo.html
    echo "✅ Updated API URL to: https://${RENDER_APP_NAME}.onrender.com"
fi

# Create a custom demo.html for GitHub Pages
cat > index.html << EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Background Remover API - Demo</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            margin: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .container {
            max-width: 800px;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
            margin: 20px 0;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        .content {
            padding: 40px 30px;
            text-align: center;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin: 10px;
            transition: transform 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
        }
        .api-info {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            text-align: left;
        }
        code {
            background: #e9ecef;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎨 Background Remover API</h1>
            <p>AI-powered background removal with RESTful API</p>
        </div>
        <div class="content">
            <h2>🚀 Live Demo & Documentation</h2>
            <p>Click the buttons below to access the interactive demo and API documentation:</p>
            
            <a href="demo.html" class="btn">🎨 Try Live Demo</a>
            <a href="https://${RENDER_APP_NAME}.onrender.com/docs" class="btn" target="_blank">📖 API Documentation</a>
            
            <div class="api-info">
                <h3>📡 API Endpoints</h3>
                <p><strong>Base URL:</strong> <code>https://${RENDER_APP_NAME}.onrender.com</code></p>
                <p><strong>Generate API Key:</strong> <code>POST /api-keys</code></p>
                <p><strong>Remove Background:</strong> <code>POST /remove-background</code></p>
                <p><strong>Health Check:</strong> <code>GET /health</code></p>
            </div>
            
            <div class="api-info">
                <h3>🔧 Quick Start</h3>
                <p>1. <a href="demo.html">Open the demo</a> to generate an API key</p>
                <p>2. Upload an image to test background removal</p>
                <p>3. Integrate the API into your applications using the key</p>
            </div>
            
            <div class="api-info">
                <h3>📚 Features</h3>
                <ul>
                    <li>✅ AI-powered background removal</li>
                    <li>✅ RESTful API with authentication</li>
                    <li>✅ Support for JPEG, PNG, WebP, BMP, TIFF</li>
                    <li>✅ JSON and binary response formats</li>
                    <li>✅ Usage tracking and API key management</li>
                </ul>
            </div>
        </div>
    </div>
</body>
</html>
EOF

echo "✅ Created index.html for GitHub Pages"
echo ""
echo "🎯 Next Steps:"
echo "==============="
echo ""
echo "📦 1. Deploy API to Render:"
echo "   - Go to https://render.com"
echo "   - Connect your GitHub repository"
echo "   - Choose 'Web Service'"
echo "   - Set build command: 'pip install -r requirements.txt'"
echo "   - Set start command: 'python main.py'"
echo "   - Set environment variable PORT=8000"
echo ""
echo "🌐 2. Deploy Frontend to GitHub Pages:"
echo "   - Push this repository to GitHub"
echo "   - Go to repository Settings > Pages"
echo "   - Choose 'Deploy from a branch'"
echo "   - Select 'main' branch"
echo "   - Your demo will be available at: https://${GITHUB_USERNAME}.github.io/${REPO_NAME}"
echo ""
echo "🔗 3. Update CORS settings in main.py with your actual domain"
echo ""
echo "🎉 Your Background Remover API will be live and ready to use!"
