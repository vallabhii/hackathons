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
store = BloomStore(
    app.config["FIREBASE_CREDENTIALS_PATH"],
    app.config["FIREBASE_CREDENTIALS_JSON"]
)

ALLOWED_DASHBOARD_PAGES = {"home", "calendar", "analytics", "chat", "myths", "profile"}
ALLOWED_CYCLE_PHASES = {"menstrual", "follicular", "ovulatory", "luteal", "unsure"}
LOG_NUMBER_FIELDS = {
    "sleep": (0, 14, "Sleep hours"),
    "energy": (1, 5, "Energy level"),
    "exerciseHours": (0, 12, "Exercise hours"),
    "calories": (0, 6000, "Calories"),
    "proteinGrams": (0, 300, "Protein grams"),
    "fatGrams": (0, 250, "Fat grams")
}


def current_email():
    return session.get("email")


def require_auth():
    email = current_email()
    if not email:
        return None, (jsonify({"error": "Please verify your email to continue."}), 401)
    return email, None


@app.get("/")
def index():
    return render_app()


@app.get("/dashboard")
def dashboard_home():
    return render_app("home")


@app.get("/dashboard/<page>")
def dashboard_page(page):
    return render_app(page if page in ALLOWED_DASHBOARD_PAGES else "home")


def today_iso():
    return datetime.now(timezone.utc).date().isoformat()


def render_app(page="home"):
    return render_template("index.html", initial_page=page, today=today_iso())


def parse_iso_date(value, field_name):
    if not value:
        return None, None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date(), None
    except ValueError:
        return None, f"{field_name} must be a valid date."


def validate_onboarding_profile(profile):
    last_period_date = (profile.get("lastPeriodDate") or "").strip()
    parsed_date, error = parse_iso_date(last_period_date, "Date of last period")
    if error:
        return error
    if parsed_date and parsed_date > datetime.now(timezone.utc).date():
        return "Date of last period cannot be after today."
    return None


def validate_log_payload(log, date_key):
    parsed_date, error = parse_iso_date(date_key, "Log date")
    if error:
        return error
    if parsed_date and parsed_date > datetime.now(timezone.utc).date():
        return "Check-in date cannot be after today."

    cycle_phase = (log.get("cyclePhase") or "").strip().lower()
    if cycle_phase not in ALLOWED_CYCLE_PHASES:
        return "Please choose a valid cycle phase."
    log["cyclePhase"] = cycle_phase

    for field, (minimum, maximum, label) in LOG_NUMBER_FIELDS.items():
        value = log.get(field)
        if value in ("", None):
            log[field] = ""
            continue
        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            return f"{label} must be a number."
        if numeric_value < minimum or numeric_value > maximum:
            return f"{label} must be between {minimum} and {maximum}."
        log[field] = numeric_value
    return None


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
        response = {
            "message": "A soft little code is on its way to your inbox.",
            "pendingSignup": not user_exists
        }
        if app.config["RESEND_API_KEY"]:
            send_otp(email, otp, app.config)
        else:
            response["devOtp"] = otp
            response["message"] = "Development mode: use the OTP shown below to continue."
        return jsonify(response)
    except Exception:
        app.logger.exception("Bloom OTP request failed")
        return jsonify({"error": "Bloom could not send the OTP email or save the auth session. Please check Render environment variables and logs."}), 500

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
    today = today_iso()
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
    today = today_iso()
    return jsonify({
        "user": user,
        "needsOnboarding": not user.get("onboardingComplete"),
        "needsCheckin": not store.get_log(email, today),
        "today": today
    })


@app.get("/api/config-status")
def config_status():
    return jsonify({
        "firebaseConfigured": store.db is not None,
        "emailConfigured": bool(app.config["RESEND_API_KEY"]),
        "storage": "firebase" if store.db else "local-dev-json"
    })


@app.post("/api/onboarding")
def onboarding():
    email, error = require_auth()
    if error:
        return error
    profile = request.get_json(force=True)
    validation_error = validate_onboarding_profile(profile)
    if validation_error:
        return jsonify({"error": validation_error}), 400
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
    validation_error = validate_log_payload(log, date_key)
    if validation_error:
        return jsonify({"error": validation_error}), 400
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

