from sqlalchemy.orm import Session
from datetime import datetime
from app.models import Enrollment, User, Event
from app.crud import get_user_by_email, get_event, create_user, create_event as crud_create_event, enroll_user_in_event
from app.schemas import UserCreate, EventCreate
from app.auth import get_password_hash, verify_password

def check_event_capacity(event) -> bool:
    """Check if the event has reached its maximum capacity."""
    return len(event.participants) < event.max_pax

def check_user_conflict(db: Session, user_id: int, event_date: datetime) -> bool:
    """Check if the user has any conflicting events at the same time."""
    user_events = db.query(Enrollment).filter(Enrollment.user_id == user_id).all()
    for enrollment in user_events:
        if enrollment.event.date == event_date:
            return False  # Conflict found
    return True  # No conflicts

def enroll_user(db: Session, user_id: int, event_id: int):
    """Enroll the user in an event after checking capacity and conflicts."""
    event = get_event(db, event_id)
    if not check_event_capacity(event):
        return None  # Event is full
    
    if not check_user_conflict(db, user_id, event.date):
        return None  # Conflict found

    # All checks passed; proceed to enroll
    return enroll_user_in_event(db, user_id, event_id)

def create_event(db: Session, event_data: EventCreate, organizer_id: int):
    """Create a new event if there are no conflicts with existing events."""
    # Check for conflicts (this could be an additional function if needed)
    existing_events = db.query(Event).filter(
        Event.venue == event_data.venue,
        Event.room == event_data.room,
        Event.date == event_data.date
    ).all()
    if existing_events:
        return None  # Conflict found

    return crud_create_event(db, event_data, organizer_id)

def check_user_exists(db: Session, email: str) -> bool:
    """Check if a user with the given email already exists."""
    return get_user_by_email(db, email) is not None

def authenticate_user(db: Session, email: str, password: str) -> User:
    """Authenticate a user by email and password."""
    user = get_user_by_email(db, email=email)
    if user and verify_password(password, user.hashed_password):
        return user
    return None

def register_user(db: Session, user_data: UserCreate):
    """Register a new user by hashing their password and saving it to the database."""
    user_data.password = get_password_hash(user_data.password)
    return create_user(db, user_data)

def get_user(db: Session, email: str):
    """Retrieve a user by email without verifying the password."""
    return get_user_by_email(db, email)