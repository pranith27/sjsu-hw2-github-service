
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

        response = httpx.request(
            method=method,
            url=url,
            headers=self.headers,
            timeout=30,
            **kwargs,
        )

        logger.info("GitHub Response: %s", response.status_code)

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


github_client = GitHubClient()