from datetime import UTC, datetime
from threading import Lock

events = []
processed_deliveries = set()
_lock = Lock()


def save_event(delivery_id: str, event: str, action: str | None,
               issue_number: int | None) -> bool:
    """Atomically store each delivery/action once; return whether it was new."""
    key = (delivery_id, action)
    with _lock:
        if key in processed_deliveries:
            return False
        processed_deliveries.add(key)
        events.append({
            'delivery_id': delivery_id,
            'event': event,
            'action': action,
            'issue_number': issue_number,
            'timestamp': datetime.now(UTC).isoformat(),
        })
    return True


def get_events(limit: int = 20):
    """Return a snapshot of recent events from this process's in-memory store."""
    with _lock:
        return [event.copy() for event in events[-limit:]] if limit > 0 else []
