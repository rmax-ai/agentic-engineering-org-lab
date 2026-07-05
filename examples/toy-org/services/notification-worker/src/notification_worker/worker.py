"""Event-driven notification worker.

Processes transactional events from signup-api and billing-api,
returning structured notification descriptors.
"""

from __future__ import annotations

from typing import Any


class EventQueue:
    """In-memory event queue that processes events and tracks notifications."""

    def __init__(self) -> None:
        self._processed: list[dict[str, Any]] = []

    def process_event(self, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Process a single event and return a notification descriptor.

        Supported event types:
          - "user_signup"     → welcome_email notification
          - "invoice_created" → invoice_receipt notification
        """
        match event_type:
            case "user_signup":
                notification: dict[str, Any] = {
                    "notification": "welcome_email",
                    "user_id": payload["user_id"],
                }
            case "invoice_created":
                notification = {
                    "notification": "invoice_receipt",
                    "invoice_id": payload["invoice_id"],
                }
            case _:
                notification = {
                    "notification": "unknown_event",
                    "type": event_type,
                }

        self._processed.append(notification)
        return notification

    def get_pending_notifications(self) -> list[dict[str, Any]]:
        """Return all notifications processed so far."""
        return list(self._processed)
