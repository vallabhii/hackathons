import hashlib
import random
import resend
from datetime import datetime, timezone

def create_otp(expiry_delta):
    otp = f"{random.randint(100000, 999999)}"
    otp_hash = hashlib.sha256(otp.encode("utf-8")).hexdigest()
    expires_at = datetime.now(timezone.utc) + expiry_delta
    return otp, otp_hash, expires_at.isoformat()

def send_otp(email, otp, config):
    resend.api_key = config["RESEND_API_KEY"]
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
        "from": config["RESEND_FROM_EMAIL"],
        "to": email,
        "subject": subject,
        "html": html
    })
