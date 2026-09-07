"""
CMPE 272
Webhook Routes

Author: Pranith Varma
"""

from fastapi import APIRouter, Header, HTTPException, Request, Response

from app.webhook import verify_signature
from app.storage import save_event, get_events

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

    if not verify_signature(body, x_hub_signature_256):
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook signature",
        )

    if x_github_event not in [
        "ping",
        "issues",
        "issue_comment",
    ]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported webhook event",
        )

    payload = await request.json()

    action = payload.get("action")

    issue_number = None

    if "issue" in payload:
        issue_number = payload["issue"]["number"]

    save_event(
        x_github_delivery,
        x_github_event,
        action,
        issue_number,
    )

    print("\n========== WEBHOOK RECEIVED ==========")
    print("Delivery:", x_github_delivery)
    print("Event:", x_github_event)
    print("Action:", action)

    if "issue" in payload:
        print("Issue:", payload["issue"]["title"])

    print("======================================\n")

    return Response(status_code=204)


@router.get("/events")
def events():
    return get_events()