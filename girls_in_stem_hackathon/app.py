import smtplib
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template, request, session
from flask_cors import CORS

from config import Config
from services.analytics_service import build_analytics
from services.chatbot_service import answer_question
from services.email_service import create_otp, send_otp
from services.firebase_service import BloomStore


app = Flask(__name__)
app.config.from_object(Config)
CORS(app, supports_credentials=True)
store = BloomStore(app.config["FIREBASE_CREDENTIALS_PATH"])


def current_email():
    return session.get("email")


def require_auth():
    email = current_email()
    if not email:
        return None, (jsonify({"error": "Please verify your email to continue."}), 401)
    return email, None


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/auth/request-otp")
def request_otp():
    try:
        data = request.get_json(force=True)
        email = (data.get("email") or "").strip().lower()
        intent = data.get("intent", "login")
        if not email or "@" not in email:
            return jsonify({"error": "Please enter a valid email address."}), 400

        user_exists = store.user_exists(email)
        if intent == "login" and not user_exists:
            return jsonify({
                "needsSignup": True,
                "message": "This email is not registered yet. Please create an account first 🌸"
            }), 404

        otp, otp_hash, expires_at = create_otp(app.config["OTP_EXPIRY"])
        store.save_otp(email, otp_hash, expires_at, pending_signup=not user_exists)
        send_otp(email, otp, app.config)
        response = {
            "message": "A soft little code is on its way to your inbox.",
            "pendingSignup": not user_exists
        }
        if not app.config["SMTP_HOST"]:
            response["devOtp"] = otp
            response["message"] = "Development mode: use the OTP shown below to continue."
        return jsonify(response)
    except smtplib.SMTPAuthenticationError:
        app.logger.exception("Bloom OTP email authentication failed")
        return jsonify({"error": "Gmail rejected the SMTP login. Please create a fresh Google App Password and update SMTP_PASSWORD in Render."}), 502
    except smtplib.SMTPException:
        app.logger.exception("Bloom OTP email sending failed")
        return jsonify({"error": "Bloom could not send the OTP email. Please check the SMTP settings in Render."}), 502
    except Exception:
        app.logger.exception("Bloom OTP request failed")
        return jsonify({"error": "Bloom could not start signup. Please check Render logs for the exact backend error."}), 500

@app.post("/api/auth/verify-otp")
def verify_otp():
    data = request.get_json(force=True)
    email = (data.get("email") or "").strip().lower()
    otp = (data.get("otp") or "").strip()
    if not store.verify_otp(email, otp):
        return jsonify({"error": "That code was not quite right or has expired."}), 400

    session["email"] = email
    user = store.get_user(email)
    if not user:
        store.create_user(email)
        user = store.get_user(email)
    today = datetime.now(timezone.utc).date().isoformat()
    return jsonify({
        "user": user,
        "needsOnboarding": not user.get("onboardingComplete"),
        "needsCheckin": not store.get_log(email, today),
        "today": today
    })


@app.post("/api/auth/logout")
def logout():
    session.clear()
    return jsonify({"message": "Signed out."})


@app.get("/api/me")
def me():
    email, error = require_auth()
    if error:
        return error
    user = store.get_user(email)
    today = datetime.now(timezone.utc).date().isoformat()
    return jsonify({
        "user": user,
        "needsOnboarding": not user.get("onboardingComplete"),
        "needsCheckin": not store.get_log(email, today),
        "today": today
    })


@app.post("/api/onboarding")
def onboarding():
    email, error = require_auth()
    if error:
        return error
    profile = request.get_json(force=True)
    store.update_user(email, {
        "preferredName": profile.get("preferredName", "").strip(),
        "age": profile.get("age"),
        "diagnosisStatus": profile.get("diagnosisStatus"),
        "averageCycleLength": profile.get("averageCycleLength"),
        "lastPeriodDate": profile.get("lastPeriodDate"),
        "symptoms": profile.get("symptoms", []),
        "wellnessGoals": profile.get("wellnessGoals", []),
        "onboardingComplete": True,
        "updatedAt": datetime.now(timezone.utc).isoformat()
    })
    return jsonify({"user": store.get_user(email)})


@app.get("/api/logs")
def logs():
    email, error = require_auth()
    if error:
        return error
    return jsonify({"logs": store.get_logs(email)})


@app.get("/api/logs/<date_key>")
def get_log(date_key):
    email, error = require_auth()
    if error:
        return error
    return jsonify({"log": store.get_log(email, date_key)})


@app.post("/api/logs/<date_key>")
def save_log(date_key):
    email, error = require_auth()
    if error:
        return error
    log = request.get_json(force=True)
    log["date"] = date_key
    log["updatedAt"] = datetime.now(timezone.utc).isoformat()
    store.save_log(email, date_key, log)
    analytics = build_analytics(store.get_logs(email), store.get_user(email))
    store.save_analytics(email, analytics)
    return jsonify({"log": store.get_log(email, date_key), "analytics": analytics})


@app.get("/api/analytics")
def analytics():
    email, error = require_auth()
    if error:
        return error
    result = build_analytics(store.get_logs(email), store.get_user(email))
    store.save_analytics(email, result)
    return jsonify(result)


@app.post("/api/chat")
def chat():
    email, error = require_auth()
    if error:
        return error
    data = request.get_json(force=True)
    return jsonify({"reply": answer_question(data.get("message", ""))})


if __name__ == "__main__":
    app.run(debug=True)

