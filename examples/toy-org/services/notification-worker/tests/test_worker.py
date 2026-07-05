"""Tests for the notification-worker EventQueue."""

from notification_worker.worker import EventQueue


def test_user_signup_returns_welcome_email() -> None:
    """A user_signup event produces a welcome_email notification."""
    queue = EventQueue()
    result = queue.process_event("user_signup", {"user_id": "42"})
    assert result == {"notification": "welcome_email", "user_id": "42"}


def test_invoice_created_returns_invoice_receipt() -> None:
    """An invoice_created event produces an invoice_receipt notification."""
    queue = EventQueue()
    result = queue.process_event("invoice_created", {"invoice_id": "inv-001"})
    assert result == {"notification": "invoice_receipt", "invoice_id": "inv-001"}


def test_unknown_event_type_returns_unknown_event() -> None:
    """An unrecognised event type returns an unknown_event notification."""
    queue = EventQueue()
    result = queue.process_event("order_shipped", {"order_id": "123"})
    assert result == {"notification": "unknown_event", "type": "order_shipped"}


def test_get_pending_notifications_returns_all_processed() -> None:
    """get_pending_notifications returns every notification processed so far."""
    queue = EventQueue()
    queue.process_event("user_signup", {"user_id": "1"})
    queue.process_event("invoice_created", {"invoice_id": "inv-1"})
    pending = queue.get_pending_notifications()
    assert len(pending) == 2
    assert {"notification": "welcome_email", "user_id": "1"} in pending
    assert {"notification": "invoice_receipt", "invoice_id": "inv-1"} in pending


def test_multiple_events_accumulate_correctly() -> None:
    """Processing many events preserves order and count."""
    queue = EventQueue()
    results: list[dict[str, object]] = []
    for i in range(5):
        result = queue.process_event("user_signup", {"user_id": str(i)})
        results.append(result)

    pending = queue.get_pending_notifications()
    assert len(pending) == 5
    assert results == pending
    for i, entry in enumerate(pending):
        assert entry == {"notification": "welcome_email", "user_id": str(i)}
