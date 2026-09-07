import hashlib
import hmac

from app.webhook import verify_signature
from app.config import settings


def test_valid_signature():
    body = b'{"action":"opened"}'

    signature = (
        "sha256="
        + hmac.new(
            settings.WEBHOOK_SECRET.encode(),
            body,
            hashlib.sha256,
        ).hexdigest()
    )

    assert verify_signature(body, signature)


def test_invalid_signature():
    body = b'{"action":"opened"}'

    assert verify_signature(body, "sha256=wrong") is False


def test_tampered_body():
    original_body = b'{"action":"opened"}'

    signature = (
        "sha256="
        + hmac.new(
            settings.WEBHOOK_SECRET.encode(),
            original_body,
            hashlib.sha256,
        ).hexdigest()
    )

    tampered_body = b'{"action":"closed"}'

    assert verify_signature(tampered_body, signature) is False


def test_empty_body():
    body = b""

    signature = (
        "sha256="
        + hmac.new(
            settings.WEBHOOK_SECRET.encode(),
            body,
            hashlib.sha256,
        ).hexdigest()
    )

    assert verify_signature(body, signature)


def test_invalid_signature_prefix():
    body = b'{"action":"opened"}'

    signature = (
        "sha1="
        + hmac.new(
            settings.WEBHOOK_SECRET.encode(),
            body,
            hashlib.sha256,
        ).hexdigest()
    )

    assert verify_signature(body, signature) is False


def test_random_signature():
    body = b'{"action":"opened"}'

    random_signature = (
        "sha256="
        + "0" * 64
    )

    assert verify_signature(body, random_signature) is False