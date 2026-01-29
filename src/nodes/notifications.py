import logging

from src.deps import get_supabase
from src.state import BookState
from src.notifications.email import send_email
from src.notifications.teams import send_teams_message

logger = logging.getLogger(__name__)


def notify(state: BookState) -> BookState:
    """
    Simple notification node. Uses `state.control["event"]`
    to decide what to send.
    """
    event = state.control.get("event")
    if not event:
        return state

    logger.info(f"Sending notification: {event}")

    supabase = get_supabase()

    subject = f"[Book System] Event: {event}"
    body = f"Event: {event}\nBook ID: {state.book_id}\nTitle: {state.title}"

    # Send actual notifications
    send_email(subject, body)
    send_teams_message(body)

    # Log to DB
    supabase.table("notifications").insert(
        {
            "book_id": state.book_id,
            "type": event,
            "channel": "email+teams",
            "payload": {"subject": subject, "body": body},
            "status": "sent",
        }
    ).execute()

    return state

