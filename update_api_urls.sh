#!/bin/bash

# Script to update API URLs for Render deployment
# Usage: ./update_api_urls.sh https://bg-remover-frontend-vfhc.onrender.com

if [ $# -eq 0 ]; then
    echo "Usage: $0 <API_URL>"
    echo "Example: $0 https://bg-remover-frontend-vfhc.onrender.com.com"
    exit 1
fi

API_URL=$1

echo "Updating API URLs to: $API_URL"

# Update demo.html
sed -i.bak "s|https://bg-remover-frontend-vfhc.onrender.com|$API_URL|g" demo.html
sed -i.bak "s|'http://localhost:8000'|'$API_URL'|g" demo.html

# Update index.html
sed -i.bak "s|https://bg-remover-frontend-vfhc.onrender.com|$API_URL|g" index.html
sed -i.bak "s|'http://localhost:8000'|'$API_URL'|g" index.html

# Update api-status.html
sed -i.bak "s|https://bg-remover-frontend-vfhc.onrender.com|$API_URL|g" api-status.html
sed -i.bak "s|'http://localhost:8000'|'$API_URL'|g" api-status.html

echo "✅ API URLs updated successfully!"
echo "Files updated:"
echo "  - demo.html"
echo "  - index.html"
echo "  - api-status.html"
echo ""
echo "Next steps:"
echo "1. git add ."
echo "2. git commit -m 'Update API URLs for Render deployment'"
echo "3. git push origin main"
echo ""
echo "Backup files created with .bak extension"
