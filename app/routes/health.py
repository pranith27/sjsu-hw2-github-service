
from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/")
def root():
    return {"message": "GitHub Issues Service API"}


@router.get("/healthz")
def health():
    return {
        "status": "healthy",
        "service": "GitHub Issues Service",
    }