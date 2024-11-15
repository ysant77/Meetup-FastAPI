from sqlalchemy.orm import Session
from datetime import datetime
from app.models import Enrollment, User, Event
from app.crud import (
    delete_enrollment, delete_user, get_all_events, get_all_users, get_event_by_id,
    get_user_by_email, get_event, create_user, create_event as crud_create_event,
    enroll_user_in_event, update_event as update_crud_event
)
from app.schemas import UserCreate, EventCreate
from app.auth import get_password_hash, verify_password

def check_event_capacity(event: Event) -> bool:
    """
    Check if an event has available capacity for additional participants.

    Args:
        event (Event): The event object to check capacity for.

    Returns:
        bool: True if the event has capacity, False if it is full.
    """
    return len(event.participants) < event.max_pax

def check_user_conflict(db: Session, user_id: int, event_date: datetime) -> bool:
    """
    Determine if a user has conflicting events on the same date and time.

    Args:
        db (Session): The database session.
        user_id (int): The unique identifier of the user.
        event_date (datetime): The date and time of the event to check against.

    Returns:
        bool: True if no conflicts exist, False if there is a conflict.
    """
    user_events = db.query(Enrollment).filter(Enrollment.user_id == user_id).all()
    for enrollment in user_events:
        if enrollment.event.date == event_date:
            return False  # Conflict found
    return True  # No conflicts

def enroll_user(db: Session, user_id: int, event_id: int) -> Enrollment:
    """
    Enroll a user in an event if capacity is available and there are no conflicts.

    Args:
        db (Session): The database session.
        user_id (int): The unique identifier of the user to enroll.
        event_id (int): The unique identifier of the event to enroll in.

    Returns:
        Enrollment: The enrollment object created if successful, otherwise None if capacity is full or a conflict exists.
    """
    event = get_event(db, event_id)
    if not check_event_capacity(event):
        return None  # Event is full

    if not check_user_conflict(db, user_id, event.date):
        return None  # Conflict found

    return enroll_user_in_event(db, user_id, event_id)

def create_event(db: Session, event_data: EventCreate, organizer_id: int) -> Event:
    """
    Create a new event if no scheduling conflicts exist with other events.

    Args:
        db (Session): The database session.
        event_data (EventCreate): The event data including name, date, venue, room, etc.
        organizer_id (int): The ID of the user organizing the event.

    Returns:
        Event: The created event object if successful, otherwise None if a conflict is found.
    """
    existing_events = db.query(Event).filter(
        Event.venue == event_data.venue,
        Event.room == event_data.room,
        Event.date == event_data.date
    ).all()
    if existing_events:
        return None  # Conflict found

    return crud_create_event(db, event_data, organizer_id)

def check_user_exists(db: Session, email: str) -> bool:
    """
    Check if a user with the specified email address already exists in the database.

    Args:
        db (Session): The database session.
        email (str): The email address to check.

    Returns:
        bool: True if the user exists, False otherwise.
    """
    return get_user_by_email(db, email) is not None

def authenticate_user(db: Session, email: str, password: str) -> User:
    """
    Authenticate a user by verifying the provided email and password.

    Args:
        db (Session): The database session.
        email (str): The user's email address.
        password (str): The user's plaintext password to verify.

    Returns:
        User: The authenticated user object if credentials are valid, otherwise None.
    """
    user = get_user_by_email(db, email=email)
    if user and verify_password(password, user.hashed_password):
        return user
    return None

def register_user(db: Session, user_data: UserCreate) -> User:
    """
    Register a new user by hashing their password and storing the user details in the database.

    Args:
        db (Session): The database session.
        user_data (UserCreate): The user data including name, email, plaintext password, and role.

    Returns:
        User: The newly created user object.
    """
    user_data.password = get_password_hash(user_data.password)
    return create_user(db, user_data)

def get_user(db: Session, email: str) -> User:
    """
    Retrieve a user by their email without requiring password verification.

    Args:
        db (Session): The database session.
        email (str): The user's email address.

    Returns:
        User: The user object if found, otherwise None.
    """
    return get_user_by_email(db, email)

def list_all_events(db: Session, show_participants: bool = False) -> list[dict]:
    """
    List all events with an optional parameter to include participants.

    Args:
        db (Session): The database session.
        show_participants (bool): Whether to include participant details in the event data.

    Returns:
        list[dict]: A list of dictionaries representing each event and, optionally, its participants.
    """
    events = get_all_events(db)
    event_list = []
    for event in events:
        event_data = {
            "id": event.id,
            "name": event.name,
            "date": event.date,
            "venue": event.venue,
            "room": event.room,
            "speaker": event.speaker,
            "description": event.description,
            "max_pax": event.max_pax,
            "organizer_id": event.organizer_id
        }
        if show_participants:
            event_data["participants"] = [{"id": p.user_id} for p in event.participants]
        event_list.append(event_data)
    return event_list

def update_event(db: Session, event_id: int, event_data: EventCreate, current_user: User) -> Event:
    """
    Update the details of an event if the user is authorized.

    Args:
        db (Session): The database session.
        event_id (int): The unique identifier of the event to update.
        event_data (EventCreate): The new event data to apply.
        current_user (User): The current user attempting the update.

    Returns:
        Event: The updated event object.

    Raises:
        ValueError: If the event is not found.
        PermissionError: If the user is not authorized to update the event.
    """
    event = get_event_by_id(db, event_id)
    if event is None:
        raise ValueError("Event not found")

    if current_user.role != "admin" and (current_user.id != event.organizer_id or event.date < datetime.now()):
        raise PermissionError("Not authorized to update this event")
    return update_crud_event(db, event, event_data)

def remove_event_organizer(db: Session, organizer_id: int) -> User:
    """
    Remove an event organizer from the system if they exist.

    Args:
        db (Session): The database session.
        organizer_id (int): The unique identifier of the organizer to remove.

    Returns:
        User: The removed organizer object if found.

    Raises:
        ValueError: If the organizer is not found or is not an event organizer.
    """
    organizer = delete_user(db, organizer_id)
    if not organizer or organizer.role != "event_organizer":
        raise ValueError("Organizer not found")
    return organizer

def unenroll_from_event(db: Session, event_id: int, user_id: int) -> Enrollment:
    """
    Remove a user's enrollment from an event.

    Args:
        db (Session): The database session.
        event_id (int): The unique identifier of the event.
        user_id (int): The unique identifier of the user to unenroll.

    Returns:
        Enrollment: The removed enrollment object if found.

    Raises:
        ValueError: If the enrollment is not found.
    """
    enrollment = delete_enrollment(db, event_id, user_id)
    if not enrollment:
        raise ValueError("Enrollment not found")
    return enrollment

def get_users(db: Session) -> list[User]:
    """
    Retrieve all users in the system.

    Args:
        db (Session): The database session.

    Returns:
        list[User]: A list of all user objects.
    """
    return get_all_users(db)
