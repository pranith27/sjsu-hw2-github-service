from unittest.mock import Mock

import httpx
import pytest

from app.github_client import GitHubClient


@pytest.fixture
def transport(monkeypatch):
    request = Mock()
    monkeypatch.setattr(httpx, "request", request)
    return request


def test_short_rate_limit_retries_get(transport, monkeypatch):
    sleep = Mock()
    monkeypatch.setattr("time.sleep", sleep)
    transport.side_effect = [
        httpx.Response(429, headers={"Retry-After": "1"}),
        httpx.Response(200),
    ]
    assert GitHubClient().get_issue(1).status_code == 200
    assert transport.call_count == 2
    sleep.assert_called_once_with(1)


def test_long_rate_limit_returns_without_sleep(transport, monkeypatch):
    sleep = Mock()
    monkeypatch.setattr("time.sleep", sleep)
    transport.return_value = httpx.Response(
        403,
        headers={"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "1120"},
        json={"message": "rate limited"},
    )
    monkeypatch.setattr("time.time", lambda: 1000)
    response = GitHubClient().get_issue(1)
    assert response.status_code == 429
    assert response.headers["Retry-After"] == "120"
    assert transport.call_count == 1
    sleep.assert_not_called()


def test_get_server_errors_retry_with_bounded_backoff(transport, monkeypatch):
    sleep = Mock()
    monkeypatch.setattr("time.sleep", sleep)
    transport.return_value = httpx.Response(503)
    response = GitHubClient().get_issue(1)
    assert response.status_code == 503
    assert response.headers["Retry-After"]
    assert transport.call_count == 3
    assert [call.args[0] for call in sleep.call_args_list] == [0.25, 0.5]


@pytest.mark.parametrize("status", [429, 500, 503])
def test_mutations_are_not_retried(transport, status):
    transport.return_value = httpx.Response(status, headers={"Retry-After": "1"})
    assert GitHubClient().create_issue({"title": "test"}).status_code == status
    assert transport.call_count == 1


def test_network_failure_is_safe_503_without_retry_or_secret(transport):
    transport.side_effect = httpx.ReadTimeout("secret transport detail")
    response = GitHubClient().create_comment(1, {"body": "test"})
    assert response.status_code == 503
    assert "secret" not in response.text
    assert transport.call_count == 1


@pytest.mark.parametrize("status", [401, 403, 404])
def test_nonrate_errors_are_unchanged(transport, status):
    transport.return_value = httpx.Response(status, json={"message": "denied"})
    assert GitHubClient().get_issue(1).status_code == status
    assert transport.call_count == 1


def test_comments_fetch_uses_paginated_get(transport):
    transport.return_value = httpx.Response(200, json=[])
    GitHubClient().list_comments(7, {"page": 2, "per_page": 10})
    assert transport.call_args.kwargs["method"] == "GET"
    assert transport.call_args.kwargs["url"].endswith("/issues/7/comments")
    assert transport.call_args.kwargs["params"] == {"page": 2, "per_page": 10}


@pytest.mark.parametrize("retry_after", ["invalid", "nan", "inf"])
def test_malformed_retry_after_uses_safe_fallback(transport, retry_after):
    transport.return_value = httpx.Response(429, headers={"Retry-After": retry_after})
    response = GitHubClient().get_issue(1)
    assert response.headers["Retry-After"] == "60"
    assert transport.call_count == 1


def test_retry_after_date_preserved_without_wait(transport, monkeypatch):
    retry_after = "Thu, 01 Jan 1970 00:20:00 GMT"
    transport.return_value = httpx.Response(503, headers={"Retry-After": retry_after})
    monkeypatch.setattr("time.time", lambda: 1000)
    assert GitHubClient().get_issue(1).headers["Retry-After"] == retry_after
    assert transport.call_count == 1


def test_secondary_rate_limit_without_headers_surfaces_one_minute(transport):
    transport.return_value = httpx.Response(
        403, json={"message": "You have exceeded a secondary rate limit"}
    )
    response = GitHubClient().get_issue(1)
    assert response.status_code == 429
    assert response.headers["Retry-After"] == "60"
    assert transport.call_count == 1
