import hashlib
import json
import os
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore


class BloomStore:
    def __init__(self, credentials_path="", credentials_json=""):
        self.db = None
        if credentials_json:
            if not firebase_admin._apps:
                cred = credentials.Certificate(json.loads(credentials_json))
                firebase_admin.initialize_app(cred)
            self.db = firestore.client()
        elif credentials_path and os.path.exists(credentials_path):
            if not firebase_admin._apps:
                cred = credentials.Certificate(credentials_path)
                firebase_admin.initialize_app(cred)
            self.db = firestore.client()
        self.local_path = Path("instance/local_store.json")
        self.local_path.parent.mkdir(exist_ok=True)

    def _read_local(self):
        if not self.local_path.exists():
            return {"users": {}, "otp_sessions": {}}
        return json.loads(self.local_path.read_text(encoding="utf-8"))

    def _write_local(self, data):
        self.local_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def user_exists(self, email):
        return self.get_user(email) is not None

    def get_user(self, email):
        if self.db:
            doc = self.db.collection("users").document(email).get()
            return doc.to_dict() if doc.exists else None
        return deepcopy(self._read_local()["users"].get(email))

    def create_user(self, email):
        user = {
            "email": email,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "onboardingComplete": False
        }
        if self.db:
            self.db.collection("users").document(email).set(user)
            return
        data = self._read_local()
        data["users"][email] = {**user, "daily_logs": {}, "analytics": {}}
        self._write_local(data)

    def update_user(self, email, payload):
        if self.db:
            self.db.collection("users").document(email).set(payload, merge=True)
            return
        data = self._read_local()
        data["users"].setdefault(email, {"email": email, "daily_logs": {}, "analytics": {}})
        data["users"][email].update(payload)
        self._write_local(data)

    def save_otp(self, email, otp_hash, expires_at, pending_signup=False):
        payload = {"otpHash": otp_hash, "expiresAt": expires_at, "pendingSignup": pending_signup}
        if self.db:
            self.db.collection("otp_sessions").document(email).set(payload)
            return
        data = self._read_local()
        data["otp_sessions"][email] = payload
        self._write_local(data)

    def verify_otp(self, email, otp):
        session = None
        if self.db:
            doc = self.db.collection("otp_sessions").document(email).get()
            session = doc.to_dict() if doc.exists else None
        else:
            session = self._read_local()["otp_sessions"].get(email)
        if not session:
            return False
        expires_at = datetime.fromisoformat(session["expiresAt"])
        if expires_at < datetime.now(timezone.utc):
            return False
        otp_hash = hashlib.sha256(otp.encode("utf-8")).hexdigest()
        return otp_hash == session.get("otpHash")

    def get_logs(self, email):
        if self.db:
            docs = self.db.collection("users").document(email).collection("daily_logs").stream()
            return [doc.to_dict() for doc in docs]
        user = self._read_local()["users"].get(email, {})
        return list(user.get("daily_logs", {}).values())

    def get_log(self, email, date_key):
        if self.db:
            doc = self.db.collection("users").document(email).collection("daily_logs").document(date_key).get()
            return doc.to_dict() if doc.exists else None
        user = self._read_local()["users"].get(email, {})
        return deepcopy(user.get("daily_logs", {}).get(date_key))

    def save_log(self, email, date_key, log):
        if self.db:
            self.db.collection("users").document(email).collection("daily_logs").document(date_key).set(log, merge=True)
            return
        data = self._read_local()
        data["users"].setdefault(email, {"email": email, "daily_logs": {}, "analytics": {}})
        data["users"][email].setdefault("daily_logs", {})[date_key] = log
        self._write_local(data)

    def save_analytics(self, email, analytics):
        if self.db:
            self.db.collection("users").document(email).collection("analytics").document("latest").set(analytics)
            return
        data = self._read_local()
        data["users"].setdefault(email, {"email": email, "daily_logs": {}, "analytics": {}})
        data["users"][email]["analytics"] = analytics
        self._write_local(data)
