
import hashlib
import hmac

from app.config import settings


def verify_signature(body: bytes, signature: str | None) -> bool:
    """
    Verify GitHub webhook HMAC SHA-256 signature.
    """

    if not isinstance(signature, str) or not signature.isascii():
        return False

    expected = (
        "sha256="
        + hmac.new(
            settings.WEBHOOK_SECRET.encode(),
            body,
            hashlib.sha256,
        ).hexdigest()
    )

    return hmac.compare_digest(expected, signature)