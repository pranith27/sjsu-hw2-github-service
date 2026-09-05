from fastapi import APIRouter

router = APIRouter(
    prefix="/issues",
    tags=["Issues"]
)


@router.get("/test")
def test_route():
    return {
        "message": "Issues router working!"
    }