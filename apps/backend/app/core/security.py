import base64
import hashlib
import hmac
import json
import time
import uuid
from typing import Any

from app.core.config import settings


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _sign(value: str) -> str:
    return hmac.new(
        settings.auth_secret_key.encode("utf-8"), value.encode("utf-8"), hashlib.sha256
    ).hexdigest()


def create_session_token(user_id: uuid.UUID, role: str) -> str:
    issued_at = int(time.time())
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": issued_at,
        "exp": issued_at + settings.auth_session_days * 24 * 60 * 60,
    }
    encoded_payload = _b64encode(
        json.dumps(payload, separators=(",", ":")).encode("utf-8")
    )
    return f"{encoded_payload}.{_sign(encoded_payload)}"


def decode_session_token(token: str) -> dict[str, Any] | None:
    try:
        encoded_payload, signature = token.split(".", 1)
    except ValueError:
        return None

    if not hmac.compare_digest(signature, _sign(encoded_payload)):
        return None

    try:
        payload = json.loads(_b64decode(encoded_payload))
    except (json.JSONDecodeError, ValueError):
        return None

    if int(payload.get("exp", 0)) < int(time.time()):
        return None

    return payload


def create_csrf_token(session_token: str) -> str:
    nonce = _b64encode(uuid.uuid4().bytes)
    value = f"{nonce}.{hashlib.sha256(session_token.encode('utf-8')).hexdigest()}"
    return f"{nonce}.{_sign(value)}"


def verify_csrf_token(session_token: str, csrf_token: str) -> bool:
    try:
        nonce, signature = csrf_token.split(".", 1)
    except ValueError:
        return False

    value = f"{nonce}.{hashlib.sha256(session_token.encode('utf-8')).hexdigest()}"
    return hmac.compare_digest(signature, _sign(value))
