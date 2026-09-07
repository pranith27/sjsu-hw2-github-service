
from app.routes.issues import format_issue


def test_format_issue():

    issue = {
        "number": 1,
        "html_url": "https://github.com",
        "state": "open",
        "title": "Test",
        "body": "Body",
        "labels": [{"name": "bug"}],
        "created_at": "today",
        "updated_at": "today",
    }

    formatted = format_issue(issue)

    assert formatted["title"] == "Test"

    assert formatted["labels"] == ["bug"]