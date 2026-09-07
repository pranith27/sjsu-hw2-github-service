"""GitHub issue routes. Original author: Pranith Varma; corrections assisted by Codex."""

from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException, Query, Response

from app.github_client import github_client
from app.models import (
    CommentResponse,
    CreateCommentRequest,
    CreateIssueRequest,
    ErrorResponse,
    IssueResponse,
    UpdateIssueRequest,
)

ERRORS = {
    code: {"model": ErrorResponse, "description": description}
    for code, description in {
        400: "Invalid request",
        401: "GitHub authentication failed",
        403: "GitHub access denied",
        404: "Resource not found",
        429: "GitHub rate limit exceeded",
        500: "Server error",
        503: "GitHub temporarily unavailable",
    }.items()
}
for code in (429, 503):
    ERRORS[code]["headers"] = {
        "Retry-After": {
            "description": "Delay in seconds or HTTP date before retrying",
            "schema": {"type": "string"},
        }
    }
PAGINATION = {
    200: {
        "headers": {
            "Link": {
                "description": "GitHub pagination links",
                "schema": {"type": "string"},
            }
        }
    }
}
LOCATION = {
    201: {
        "headers": {
            "Location": {
                "description": "Location of the created resource",
                "schema": {"type": "string"},
            }
        }
    }
}
Page = Annotated[int, Query(ge=1)]
PageSize = Annotated[int, Query(ge=1, le=100)]
router = APIRouter(prefix="/issues", tags=["Issues"], responses=ERRORS)


def format_issue(issue):
    return {
        "number": issue["number"],
        "html_url": issue["html_url"],
        "state": issue["state"],
        "title": issue["title"],
        "body": issue.get("body"),
        "labels": [label["name"] for label in issue.get("labels", [])],
        "created_at": issue["created_at"],
        "updated_at": issue["updated_at"],
    }


def format_comment(comment):
    return {
        "id": comment["id"],
        "body": comment["body"],
        "user": comment["user"]["login"],
        "created_at": comment["created_at"],
        "html_url": comment["html_url"],
    }


def github_error(response):
    try:
        detail = response.json().get("message") or "GitHub rejected the request"
    except (ValueError, AttributeError):
        detail = "GitHub returned an error"
    headers = {
        key: response.headers[key]
        for key in ("Retry-After",)
        if key in response.headers
    }
    raise HTTPException(
        status_code=400 if response.status_code == 422 else response.status_code,
        detail=detail,
        headers=headers,
    )


@router.post("", status_code=201, response_model=IssueResponse, responses=LOCATION)
def create_issue(payload: CreateIssueRequest, response: Response):
    upstream = github_client.create_issue(payload.model_dump(exclude_none=True))
    if upstream.status_code != 201:
        github_error(upstream)
    issue = upstream.json()
    response.headers["Location"] = f"/issues/{issue['number']}"
    return format_issue(issue)


@router.get("", response_model=list[IssueResponse], responses=PAGINATION)
def list_issues(
    response: Response,
    state: Literal["open", "closed", "all"] = "open",
    labels: str | None = None,
    page: Page = 1,
    per_page: PageSize = 30,
):
    params = {"state": state, "page": page, "per_page": per_page}
    if labels:
        params["labels"] = labels
    upstream = github_client.list_issues(params)
    if upstream.status_code != 200:
        github_error(upstream)
    if "Link" in upstream.headers:
        response.headers["Link"] = upstream.headers["Link"]
    return [format_issue(issue) for issue in upstream.json()]


@router.get("/{issue_number}", response_model=IssueResponse)
def get_issue(issue_number: int):
    upstream = github_client.get_issue(issue_number)
    if upstream.status_code != 200:
        github_error(upstream)
    return format_issue(upstream.json())


@router.patch("/{issue_number}", response_model=IssueResponse)
def update_issue(issue_number: int, payload: UpdateIssueRequest):
    upstream = github_client.update_issue(
        issue_number, payload.model_dump(exclude_none=True)
    )
    if upstream.status_code != 200:
        github_error(upstream)
    return format_issue(upstream.json())


@router.post(
    "/{issue_number}/comments",
    status_code=201,
    response_model=CommentResponse,
    responses=LOCATION,
)
def create_comment(
    issue_number: int, payload: CreateCommentRequest, response: Response
):
    upstream = github_client.create_comment(issue_number, payload.model_dump())
    if upstream.status_code != 201:
        github_error(upstream)
    comment = upstream.json()
    response.headers["Location"] = comment["html_url"]
    return format_comment(comment)


@router.get(
    "/{issue_number}/comments",
    response_model=list[CommentResponse],
    responses=PAGINATION,
)
def list_comments(
    issue_number: int, response: Response, page: Page = 1, per_page: PageSize = 30
):
    upstream = github_client.list_comments(
        issue_number, {"page": page, "per_page": per_page}
    )
    if upstream.status_code != 200:
        github_error(upstream)
    if "Link" in upstream.headers:
        response.headers["Link"] = upstream.headers["Link"]
    return [format_comment(comment) for comment in upstream.json()]
