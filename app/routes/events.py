"""
CMPE 272
Webhook Event Store

Author: Pranith Varma
"""

from datetime import datetime

events = []
processed_deliveries = set()


def save_event(
    delivery_id: str,
    event: str,
    action: str,
    issue_number: int | None,
):
    key = (delivery_id, event)

    # Prevent processing the same webhook twice
    if key in processed_deliveries:
        return

    processed_deliveries.add(key)

    events.append(
        {
            "delivery_id": delivery_id,
            "event": event,
            "action": action,
            "issue_number": issue_number,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    )


def get_events(limit: int = 20):
    return events[-limit:]