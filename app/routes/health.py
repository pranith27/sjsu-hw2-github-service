"""Health routes. Original: Pranith Varma; contract cleanup: Bernie Miao with AI assistance."""
from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/", response_model=dict[str, str])
def root():
    return {"message": "GitHub Issues Service API", "version": "1.0.0", "documentation": "/docs", "health_check": "/healthz"}


@router.get("/healthz", response_model=dict[str, str])
def health():
    return {"status": "healthy", "service": "GitHub Issues Service", "version": "1.0.0"}
