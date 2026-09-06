"""
CMPE 272 - Homework #2
Pydantic Models

Author: Pranith Varma
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class CreateIssueRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=256)
    body: Optional[str] = None
    labels: Optional[List[str]] = []


class UpdateIssueRequest(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    state: Optional[str] = Field(default=None, pattern="^(open|closed)$")


class CreateCommentRequest(BaseModel):
    body: str = Field(..., min_length=1)


class IssueResponse(BaseModel):
    number: int
    html_url: str
    state: str
    title: str
    body: Optional[str]
    labels: List[str]
    created_at: str
    updated_at: str


class CommentResponse(BaseModel):
    id: int
    body: str
    user: str
    created_at: str
    html_url: str


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None