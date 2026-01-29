import logging
import os
import smtplib
from email.message import EmailMessage

logger = logging.getLogger(__name__)

SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASS = os.environ.get("SMTP_PASS")
NOTIFY_TO = os.environ.get("NOTIFY_TO")


def send_email(subject: str, body: str) -> None:
    """
    SMTP email sender with support for free email providers.
    
    Free options:
    - Gmail: Use App Password (not regular password)
    - Outlook/Hotmail: Use App Password
    - Yahoo: Use App Password
    
    If SMTP_* env vars are not set, this is a no-op.
    """
    if not (SMTP_HOST and SMTP_USER and SMTP_PASS and NOTIFY_TO):
        logger.debug("Email not configured - skipping")
        return

    # Clean password (remove quotes/spaces that might have been added)
    password_clean = SMTP_PASS.strip().strip('"').strip("'")
    
    # Log password length for debugging (without showing actual password)
    logger.debug(f"Email config: {SMTP_USER} -> {NOTIFY_TO} (password length: {len(password_clean)})")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = NOTIFY_TO
    msg.set_content(body)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, password_clean)
            smtp.send_message(msg)
            logger.info(f"✓ Email sent to {NOTIFY_TO}")
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"✗ Email authentication failed: {e}")
        logger.error("   Check: Is your password an APP PASSWORD? (not regular password)")
        logger.error(f"   Password length: {len(password_clean)} chars (should be 16 for Gmail)")
        logger.error("   Run 'python test_email.py' for detailed diagnostics")
    except Exception as e:
        logger.error(f"✗ Failed to send email: {e}")
        logger.error("   Run 'python test_email.py' for detailed diagnostics")

