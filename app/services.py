from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Event

def check_event_conflict(db: Session, venue: str, room: str, date: datetime) -> bool:
    """
    Check for event conflicts by verifying if another event exists in the same venue and room on the same date.
    
    Parameters:
    - db (Session): Database session.
    - venue (str): Venue name.
    - room (str): Room name within the venue.
    - date (datetime): Event date.

    Returns:
    - bool: True if no conflict, False if a conflict exists.
    """
    conflicting_events = db.query(Event).filter(
        Event.venue == venue,
        Event.room == room,
        Event.date == date
    ).all()
    return len(conflicting_events) == 0
