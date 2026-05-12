import hashlib
import random
import smtplib
import os
import resend
from datetime import datetime, timezone
from email.message import EmailMessage

resend.api_key = os.getenv("RESEND_API_KEY")

def create_otp(expiry_delta):
    otp = f"{random.randint(100000, 999999)}"
    otp_hash = hashlib.sha256(otp.encode("utf-8")).hexdigest()
    expires_at = datetime.now(timezone.utc) + expiry_delta
    return otp, otp_hash, expires_at.isoformat()

def send_otp(email, otp, config):
    subject = "Your Bloom verification code"

    html = f"""
    <div style="font-family: Arial, sans-serif;">
        <h2>Your Bloom code is:</h2>
        <h1>{otp}</h1>
        <p>
            This code will expire soon.
            Take your time, breathe softly,
            and come back when ready.
        </p>
    </div>
    """

    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": email,
        "subject": subject,
        "html": html
    })