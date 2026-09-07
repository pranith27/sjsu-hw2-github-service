
from fastapi import APIRouter, Header, HTTPException, Request, Response

from app.logger import logger
from app.storage import get_events, save_event
from app.webhook import verify_signature

router = APIRouter(
    prefix="/webhook",
    tags=["Webhook"],
)


@router.post("", status_code=204)
async def github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(default=None),
    x_github_event: str = Header(default=None),
    x_github_delivery: str = Header(default=None),
):
    body = await request.body()

    # Verify GitHub webhook signature
    if not verify_signature(body, x_hub_signature_256):
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook signature",
        )

    # Allow only supported GitHub events
    if x_github_event not in ["ping", "issues", "issue_comment"]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported webhook event",
        )

    payload = await request.json()

    action = payload.get("action")
    issue_number = payload.get("issue", {}).get("number")

    # Store webhook event
    save_event(
        x_github_delivery,
        x_github_event,
        action,
        issue_number,
    )

    # Log webhook summary
    logger.info(
        "Webhook received | Delivery=%s | Event=%s | Action=%s | Issue=%s",
        x_github_delivery,
        x_github_event,
        action,
        issue_number,
    )

    return Response(status_code=204)


@router.get("/events")
def events():
    """
    Return recently processed webhook events.
    """
    return get_events()