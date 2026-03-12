# =============================================================================
# email/email_sender.py
# =============================================================================
# PURPOSE: Send decision emails to loan applicants using SendGrid API.
#
# HOW IT WORKS:
#   1. Reads SENDGRID_API_KEY and FROM_EMAIL from .env
#   2. Connects to SendGrid API
#   3. Sends email to the applicant
#
# REQUIRES:
#   - sendgrid package
#   - python-dotenv package
#   - SENDGRID_API_KEY in .env
#   - FROM_EMAIL in .env (must be verified in SendGrid)
# =============================================================================

import os
import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

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
def send_email(recipient_email: str, subject: str, body: str) -> bool:
    """
    Send email using SendGrid API.

    Args:
        recipient_email (str): recipient email address
        subject (str): email subject
        body (str): email body (HTML supported)

    Returns:
        bool: True if sent successfully, False otherwise
    """

    api_key = os.getenv("SENDGRID_API_KEY", "").strip()
    sender_email = os.getenv("FROM_EMAIL", "").strip()
    mail_mode = os.getenv("MAIL_MODE", "SENDGRID").upper().strip()

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
                f.write(f"<!-- FROM: {sender_email} -->\n")
                f.write(f"<!-- TO: {recipient_email} -->\n")
                f.write(f"<!-- SUBJECT: {subject} -->\n")
                f.write("<hr>\n")
                f.write(body)
            
            print(f"📦 SANDBOX MODE: Email captured locally!")
            print(f"   File: {filepath}")
            return True
        except Exception as e:
            print(f"❌ SANDBOX MODE ERROR: {e}")
            return False

    # -----------------------------------------------------------------------
    # SENDGRID MODE: Actual sending
    # -----------------------------------------------------------------------

    # Check configuration
    if not api_key:
        print("❌ SENDGRID_API_KEY not found in .env")
        return False

    if not sender_email:
        print("❌ FROM_EMAIL not found in .env")
        return False

    try:
        message = Mail(
            from_email=sender_email,
            to_emails=recipient_email,
            subject=subject,
            html_content=body
        )

        print("Connecting to SendGrid API...")
        sg = SendGridAPIClient(api_key)

        response = sg.send(message)

        if response.status_code in [200, 202]:
            print(f"✅ Email sent successfully to {recipient_email}")
            return True
        else:
            print(f"❌ Failed with status code: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False


# ---------------------------------------------------------------------------
# Test Script
# ---------------------------------------------------------------------------
if __name__ == "__main__":

    print("=" * 60)
    print("SENDGRID EMAIL TEST")
    print("=" * 60)

    subject = "Loan Application Decision — Test"

    body = """
    <h2>Automated Loan Processing System</h2>

    <p>Dear Applicant,</p>

    <p>This is a <b>test email</b> from the Automated Enterprise Loan Approval System.</p>

    <p>Your loan application has been processed successfully by our AI system.</p>

    <p>Thank you.</p>

    <br>

    <p>Best regards,<br>
    Loan Processing Department</p>
    """

    send_email(
        recipient_email="your_email@gmail.com",
        subject=subject,
        body=body
    )