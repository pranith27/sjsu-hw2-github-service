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


def test_format_issue_multiple_labels():
    issue = {
        "number": 2,
        "html_url": "https://github.com",
        "state": "open",
        "title": "Bug Fix",
        "body": "Example",
        "labels": [
            {"name": "bug"},
            {"name": "high-priority"},
            {"name": "backend"},
        ],
        "created_at": "today",
        "updated_at": "today",
    }

    formatted = format_issue(issue)

    assert formatted["labels"] == [
        "bug",
        "high-priority",
        "backend",
    ]


def test_format_issue_no_labels():
    issue = {
        "number": 3,
        "html_url": "https://github.com",
        "state": "open",
        "title": "No Labels",
        "body": "Body",
        "labels": [],
        "created_at": "today",
        "updated_at": "today",
    }

    formatted = format_issue(issue)

    assert formatted["labels"] == []


def test_format_issue_closed():
    issue = {
        "number": 4,
        "html_url": "https://github.com",
        "state": "closed",
        "title": "Closed Issue",
        "body": "Done",
        "labels": [],
        "created_at": "today",
        "updated_at": "today",
    }

    formatted = format_issue(issue)

    assert formatted["state"] == "closed"


def test_format_issue_preserves_number():
    issue = {
        "number": 25,
        "html_url": "https://github.com",
        "state": "open",
        "title": "Issue 25",
        "body": "Testing",
        "labels": [],
        "created_at": "today",
        "updated_at": "today",
    }

    formatted = format_issue(issue)

    assert formatted["number"] == 25