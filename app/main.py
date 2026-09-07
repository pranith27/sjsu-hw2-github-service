
from fastapi import FastAPI

from app.logger import logger
from app.routes.health import router as health_router
from app.routes.issues import router as issues_router
from app.routes.webhook import router as webhook_router


app = FastAPI(
    title="GitHub Issues Service API",
    version="1.0.0",
    summary="REST API wrapper for GitHub Issues",
    description="""
A production-style REST API built with **FastAPI** that wraps the GitHub REST API
for managing issues and comments within a single GitHub repository.

## Features

- Create GitHub Issues
- List Repository Issues
- Retrieve Individual Issues
- Update Issue Title, Body, and State
- Add Comments to Issues
- Verify GitHub Webhook Signatures (HMAC SHA-256)
- Process Issue and Issue Comment Events
- Store Webhook Events for Debugging
- OpenAPI 3.1 Documentation
- Docker Support
- Automated Unit Tests

Developed as part of **CMPE 272 - Homework #2**.
""",
)


# ---------------------------------------------------------
# Register API Routes
# ---------------------------------------------------------

app.include_router(health_router)
app.include_router(issues_router)
app.include_router(webhook_router)


# ---------------------------------------------------------
# Root Endpoint
# ---------------------------------------------------------

@app.get(
    "/",
    tags=["Health"],
    summary="Root Endpoint",
    description="Returns basic information about the GitHub Issues Service API.",
)
def root():
    return {
        "message": "GitHub Issues Service API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health_check": "/healthz",
    }


# ---------------------------------------------------------
# Health Check Endpoint
# ---------------------------------------------------------

@app.get(
    "/healthz",
    tags=["Health"],
    summary="Health Check",
    description="Returns the current health status of the application.",
)
def health():
    return {
        "status": "healthy",
        "service": "GitHub Issues Service",
        "version": "1.0.0",
    }


# ---------------------------------------------------------
# Startup Event
# ---------------------------------------------------------

@app.on_event("startup")
async def startup():
    logger.info("GitHub Issues Service API started successfully.")