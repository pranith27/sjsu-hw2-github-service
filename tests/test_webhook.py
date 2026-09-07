

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