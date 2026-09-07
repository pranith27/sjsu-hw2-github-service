import math
import time
from email.utils import parsedate_to_datetime

import httpx

from app.config import settings
from app.logger import logger


class GitHubClient:
    """
    Wrapper around the GitHub REST API for managing repository issues.
    """

    BASE_URL = "https://api.github.com"

    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _request(self, method: str, endpoint: str, **kwargs):
        """
        Send an HTTP request to the GitHub REST API.
        """

        url = f"{self.BASE_URL}{endpoint}"

        logger.info("%s %s", method, url)

        # Only reads are retried: a failed write may already have reached GitHub.
        for attempt in range(3):
            try:
                response = httpx.request(
                    method=method, url=url, headers=self.headers, timeout=30, **kwargs
                )
            except httpx.RequestError:
                return httpx.Response(
                    503,
                    headers={"Retry-After": "1"},
                    json={
                        "message": "GitHub could not be reached. For a write, check its outcome before retrying."
                    },
                )

            logger.info("GitHub Response: %s", response.status_code)
            rate_limited = response.status_code == 429 or (
                response.status_code == 403
                and (
                    response.headers.get("X-RateLimit-Remaining") == "0"
                    or "Retry-After" in response.headers
                    or "rate limit" in response.text.lower()
                )
            )
            if rate_limited:
                response.status_code = 429
            if not (rate_limited or response.status_code >= 500):
                return response

            delay = 0.25 * 2**attempt
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                try:
                    delay = float(retry_after)
                except ValueError:
                    try:
                        delay = max(
                            0,
                            parsedate_to_datetime(retry_after).timestamp()
                            - time.time(),
                        )
                    except (ValueError, TypeError, OverflowError):
                        delay = 60
                        retry_after = None
            elif rate_limited:
                try:
                    delay = max(
                        1, float(response.headers["X-RateLimit-Reset"]) - time.time()
                    )
                except (KeyError, ValueError):
                    delay = 60
            if not math.isfinite(delay):
                delay = 60
                retry_after = None
            if delay < 0:
                delay = 60
                retry_after = None
            # Surface long waits to the caller instead of occupying a request worker.
            if method != "GET" or attempt == 2 or delay > 1:
                if not retry_after:
                    response.headers["Retry-After"] = str(max(1, math.ceil(delay)))
                return response
            time.sleep(delay)
        return response

    def create_issue(self, payload: dict):
        """Create a new GitHub issue."""

        return self._request(
            "POST",
            f"/repos/{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}/issues",
            json=payload,
        )

    def list_issues(self, params: dict):
        """Retrieve repository issues."""

        return self._request(
            "GET",
            f"/repos/{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}/issues",
            params=params,
        )

    def get_issue(self, issue_number: int):
        """Retrieve a single GitHub issue."""

        return self._request(
            "GET",
            f"/repos/{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}/issues/{issue_number}",
        )

    def update_issue(
        self,
        issue_number: int,
        payload: dict,
    ):
        """Update an existing GitHub issue."""

        return self._request(
            "PATCH",
            f"/repos/{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}/issues/{issue_number}",
            json=payload,
        )

    def create_comment(
        self,
        issue_number: int,
        payload: dict,
    ):
        """Add a comment to a GitHub issue."""

        return self._request(
            "POST",
            f"/repos/{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}/issues/{issue_number}/comments",
            json=payload,
        )

    def list_comments(self, issue_number: int, params: dict):
        """Retrieve issue comments while preserving GitHub pagination."""
        return self._request(
            "GET",
            f"/repos/{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}/issues/{issue_number}/comments",
            params=params,
        )


github_client = GitHubClient()
