# Gmail App Password Troubleshooting Guide

## Can't Find App Passwords? Here's How to Fix It

### Step 1: Enable 2-Step Verification First
The App passwords option only appears AFTER 2-Step Verification is enabled.

1. Go to https://myaccount.google.com/
2. Click **Security** (left sidebar)
3. Look for **"2-Step Verification"** section
4. Click **"2-Step Verification"** 
5. Follow the setup process (phone verification, etc.)
6. **Complete the entire 2-Step setup** before proceeding

### Step 2: Find App Passwords (After 2-Step is Complete)
1. Go back to https://myaccount.google.com/security
2. Click **"2-Step Verification"** again
3. Scroll down to the bottom of the page
4. Look for **"App passwords"** section
5. Click **"App passwords"**

### Alternative Path to App Passwords
If you still can't find it, try this direct link:
https://myaccount.google.com/apppasswords

### Step 3: Generate App Password
1. Select **"Mail"** from the dropdown
2. Select your device/computer
3. Click **"Generate"**
4. Copy the 16-character password (format: `abcd efgh ijkl mnop`)
5. **Use this password** in Railway, not your regular Gmail password

## Alternative Solutions

### Option 1: Use a Different Gmail Account
If your main Gmail account has issues:
1. Create a new Gmail account specifically for this service
2. Enable 2-Step Verification on the new account
3. Generate App password for the new account
4. Use the new account credentials

### Option 2: Use SendGrid (Recommended for Production)
SendGrid is more reliable for automated emails:

1. Sign up at https://sendgrid.com/ (free tier available)
2. Create an API key
3. Use these Railway environment variables:
```
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SENDER_EMAIL=apikey
SENDER_PASSWORD=your-sendgrid-api-key
RECIPIENT_EMAIL=support@hjbcodeforge.com
```

### Option 3: Use Outlook/Hotmail
If Gmail is giving you trouble:

1. Create a Microsoft account at https://outlook.com/
2. Go to https://account.microsoft.com/security
3. Enable 2-Step Verification
4. Generate App password
5. Use these Railway environment variables:
```
SMTP_SERVER=smtp.live.com
SMTP_PORT=587
SENDER_EMAIL=your-outlook@outlook.com
SENDER_PASSWORD=your-app-password
RECIPIENT_EMAIL=support@hjbcodeforge.com
```

## Common Issues

### "App passwords" Not Showing
- ❌ 2-Step Verification not fully completed
- ❌ Using Google Workspace account (different process)
- ❌ Account security restrictions

### "App passwords" Grayed Out
- ❌ Less secure app access enabled (disable it)
- ❌ Google Workspace admin restrictions

### Account Type Issues
- **Personal Gmail**: Should work with above steps
- **Google Workspace**: Admin needs to enable App passwords
- **School/Work Account**: May have restrictions

## Quick Test Commands

After setting up any email provider, test with:

```bash
# Check configuration
curl -s https://web-production-faaf.up.railway.app/email-config-test

# Test contact form
curl -X POST https://web-production-faaf.up.railway.app/contact \
  -F "name=Test User" \
  -F "email=test@example.com" \
  -F "message=This is a test message"
```

## Need Help?
If you're still having trouble, let me know:
1. What you see in your Google Security settings
2. What type of Google account you're using
3. Whether you'd prefer to try SendGrid instead

The important thing is getting email working - we can use any reliable email provider!
