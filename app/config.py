"""
CMPE 272 - Homework #2
GitHub Issues Service

Author: Pranith Varma
"""

from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GITHUB_OWNER = os.getenv("GITHUB_OWNER")
    GITHUB_REPO = os.getenv("GITHUB_REPO")
    WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
    PORT = int(os.getenv("PORT", 8000))

settings = Settings()