# Email Configuration Setup Guide

## Current Issue
The contact form shows "Message sent successfully!" but emails are not actually being sent because the email credentials are not configured.

## Setup for Gmail (Recommended)

### 1. Enable 2-Factor Authentication
- Go to your Google Account settings
- Enable 2-Factor Authentication if not already enabled

### 2. Generate App Password
- Go to Google Account > Security > 2-Step Verification
- At the bottom, click "App passwords"
- Select "Mail" and your device
- Copy the generated 16-character password

### 3. Configure Environment Variables

#### For Local Development:
Update the `.env` file with your credentials:
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-gmail@gmail.com
SENDER_PASSWORD=your-16-char-app-password
RECIPIENT_EMAIL=support@hjbcodeforge.com
```

#### For Railway Production:
Set these as environment variables in Railway dashboard:
- `SMTP_SERVER=smtp.gmail.com`
- `SMTP_PORT=587`
- `SENDER_EMAIL=your-gmail@gmail.com`
- `SENDER_PASSWORD=your-16-char-app-password`
- `RECIPIENT_EMAIL=support@hjbcodeforge.com`

## Alternative Email Providers

### SendGrid
```
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SENDER_EMAIL=apikey
SENDER_PASSWORD=your-sendgrid-api-key
```

### Mailgun
```
SMTP_SERVER=smtp.mailgun.org
SMTP_PORT=587
SENDER_EMAIL=postmaster@yourdomain.mailgun.org
SENDER_PASSWORD=your-mailgun-password
```

## Testing
After configuration, the contact form will:
1. Send actual emails if credentials are configured
2. Show appropriate error messages if credentials are missing
3. Log all attempts for debugging

## Security Notes
- Never commit the `.env` file to version control
- Use environment variables in production
- The `.env` file is excluded from Docker builds for security
