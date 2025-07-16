# Railway Email Configuration Setup

## Current Status
✅ Code is working correctly  
❌ Email credentials not configured in Railway  
📧 Response: "Message received! We'll get back to you soon. (Email forwarding not configured)"

## Quick Fix - Set Railway Environment Variables

### 1. Go to Railway Dashboard
- Visit https://railway.app/dashboard
- Select your `bg-remover-api` project
- Go to the "Variables" tab

### 2. Add These Environment Variables

#### For Gmail (Recommended):
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-gmail@gmail.com
SENDER_PASSWORD=your-app-password
RECIPIENT_EMAIL=support@hjbcodeforge.com
```

#### For SendGrid (Production Alternative):
```
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SENDER_EMAIL=apikey
SENDER_PASSWORD=your-sendgrid-api-key
RECIPIENT_EMAIL=support@hjbcodeforge.com
```

### 3. Gmail App Password Setup
1. Go to https://myaccount.google.com/
2. Security → 2-Step Verification → App passwords
3. Select "Mail" and your device
4. Copy the 16-character password
5. Use this as `SENDER_PASSWORD` in Railway

### 4. After Adding Variables
- Railway will automatically redeploy
- Test the contact form again
- Check Railway logs for any SMTP errors

## Testing Command
```bash
curl -X POST https://web-production-faaf.up.railway.app/contact \
  -F "name=Test User" \
  -F "email=test@example.com" \
  -F "message=This is a test message"
```

Expected response after setup:
```json
{"success":true,"message":"Message sent successfully! We'll get back to you as soon as possible."}
```

## Common Issues
- **Gmail 2FA not enabled** → Enable 2-Step Verification first
- **Regular password used** → Must use App Password, not regular password
- **Wrong email format** → Use full Gmail address (user@gmail.com)
- **Typos in variables** → Double-check all variable names match exactly

## Alternative: Quick Test with Your Gmail
If you want to test immediately:
1. Use your personal Gmail credentials temporarily
2. Set `RECIPIENT_EMAIL=your-personal-email@gmail.com`
3. Test the contact form
4. Switch to support@hjbcodeforge.com later
