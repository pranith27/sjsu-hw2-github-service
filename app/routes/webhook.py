"""
CMPE 272
Webhook Routes

Author: Pranith Varma
"""

from fastapi import APIRouter, Header, HTTPException, Request

from app.webhook import verify_signature

router = APIRouter(
    prefix="/webhook",
    tags=["Webhook"],
)


@router.post("")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(default=None),
    x_github_event: str = Header(default=None),
):
    body = await request.body()

    if not verify_signature(body, x_hub_signature_256):
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook signature",
        )

    payload = await request.json()

    print("\n========== WEBHOOK RECEIVED ==========")
    print("Event:", x_github_event)

    if "action" in payload:
        print("Action:", payload["action"])

    if "issue" in payload:
        print("Issue:", payload["issue"]["title"])

    print("======================================\n")

    return {
        "status": "received",
        "event": x_github_event,
    }