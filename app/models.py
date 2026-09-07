"""Request and response schemas for the GitHub service.

Original author: Pranith Varma. Requirements corrections assisted by Codex.
"""

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

Title = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=256)
]
CommentBody = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class CreateIssueRequest(BaseModel):
    title: Title
    body: str | None = None
    labels: list[str] | None = Field(default_factory=list)
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"title": "Fix login", "body": "Steps to reproduce", "labels": ["bug"]}
            ]
        }
    )


class UpdateIssueRequest(BaseModel):
    title: Title | None = None
    body: str | None = None
    state: Literal["open", "closed"] | None = None
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"title": "Fixed login", "state": "closed"}]}
    )


class CreateCommentRequest(BaseModel):
    body: CommentBody
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"body": "Confirmed the fix."}]}
    )


class IssueResponse(BaseModel):
    number: int
    html_url: str
    state: str
    title: str
    body: str | None
    labels: list[str]
    created_at: str
    updated_at: str
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "number": 1,
                    "html_url": "https://github.com/example/repo/issues/1",
                    "state": "open",
                    "title": "Fix login",
                    "body": None,
                    "labels": ["bug"],
                    "created_at": "2026-09-01T00:00:00Z",
                    "updated_at": "2026-09-01T00:00:00Z",
                }
            ]
        }
    )


class CommentResponse(BaseModel):
    id: int
    body: str
    user: str
    created_at: str
    html_url: str
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": 2,
                    "body": "Confirmed the fix.",
                    "user": "example",
                    "created_at": "2026-09-01T00:00:00Z",
                    "html_url": "https://github.com/example/repo/issues/1#issuecomment-2",
                }
            ]
        }
    )


class ErrorResponse(BaseModel):
    error: str
    detail: Any = None
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"error": "not_found", "detail": "Not Found"}]}
    )
