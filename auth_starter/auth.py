import os, re, time, hmac, hashlib, secrets, base64
from datetime import timedelta
from collections import defaultdict, deque
from sqlalchemy import select
from passlib.context import CryptContext
from cryptography.fernet import Fernet, InvalidToken
from models import User, VerificationToken, AuditEvent, UserPreference, utcnow

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
_limits = defaultdict(deque)

def cfg(name, default=None):
    if os.getenv(name):
        return os.getenv(name)
    try:
        import streamlit as st
        return st.secrets.get(name, default)
    except Exception:
        return default

def normalize_email(email):
    return (email or "").strip().lower()

def validate_password(password):
    return isinstance(password, str) and len(password) >= 12 and password == password.strip()

def rate_allowed(key, limit=5, window=60):
    now = time.monotonic()
    queue = _limits[key]
    while queue and now - queue[0] > window:
        queue.popleft()
    if len(queue) >= limit:
        return False
    queue.append(now)
    return True

def _fernet():
    key = cfg("APP_SECRET_KEY")
    if not key:
        raise RuntimeError("APP_SECRET_KEY is not configured")
    return Fernet(key.encode() if isinstance(key, str) else key)

def audit(db, user, event_type, details=None):
    db.add(AuditEvent(user_id=user.id, event_type=event_type, details=details))
    db.flush()

def register_user(db, email, display_name, password, age_confirmed, accepted_terms):
    email = normalize_email(email)
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return None, None, "Enter a valid email address."
    if not display_name or len(display_name.strip()) > 120:
        return None, None, "Enter your name."
    if not validate_password(password):
        return None, None, "Password must be at least 12 characters with no outer spaces."
    if not age_confirmed or not accepted_terms:
        return None, None, "Confirm the minimum age and accept the Privacy Policy and Terms."
    if db.scalar(select(User.id).where(User.email == email, User.deleted_at.is_(None))):
        return None, None, "Unable to create an account with those details."
    user = User(email=email, display_name=display_name.strip(), password_hash=pwd.hash(password))
    db.add(user)
    db.flush()
    db.add(UserPreference(user_id=user.id, settings={}))
    raw = secrets.token_urlsafe(32)
    db.add(VerificationToken(user_id=user.id, token_hash=hashlib.sha256(raw.encode()).hexdigest(),
                             expires_at=utcnow() + timedelta(hours=24)))
    db.commit()
    return user, raw, "Account created; verify your email."

def verify_email_token(db, raw_token):
    if not raw_token or len(raw_token) > 200:
        return False
    item = db.scalar(select(VerificationToken).where(
        VerificationToken.token_hash == hashlib.sha256(raw_token.encode()).hexdigest()))
    if not item or item.used_at or item.expires_at <= utcnow():
        return False
    user = db.get(User, item.user_id)
    if not user or user.deleted_at:
        return False
    item.used_at = utcnow()
    user.email_verified_at = utcnow()
    db.commit()
    return True

def login_user(db, email, password, totp_code=None):
    email = normalize_email(email)
    if not rate_allowed("login:" + email, 5, 60):
        return None, "Too many attempts. Please wait a minute."
    user = db.scalar(select(User).where(User.email == email, User.deleted_at.is_(None)))
    if not user:
        return None, "Incorrect email or password."
    now = utcnow()
    if user.locked_until and user.locked_until > now:
        return None, "Account temporarily locked. Try again later."
    if not pwd.verify(password or "", user.password_hash):
        user.failed_login_count += 1
        if user.failed_login_count >= 5:
            user.failed_login_count = 0
            user.locked_until = now + timedelta(minutes=15)
        db.commit()
        return None, "Incorrect email or password."
    if user.totp_enabled:
        if not totp_code or not rate_allowed("totp:" + str(user.id), 5, 60):
            return None, "Enter a valid authenticator code."
        import pyotp
        try:
            secret = _fernet().decrypt(user.totp_secret_encrypted.encode()).decode()
        except (InvalidToken, ValueError, TypeError):
            return None, "Could not validate authenticator code."
        if not pyotp.TOTP(secret).verify(str(totp_code), valid_window=1):
            return None, "Enter a valid authenticator code."
    if str(cfg("REQUIRE_EMAIL_VERIFICATION", "false")).lower() == "true" and not user.email_verified_at:
        return None, "Verify your email before signing in."
    user.failed_login_count = 0
    user.locked_until = None
    db.commit()
    return user, "Signed in."

def reload_session_user(db, user_id):
    user = db.get(User, user_id)
    return user if user and not user.deleted_at else None

def resend_token(db, user):
    raw = secrets.token_urlsafe(32)
    db.add(VerificationToken(user_id=user.id, token_hash=hashlib.sha256(raw.encode()).hexdigest(),
                             expires_at=utcnow() + timedelta(hours=24)))
    db.commit()
    return raw

def setup_totp(user):
    import pyotp
    secret = pyotp.random_base32()
    return secret, pyotp.TOTP(secret).provisioning_uri(name=user.email, issuer_name="ATHARVADRISHTI")

def enable_totp(db, user, secret, code):
    import pyotp
    if not pyotp.TOTP(secret).verify(str(code), valid_window=1):
        return False
    user.totp_secret_encrypted = _fernet().encrypt(secret.encode()).decode()
    user.totp_enabled = True
    audit(db, user, "2fa_enabled")
    db.commit()
    return True

def disable_totp(db, user, code):
    import pyotp
    if not user.totp_enabled or not user.totp_secret_encrypted:
        return False, "2FA is not enabled."
    try:
        secret = _fernet().decrypt(user.totp_secret_encrypted.encode()).decode()
    except InvalidToken:
        return False, "Stored 2FA secret cannot be decrypted."
    if not pyotp.TOTP(secret).verify(str(code), valid_window=1):
        return False, "Enter a valid current code."
    user.totp_enabled = False
    user.totp_secret_encrypted = None
    audit(db, user, "2fa_disabled")
    db.commit()
    return True, "2FA disabled."

def change_password(db, user, current_password, new_password):
    if not pwd.verify(current_password or "", user.password_hash):
        return False, "Current password is incorrect."
    if not validate_password(new_password):
        return False, "Password must be at least 12 characters with no outer spaces."
    user.password_hash = pwd.hash(new_password)
    user.cookie_nonce = secrets.token_urlsafe(24)
    audit(db, user, "password_changed")
    db.commit()
    return True, "Password changed."

def sign_cookie(user_id, expiry_unix, nonce, secret=None):
    secret = secret or cfg("APP_SECRET_KEY")
    if not secret:
        raise RuntimeError("APP_SECRET_KEY is missing")
    key = secret.encode() if isinstance(secret, str) else secret
    payload = f"{user_id}|{int(expiry_unix)}|{nonce}"
    signature = hmac.new(key, payload.encode(), hashlib.sha256).hexdigest()
    return base64.urlsafe_b64encode(f"{payload}|{signature}".encode()).decode()

def verify_cookie(cookie, secret=None, now=None):
    try:
        raw = base64.urlsafe_b64decode(cookie.encode()).decode()
        user_id, expiry, nonce, signature = raw.split("|", 3)
        secret = secret or cfg("APP_SECRET_KEY")
        key = secret.encode() if isinstance(secret, str) else secret
        payload = f"{user_id}|{expiry}|{nonce}"
        expected = hmac.new(key, payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected) or int(expiry) <= int(now or time.time()):
            return None
        return user_id, nonce
    except Exception:
        return None
