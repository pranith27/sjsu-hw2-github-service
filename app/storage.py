
from datetime import UTC, datetime

events = []
processed_deliveries = set()


def save_event(
    delivery_id: str,
    event: str,
    action: str,
    issue_number: int | None,
):
    """
    Store webhook events.

    Duplicate GitHub deliveries are ignored using
    the delivery identifier.
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


def get_events(limit: int = 20):
    """
    Return the latest processed webhook events.
    """

    return events[-limit:]