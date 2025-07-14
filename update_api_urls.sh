#!/bin/bash

# Update API URLs for Railway deployment
# Usage: ./update_api_urls.sh https://your-app-name.railway.app

if [ $# -eq 0 ]; then
    echo "Usage: $0 <new-api-url>"
    echo "Example: $0 https://bg-remover-api.railway.app"
    exit 1
fi

NEW_URL=$1

# Remove trailing slash if present
NEW_URL=${NEW_URL%/}

echo "Updating API URLs to: $NEW_URL"

# Update index.html
sed -i.bak "s|https://web-production-faaf.up.railway.app|$NEW_URL|g" index.html
echo "✅ Updated index.html"

# Update apiindex.html
sed -i.bak "s|https://bg-remover-api-052i.onrender.com|$NEW_URL|g" apiindex.html
echo "✅ Updated apiindex.html"

# Update api-status.html
sed -i.bak "s|https://bg-remover-api-052i.onrender.com|$NEW_URL|g" api-status.html
echo "✅ Updated api-status.html"

# Update main.py CORS settings
sed -i.bak "s|https://bg-remover-api-052i.onrender.com|$NEW_URL|g" main.py
echo "✅ Updated main.py CORS settings"

echo ""
echo "🎉 All files updated successfully!"
echo "📝 Backup files created with .bak extension"
echo "🚀 Ready to commit and deploy!"
echo ""
echo "Next steps:"
echo "1. Test the changes: python3 main.py"
echo "2. Commit: git add -A && git commit -m 'Update API URLs for Railway'"
echo "3. Push: git push"
