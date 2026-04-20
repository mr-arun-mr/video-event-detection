import base64
import hashlib
import hmac
import json
import time

from config import JWT_ALGORITHM, JWT_EXPIRY_HOURS, JWT_SECRET

assert JWT_ALGORITHM == "HS256", "Only HS256 is supported"

_SECRET_BYTES = JWT_SECRET.encode("utf-8")


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(s: str) -> bytes:
    # Re-add stripped padding
    padding = 4 - len(s) % 4
    if padding != 4:
        s += "=" * padding
    return base64.urlsafe_b64decode(s)


def generate_token(user_id: str) -> str:
    now = int(time.time())
    header = _b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = _b64url_encode(
        json.dumps(
            {
                "sub": user_id,
                "iat": now,
                "exp": now + JWT_EXPIRY_HOURS * 3600,
            }
        ).encode()
    )
    signing_input = f"{header}.{payload}"
    sig = _b64url_encode(
        hmac.new(_SECRET_BYTES, signing_input.encode(), hashlib.sha256).digest()
    )
    return f"{signing_input}.{sig}"


def validate_token(token: str) -> dict:
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Malformed token")

    header_b64, payload_b64, sig_b64 = parts
    signing_input = f"{header_b64}.{payload_b64}"

    expected_sig = _b64url_encode(
        hmac.new(_SECRET_BYTES, signing_input.encode(), hashlib.sha256).digest()
    )
    if not hmac.compare_digest(expected_sig, sig_b64):
        raise ValueError("Invalid token signature")

    payload = json.loads(_b64url_decode(payload_b64))

    if int(time.time()) > payload.get("exp", 0):
        raise ValueError("Token has expired")

    return payload
