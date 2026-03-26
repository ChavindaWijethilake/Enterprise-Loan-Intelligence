# =============================================================================
# mail_service/email_sender.py
# =============================================================================
# PURPOSE: Send decision emails to loan applicants using SMTP (e.g., Gmail).
#
# HOW IT WORKS:
#   1. Reads MAIL_USERNAME and MAIL_PASSWORD from .env
#   2. Connects to the SMTP server (default Gmail)
#   3. Sends email to the applicant
#
# REQUIRES:
#   - python-dotenv package
#   - MAIL_USERNAME in .env
#   - MAIL_PASSWORD in .env
# =============================================================================

import os
import smtplib
import datetime
from email.message import EmailMessage
import mimetypes
from dotenv import load_dotenv

from src.logger import get_logger
logger = get_logger("email_sender")

# ---------------------------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(BASE_DIR, "..")
ENV_PATH = os.path.join(PROJECT_DIR, ".env")

load_dotenv(ENV_PATH)


# ---------------------------------------------------------------------------
# Email Sending Function
# ---------------------------------------------------------------------------
def send_email(recipient_email: str, subject: str, body: str, attachment_path: str = None) -> bool:
    """
    Send email using standard SMTP.

    Args:
        recipient_email (str): recipient email address
        subject (str): email subject
        body (str): email body (HTML supported)
        attachment_path (str, optional): absolute path to a file to attach

    Returns:
        bool: True if sent successfully, False otherwise
    """
    
    mail_username = os.getenv("MAIL_USERNAME", "").strip()
    mail_password = os.getenv("MAIL_PASSWORD", "").strip()
    mail_server = os.getenv("MAIL_SERVER", "smtp.gmail.com").strip()
    mail_port = int(os.getenv("MAIL_PORT", "587"))
    mail_mode = os.getenv("MAIL_MODE", "SMTP").upper().strip()

    # Apply HTML Branded Template
    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eaeaea; border-radius: 10px;">
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="color: #0b5cff; margin: 0;">Enterprise Bank</h1>
            <p style="color: #666; margin: 5px 0;">Automated Loan Operations</p>
        </div>
        <hr style="border: 0; border-top: 1px solid #eaeaea; margin: 20px 0;">
        <div style="line-height: 1.6; font-size: 16px;">
            {body}
        </div>
        <hr style="border: 0; border-top: 1px solid #eaeaea; margin: 20px 0;">
        <div style="text-align: center; font-size: 12px; color: #999;">
            <p>This is an automated message. Please do not reply directly to this email.</p>
            <p>&copy; {datetime.datetime.now().year} Enterprise Bank. All rights reserved.</p>
        </div>
      </body>
    </html>
    """

    # -----------------------------------------------------------------------
    # SANDBOX MODE: Save to local file
    # -----------------------------------------------------------------------
    if mail_mode == "SANDBOX":
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"email_{timestamp}_{recipient_email.replace('@', '_at_')}.html"
        
        # Ensure directory exists
        intercept_dir = os.path.join(BASE_DIR, "intercepted_emails")
        if not os.path.exists(intercept_dir):
            os.makedirs(intercept_dir)
            
        filepath = os.path.join(intercept_dir, filename)
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"<!-- FROM: {mail_username} -->\n")
                f.write(f"<!-- TO: {recipient_email} -->\n")
                f.write(f"<!-- SUBJECT: {subject} -->\n")
                if attachment_path:
                    f.write(f"<!-- ATTACHMENT: {attachment_path} -->\n")
                f.write("<hr>\n")
                f.write(html_body)
            
            logger.info(f"SANDBOX MODE: Email captured locally! File: {filepath}")
            return True
        except Exception as e:
            logger.error(f"SANDBOX MODE ERROR: {e}")
            return False

    # -----------------------------------------------------------------------
    # SMTP MODE: Actual sending
    # -----------------------------------------------------------------------

    # Check configuration
    if not mail_username or not mail_password:
        logger.error("MAIL_USERNAME or MAIL_PASSWORD not found in .env")
        return False

    try:
        msg = EmailMessage()
        msg.set_content(html_body, subtype='html')
        msg['Subject'] = subject
        msg['From'] = mail_username
        msg['To'] = recipient_email

        if attachment_path and os.path.exists(attachment_path):
            ctype, encoding = mimetypes.guess_type(attachment_path)
            if ctype is None or encoding is not None:
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/', 1)
            with open(attachment_path, 'rb') as fp:
                msg.add_attachment(fp.read(),
                                   maintype=maintype,
                                   subtype=subtype,
                                   filename=os.path.basename(attachment_path))

        logger.info(f"Connecting to SMTP server {mail_server}:{mail_port}...")
        
        # Use SMTP_SSL for port 465, or standard SMTP for port 587
        if mail_port == 465:
            server = smtplib.SMTP_SSL(mail_server, mail_port)
        else:
            server = smtplib.SMTP(mail_server, mail_port)
            server.starttls()
            
        server.login(mail_username, mail_password)
        server.send_message(msg)
        server.quit()

        logger.info(f"Email sent successfully to {recipient_email} via SMTP")
        return True

    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return False


# ---------------------------------------------------------------------------
# Test Script
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("SMTP EMAIL TEST")
    print("=" * 60)

    test_email = "your_email@gmail.com" # Swap if you want to hardcode for test
    subject = "Loan Application Decision — Test"

    body = """
    <h2>Automated Loan Processing System</h2>
    <p>Dear Applicant,</p>
    <p>This is a <b>test email</b> from the Automated Enterprise Loan Approval System.</p>
    <p>Your loan application has been processed successfully by our AI system via SMTP!</p>
    <br>
    <p>Best regards,<br>
    Loan Processing Department</p>
    """

    send_email(
        recipient_email=test_email,
        subject=subject,
        body=body
    )