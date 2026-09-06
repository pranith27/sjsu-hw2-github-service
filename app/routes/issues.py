"""
CMPE 272
GitHub Issues Routes

Author: Pranith Varma
"""

from fastapi import APIRouter, HTTPException, Response
from typing import Optional

from app.github_client import github_client
from app.models import (
    CreateIssueRequest,
    UpdateIssueRequest,
    CreateCommentRequest,
)

router = APIRouter(
    prefix="/issues",
    tags=["Issues"]
)


def format_issue(issue):
    return {
        "number": issue["number"],
        "html_url": issue["html_url"],
        "state": issue["state"],
        "title": issue["title"],
        "body": issue.get("body"),
        "labels": [
            label["name"]
            for label in issue.get("labels", [])
        ],
        "created_at": issue["created_at"],
        "updated_at": issue["updated_at"],
    }


def github_error(response):
    try:
        detail = response.json().get("message")
    except Exception:
        detail = response.text

    raise HTTPException(
        status_code=response.status_code,
        detail=detail,
    )
@router.post("", status_code=201)
def create_issue(
    payload: CreateIssueRequest,
    response: Response,
):

    github_response = github_client.create_issue(
        payload.model_dump(exclude_none=True)
    )

    if github_response.status_code != 201:
        github_error(github_response)

    issue = github_response.json()

    response.headers["Location"] = f"/issues/{issue['number']}"

    return format_issue(issue)
@router.get("")
def list_issues(
    state: str = "open",
    labels: Optional[str] = None,
    page: int = 1,
    per_page: int = 30,
    response: Response = None,
):

    params = {
        "state": state,
        "page": page,
        "per_page": per_page,
    }

    if labels:
        params["labels"] = labels

    github_response = github_client.list_issues(params)

    if github_response.status_code != 200:
        github_error(github_response)

    if "Link" in github_response.headers:
        response.headers["Link"] = github_response.headers["Link"]

    issues = github_response.json()

    return [
        format_issue(issue)
        for issue in issues
    ]
@router.get("/{issue_number}")
def get_issue(issue_number: int):

    github_response = github_client.get_issue(issue_number)

    if github_response.status_code != 200:
        github_error(github_response)

    issue = github_response.json()

    return format_issue(issue)
@router.patch("/{issue_number}")
def update_issue(
    issue_number: int,
    payload: UpdateIssueRequest,
):

    github_response = github_client.update_issue(
        issue_number,
        payload.model_dump(exclude_none=True),
    )

    if github_response.status_code != 200:
        github_error(github_response)

    issue = github_response.json()

    return format_issue(issue)
@router.post("/{issue_number}/comments", status_code=201)
def create_comment(
    issue_number: int,
    payload: CreateCommentRequest,
):

    github_response = github_client.create_comment(
        issue_number,
        payload.model_dump(),
    )

    if github_response.status_code != 201:
        github_error(github_response)

    comment = github_response.json()

    return {
        "id": comment["id"],
        "body": comment["body"],
        "user": comment["user"]["login"],
        "created_at": comment["created_at"],
        "html_url": comment["html_url"],
    }