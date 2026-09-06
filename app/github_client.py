"""
CMPE 272 - Homework #2
GitHub REST API Client

Author: Pranith Varma
"""

import httpx
from app.config import settings


class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _request(self, method: str, endpoint: str, **kwargs):
        url = f"{self.BASE_URL}{endpoint}"

        print("\n========== GITHUB REQUEST ==========")
        print("Method:", method)
        print("URL:", url)
        print("Authorization:", self.headers["Authorization"][:30] + "...")
        print("Payload:", kwargs.get("json"))
        print("====================================")

        response = httpx.request(
            method,
            url,
            headers=self.headers,
            timeout=30,
            **kwargs,
        )

        print("\n========== GITHUB RESPONSE ==========")
        print("Status:", response.status_code)
        print("Body:", response.text)
        print("=====================================\n")

        return response

    def create_issue(self, payload):
        return self._request(
            "POST",
            f"/repos/{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}/issues",
            json=payload,
        )

    def list_issues(self, params):
        return self._request(
            "GET",
            f"/repos/{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}/issues",
            params=params,
        )

    def get_issue(self, issue_number):
        return self._request(
            "GET",
            f"/repos/{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}/issues/{issue_number}",
        )

    def update_issue(self, issue_number, payload):
        return self._request(
            "PATCH",
            f"/repos/{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}/issues/{issue_number}",
            json=payload,
        )

    def create_comment(self, issue_number, payload):
        return self._request(
            "POST",
            f"/repos/{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}/issues/{issue_number}/comments",
            json=payload,
        )


github_client = GitHubClient()