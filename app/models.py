"""
CMPE 272 - Homework #2
Author: Pranith Varma
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class CreateIssueRequest(BaseModel):
    title: str = Field(..., min_length=1)
    body: Optional[str] = None
    labels: List[str] = []


class UpdateIssueRequest(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    state: Optional[Literal["open", "closed"]] = None


class CreateCommentRequest(BaseModel):
    body: str = Field(..., min_length=1)


class ErrorResponse(BaseModel):
    success: bool
    message: str


class HealthResponse(BaseModel):
    status: str


class IssueSummary(BaseModel):
    number: int
    title: str
    state: str
    html_url: str