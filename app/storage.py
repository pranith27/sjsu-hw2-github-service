"""
CMPE 272
Webhook Event Storage

Author: Pranith Varma
"""

from datetime import datetime, UTC

events = []
processed_deliveries = set()


def save_event(
    delivery_id,
    event,
    action,
    issue_number,
):
    """
    Save webhook event.
    Duplicate deliveries are ignored.
    """

    if delivery_id in processed_deliveries:
        return

    processed_deliveries.add(delivery_id)

    events.append(
        {
            "delivery_id": delivery_id,
            "event": event,
            "action": action,
            "issue_number": issue_number,
            "timestamp": datetime.now(UTC).isoformat(),
        }
    )


def get_events():
    return events