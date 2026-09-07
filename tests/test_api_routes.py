from unittest.mock import Mock

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routes.issues import github_client

ISSUE = {
    "number": 7,
    "html_url": "https://github.com/example/repo/issues/7",
    "state": "open",
    "title": "Example",
    "body": None,
    "labels": [{"name": "bug"}],
    "created_at": "2026-09-01T00:00:00Z",
    "updated_at": "2026-09-01T00:00:00Z",
}
COMMENT = {
    "id": 8,
    "body": "A comment",
    "user": {"login": "example"},
    "created_at": "2026-09-01T00:00:00Z",
    "html_url": "https://github.com/example/repo/issues/7#issuecomment-8",
}


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(
        httpx, "request", Mock(side_effect=AssertionError("Live HTTP forbidden"))
    )
    return TestClient(app)


@pytest.mark.parametrize(
    "method,path,payload",
    [
        ("post", "/issues", {}),
        ("post", "/issues", {"title": "   "}),
        ("patch", "/issues/7", {"title": ""}),
        ("patch", "/issues/7", {"title": "x" * 257}),
        ("patch", "/issues/7", {"state": "invalid"}),
        ("post", "/issues/7/comments", {"body": "\t "}),
    ],
)
def test_invalid_bodies_return_400_without_upstream(client, method, path, payload):
    assert getattr(client, method)(path, json=payload).status_code == 400


@pytest.mark.parametrize(
    "query", ["state=invalid", "page=0", "page=-1", "per_page=0", "per_page=101"]
)
def test_invalid_query_returns_400(client, query):
    assert client.get(f"/issues?{query}").status_code == 400


def test_create_trims_title_and_sets_location(client, monkeypatch):
    create = Mock(return_value=httpx.Response(201, json=ISSUE))
    monkeypatch.setattr(github_client, "create_issue", create)
    response = client.post("/issues", json={"title": "  Example  "})
    assert response.status_code == 201
    assert response.headers["Location"] == "/issues/7"
    assert response.json()["labels"] == ["bug"]
    assert create.call_args.args[0]["title"] == "Example"


def test_update_and_get_issue(client, monkeypatch):
    update = Mock(return_value=httpx.Response(200, json={**ISSUE, "state": "closed"}))
    monkeypatch.setattr(github_client, "update_issue", update)
    monkeypatch.setattr(
        github_client, "get_issue", lambda n: httpx.Response(200, json=ISSUE)
    )
    assert client.get("/issues/7").json()["number"] == 7
    assert (
        client.patch(
            "/issues/7", json={"title": " Example ", "state": "closed"}
        ).json()["state"]
        == "closed"
    )
    assert update.call_args.args == (7, {"title": "Example", "state": "closed"})


def test_list_preserves_pagination(client, monkeypatch):
    link = '<https://api.github.com/repos/example/repo/issues?page=3>; rel="next"'
    listing = Mock(
        return_value=httpx.Response(200, json=[ISSUE], headers={"Link": link})
    )
    monkeypatch.setattr(github_client, "list_issues", listing)
    response = client.get("/issues?state=all&page=2&per_page=100&labels=bug")
    assert response.status_code == 200
    assert response.headers["Link"] == link
    assert listing.call_args.args[0] == {
        "state": "all",
        "page": 2,
        "per_page": 100,
        "labels": "bug",
    }


def test_comment_create_and_fetch(client, monkeypatch):
    create = Mock(return_value=httpx.Response(201, json=COMMENT))
    monkeypatch.setattr(github_client, "create_comment", create)
    monkeypatch.setattr(
        github_client,
        "list_comments",
        lambda n, params: httpx.Response(
            200, json=[COMMENT], headers={"Link": "next-page"}
        ),
        raising=False,
    )
    response = client.post("/issues/7/comments", json={"body": " A comment "})
    assert response.status_code == 201
    assert response.headers["Location"] == COMMENT["html_url"]
    assert create.call_args.args[1] == {"body": "A comment"}
    listing = client.get("/issues/7/comments?page=2&per_page=10")
    assert listing.status_code == 200
    assert listing.json()[0]["user"] == "example"
    assert listing.headers["Link"] == "next-page"


@pytest.mark.parametrize("status", [401, 403, 404, 429, 503])
def test_errors_preserve_status_and_retry_header(client, monkeypatch, status):
    monkeypatch.setattr(
        github_client,
        "get_issue",
        lambda n: httpx.Response(
            status, json={"message": "upstream error"}, headers={"Retry-After": "60"}
        ),
    )
    response = client.get("/issues/7")
    assert response.status_code == status
    assert response.headers["Retry-After"] == "60"
    assert "error" in response.json()


def test_contract_uses_response_models_and_examples(client):
    spec = client.get("/openapi.json").json()
    for path, method, status, schema in [
        ("/issues", "post", "201", "IssueResponse"),
        ("/issues/{issue_number}/comments", "post", "201", "CommentResponse"),
    ]:
        responses = spec["paths"][path][method]["responses"]
        assert responses[status]["content"]["application/json"]["schema"][
            "$ref"
        ].endswith(schema)
        assert "429" in responses and "400" in responses
    assert spec["components"]["schemas"]["IssueResponse"]["examples"]


def test_github_validation_error_maps_to_400(client, monkeypatch):
    monkeypatch.setattr(
        github_client,
        "create_issue",
        Mock(return_value=httpx.Response(422, json={"message": "Validation Failed"})),
    )
    response = client.post("/issues", json={"title": "Example"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Validation Failed"


@pytest.mark.parametrize(
    "method,path,payload,upstream_method",
    [
        ("post", "/issues", {"title": "Example"}, "create_issue"),
        ("get", "/issues", None, "list_issues"),
        ("patch", "/issues/7", {"state": "open"}, "update_issue"),
        ("post", "/issues/7/comments", {"body": "Example"}, "create_comment"),
        ("get", "/issues/7/comments", None, "list_comments"),
    ],
)
def test_every_route_preserves_upstream_error(
    client, monkeypatch, method, path, payload, upstream_method
):
    monkeypatch.setattr(
        github_client,
        upstream_method,
        Mock(return_value=httpx.Response(404, text="not JSON")),
    )
    response = client.request(
        method, path, **({"json": payload} if payload is not None else {})
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "GitHub returned an error"
