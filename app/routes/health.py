from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/")
def root():
    return {
        "message": "GitHub Issues Service API",
        "version": "1.0.0"
    }


@router.get("/healthz")
def health():
    return {
        "status": "healthy"
    }