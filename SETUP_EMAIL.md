# Free Email Setup Guide

## Quick Setup for Free Email Providers

### Option 1: Gmail (Recommended - Easiest)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Create App Password:**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Enter "Book System" → Generate
   - Copy the 16-character password (no spaces)

3. **Add to `.env`:**
   ```env
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASS=your-16-char-app-password
   NOTIFY_TO=editor@example.com
   ```

**Note:** Use the **App Password**, NOT your regular Gmail password!

---

### Option 2: Outlook/Hotmail (Free)

1. **Enable 2-Factor Authentication**
2. **Create App Password:**
   - Go to: https://account.microsoft.com/security
   - Advanced security options → App passwords
   - Create new app password → Copy it

3. **Add to `.env`:**
   ```env
   SMTP_HOST=smtp-mail.outlook.com
   SMTP_PORT=587
   SMTP_USER=your-email@outlook.com
   SMTP_PASS=your-app-password
   NOTIFY_TO=editor@example.com
   ```

---

### Option 3: Yahoo Mail (Free)

1. **Enable 2-Factor Authentication**
2. **Generate App Password:**
   - Account Security → Generate app password
   - Copy the password

3. **Add to `.env`:**
   ```env
   SMTP_HOST=smtp.mail.yahoo.com
   SMTP_PORT=587
   SMTP_USER=your-email@yahoo.com
   SMTP_PASS=your-app-password
   NOTIFY_TO=editor@example.com
   ```

---

## Test Email

After setup, test with:
```python
python -c "from src.notifications.email import send_email; send_email('Test', 'Hello!')"
```

You should receive an email at `NOTIFY_TO` address.

---

## Troubleshooting

**"Authentication failed":**
- Make sure you're using **App Password**, not regular password
- Check 2FA is enabled

**"Connection refused":**
- Check firewall/antivirus isn't blocking port 587
- Try port 465 with SSL instead of STARTTLS

**"Email not sending":**
- Check logs for error messages
- Verify all env vars are set correctly
- Test SMTP settings with an email client first
