
from app.storage import save_event, get_events


def test_save_event():

    save_event(
        "delivery-1",
        "issues",
        "opened",
        1,
    )

    events = get_events()

    assert len(events) >= 1

    assert events[-1]["event"] == "issues"

    assert events[-1]["action"] == "opened"

    assert events[-1]["issue_number"] == 1