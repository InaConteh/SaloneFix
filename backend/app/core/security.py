import hmac
import hashlib
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import bcrypt
from jose import jwt, JWTError
from app.core.config import settings


def hash_password(password: str, rounds: int = 12) -> str:
    """Hash a plaintext password with bcrypt."""
    salt = bcrypt.gensalt(rounds=rounds)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def generate_signed_media_token(asset_id: str, expires_in_seconds: int = 3600) -> str:
    """Generate a tamper-evident HMAC signature token for private media streaming."""
    expiry = int(time.time()) + expires_in_seconds
    message = f"{asset_id}:{expiry}".encode("utf-8")
    sig = hmac.new(settings.SESSION_SECRET.encode("utf-8"), message, hashlib.sha256).hexdigest()
    return f"{expiry}.{sig}"


def verify_signed_media_token(asset_id: str, token: str) -> bool:
    """Verify HMAC signature token and ensure it has not expired."""
    try:
        expiry_str, signature = token.split(".", 1)
        expiry = int(expiry_str)
        if time.time() > expiry:
            return False
        expected_msg = f"{asset_id}:{expiry}".encode("utf-8")
        expected_sig = hmac.new(settings.SESSION_SECRET.encode("utf-8"), expected_msg, hashlib.sha256).hexdigest()
        return hmac.compare_digest(signature, expected_sig)
    except Exception:
        return False
