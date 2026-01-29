"""
Email Testing & Debugging Tool

This script helps you test and debug email configuration.
It will show you exactly what's wrong if emails aren't sending.

USAGE:
    python test_email.py
    
    This will test your email configuration and show detailed error messages.

WHAT IT DOES:
    - Tests SMTP connection
    - Verifies credentials
    - Sends a test email
    - Shows detailed error messages if something fails

END GOAL:
    - Verify your email setup is working correctly
    - Debug why emails aren't being sent
    - Get clear error messages to fix issues
"""
import logging
import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def test_email_config():
    """Test email configuration and show detailed diagnostics."""
    print("\n" + "=" * 60)
    print("EMAIL CONFIGURATION TEST")
    print("=" * 60 + "\n")

    # Check environment variables
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = os.environ.get("SMTP_PORT", "587")
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASS")
    notify_to = os.environ.get("NOTIFY_TO")

    print("📋 Configuration Check:")
    print(f"   SMTP_HOST: {smtp_host or '❌ NOT SET'}")
    print(f"   SMTP_PORT: {smtp_port}")
    print(f"   SMTP_USER: {smtp_user or '❌ NOT SET'}")
    print(f"   SMTP_PASS: {'*' * len(smtp_pass) if smtp_pass else '❌ NOT SET'} ({len(smtp_pass) if smtp_pass else 0} chars)")
    print(f"   NOTIFY_TO: {notify_to or '❌ NOT SET'}")
    print()

    # Validate required fields
    if not all([smtp_host, smtp_user, smtp_pass, notify_to]):
        print("❌ ERROR: Missing required email configuration!")
        print("\nPlease set these in your .env file:")
        print("   SMTP_HOST=smtp.gmail.com")
        print("   SMTP_PORT=587")
        print("   SMTP_USER=your-email@gmail.com")
        print("   SMTP_PASS=your-app-password")
        print("   NOTIFY_TO=recipient@example.com")
        print("\nSee SETUP_EMAIL.md for detailed instructions.")
        return False

    # Check password length
    if len(smtp_pass) < 10:
        print("⚠️  WARNING: Password seems too short!")
        print(f"   Your password is {len(smtp_pass)} characters.")
        print("   Gmail App Passwords are usually 16 characters.")
        print("   Outlook/Yahoo App Passwords vary but are usually longer.")
        print("\n   Make sure you're using an APP PASSWORD, not your regular password!")
        print("   See SETUP_EMAIL.md for how to create one.")
        print()

    # Test SMTP connection
    print("🔌 Testing SMTP Connection...")
    try:
        smtp = smtplib.SMTP(smtp_host, int(smtp_port), timeout=10)
        print(f"   ✓ Connected to {smtp_host}:{smtp_port}")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        print("\n   Common issues:")
        print("   - Wrong SMTP_HOST (check provider)")
        print("   - Firewall blocking port")
        print("   - Wrong port number")
        return False

    # Test STARTTLS
    print("🔐 Testing STARTTLS...")
    try:
        smtp.starttls()
        print("   ✓ STARTTLS successful")
    except Exception as e:
        print(f"   ❌ STARTTLS failed: {e}")
        smtp.quit()
        return False

    # Test authentication
    print("🔑 Testing Authentication...")
    try:
        smtp.login(smtp_user, smtp_pass)
        print("   ✓ Authentication successful")
    except smtplib.SMTPAuthenticationError as e:
        print(f"   ❌ Authentication FAILED: {e}")
        print("\n   Common causes:")
        print("   - Wrong password (make sure it's an APP PASSWORD)")
        print("   - Password got truncated (check .env file)")
        print("   - 2FA not enabled on your account")
        print("   - App password not created correctly")
        print("\n   For Gmail:")
        print("   1. Enable 2FA: https://myaccount.google.com/security")
        print("   2. Create App Password: https://myaccount.google.com/apppasswords")
        print("   3. Copy the FULL 16-character password (no spaces)")
        smtp.quit()
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        smtp.quit()
        return False

    # Send test email
    print("📧 Sending Test Email...")
    try:
        msg = EmailMessage()
        msg["Subject"] = "Test Email - Book Generation System"
        msg["From"] = smtp_user
        msg["To"] = notify_to
        msg.set_content(
            f"""
This is a test email from the Book Generation System.

If you received this, your email configuration is working correctly!

Configuration:
- SMTP Host: {smtp_host}
- SMTP Port: {smtp_port}
- From: {smtp_user}
- To: {notify_to}

You can now receive notifications when books are generated.
"""
        )

        smtp.send_message(msg)
        print(f"   ✓ Test email sent successfully!")
        print(f"   ✓ Check inbox at: {notify_to}")
        smtp.quit()
        return True

    except Exception as e:
        print(f"   ❌ Failed to send email: {e}")
        smtp.quit()
        return False


if __name__ == "__main__":
    success = test_email_config()
    print("\n" + "=" * 60)
    if success:
        print("✅ EMAIL TEST PASSED - Everything is working!")
    else:
        print("❌ EMAIL TEST FAILED - Check errors above")
    print("=" * 60 + "\n")
