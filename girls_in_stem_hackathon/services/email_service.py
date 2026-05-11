import hashlib
import random
import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage


def create_otp(expiry_delta):
    otp = f"{random.randint(100000, 999999)}"
    otp_hash = hashlib.sha256(otp.encode("utf-8")).hexdigest()
    expires_at = datetime.now(timezone.utc) + expiry_delta
    return otp, otp_hash, expires_at.isoformat()


def send_otp(email, otp, config):
    subject = "Your Bloom verification code"
    body = (
        f"Your Bloom code is {otp}.\n\n"
        "This code will expire soon. Take your time, breathe softly, and come back when ready."
    )
    if not config.get("SMTP_HOST") or not config.get("SMTP_USERNAME"):
        print(f"[Bloom dev OTP] {email}: {otp}")
        return

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = config["SMTP_FROM_EMAIL"]
    message["To"] = email
    message.set_content(body)

    with smtplib.SMTP(config["SMTP_HOST"], config["SMTP_PORT"]) as smtp:
        smtp.starttls()
        smtp.login(config["SMTP_USERNAME"], config["SMTP_PASSWORD"])
        smtp.send_message(message)
