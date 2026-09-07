

import pytest
from pydantic import ValidationError

from app.models import (
    CreateIssueRequest,
    UpdateIssueRequest,
    CreateCommentRequest,
)


def test_create_issue_valid():
    issue = CreateIssueRequest(title="Test Issue")

    assert issue.title == "Test Issue"


def test_create_issue_missing_title():
    with pytest.raises(ValidationError):
        CreateIssueRequest()


def test_comment_body_required():
    with pytest.raises(ValidationError):
        CreateCommentRequest(body="")


def test_update_issue_valid_state():
    issue = UpdateIssueRequest(state="closed")

    assert issue.state == "closed"


def test_update_issue_invalid_state():
    with pytest.raises(ValidationError):
        UpdateIssueRequest(state="done")