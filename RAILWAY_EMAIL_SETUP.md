# Railway Email Setup Deprecated

**Note:** Railway email configuration is no longer supported for this project. Please use AWS or another recommended platform for deployment and email setup.

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
