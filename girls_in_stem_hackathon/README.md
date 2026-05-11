# Bloom — PCOS Wellness Tracker

Bloom is a full-stack Flask, Firebase Firestore, vanilla JavaScript, and Chart.js wellness tracker for PCOS support. It uses passwordless OTP authentication, first-time onboarding, daily check-ins, calendar editing, analytics, compassionate recommendations, a supportive chatbot, and myths vs facts education.

## Setup

1. Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and add values.

3. Firebase:

- Create a Firebase project.
- Enable Firestore.
- Download a service account JSON file.
- Set `FIREBASE_CREDENTIALS_PATH` in `.env` to that file path.

If Firebase is not configured, Bloom runs with a local development JSON database at `instance/local_store.json`.

4. Email OTP:

- Set `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, and `SMTP_FROM_EMAIL`.
- If SMTP is not configured, OTPs are printed in the Flask console for development.

5. Run:

```powershell
python app.py
```

Open `http://127.0.0.1:5000`.

## Firestore Shape

- `users/{email}`: profile, onboarding, auth metadata.
- `users/{email}/daily_logs/{YYYY-MM-DD}`: daily check-ins and calendar entries.
- `users/{email}/analytics/latest`: generated summaries and recommendations.
- `otp_sessions/{email}`: OTP hash, expiry, and pending signup flag.

All data is securely stored and handled privately when connected to Firebase.
