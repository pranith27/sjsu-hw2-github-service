"""Offline tests use dummy configuration and cannot reach external HTTP."""
import os

import httpx
import pytest

if os.getenv("RUN_LIVE_INTEGRATION") != "1":
    os.environ.update(
        GITHUB_TOKEN="test-token-not-a-credential",
        GITHUB_OWNER="test-owner",
        GITHUB_REPO="test-repo",
        WEBHOOK_SECRET="test-webhook-secret",
    )


@pytest.fixture(autouse=True)
def block_external_http(request, monkeypatch):
    if request.node.get_closest_marker("live"):
        return

    def blocked(*args, **kwargs):
        raise AssertionError("External HTTP is forbidden in offline tests")

    monkeypatch.setattr(httpx, "request", blocked)
