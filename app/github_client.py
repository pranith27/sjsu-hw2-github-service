"""
CMPE 272 - Homework #2
GitHub Issues Service

Author: Pranith Varma
"""

import requests
from app.config import settings

BASE_URL = "https://api.github.com"


class GitHubClient:

    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

    def create_issue(self, title, body=None, labels=None):

        url = f"{BASE_URL}/repos/{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}/issues"

        payload = {
            "title": title,
            "body": body,
            "labels": labels or []
        }

        response = requests.post(
            url,
            headers=self.headers,
            json=payload
        )

        return response


github = GitHubClient()