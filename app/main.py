from fastapi import FastAPI
from app.logger import logger

from app.routes.health import router as health_router
from app.routes.issues import router as issues_router
from app.config import settings
from app.routes.webhook import router as webhook_router

print(settings.GITHUB_TOKEN[:20])

app = FastAPI(
    title="GitHub Issues Service API",
    version="1.0.0",
    description="""
A production-style REST API wrapper around GitHub Issues.

Features:
- Issue CRUD
- Comments
- GitHub Webhooks
- OpenAPI
- Docker
- Unit Tests
"""
)

app.include_router(health_router)
app.include_router(issues_router)
app.include_router(webhook_router)


@app.on_event("startup")
async def startup():
    logger.info("GitHub Issues Service Started")