import os
import uuid
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# Skip if GitHub credentials are not configured
pytestmark = pytest.mark.skipif(
    not os.getenv("GITHUB_TOKEN"),
    reason="GitHub credentials not configured",
)


def test_create_get_update_comment_issue():
    unique = uuid.uuid4().hex[:8]

    # -----------------------------
    # Create Issue
    # -----------------------------
    create_response = client.post(
        "/issues",
        json={
            "title": f"Integration Test {unique}",
            "body": "Created by automated integration test",
            "labels": [],
        },
    )

    assert create_response.status_code == 201

    issue = create_response.json()
    issue_number = issue["number"]

    # -----------------------------
    # Get Issue
    # -----------------------------
    get_response = client.get(f"/issues/{issue_number}")

    assert get_response.status_code == 200
    assert get_response.json()["number"] == issue_number

    # -----------------------------
    # Update Issue
    # -----------------------------
    update_response = client.patch(
        f"/issues/{issue_number}",
        json={
            "title": f"Updated Integration Test {unique}",
            "state": "closed",
        },
    )

    assert update_response.status_code == 200

    # -----------------------------
    # Add Comment
    # -----------------------------
    comment_response = client.post(
        f"/issues/{issue_number}/comments",
        json={
            "body": "Integration Test Comment"
        },
    )

    assert comment_response.status_code == 201