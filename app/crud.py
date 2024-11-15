from sqlalchemy.orm import Session
from app.models import User, Event, Enrollment
from app.schemas import UserCreate, EventCreate

def get_user_by_email(db: Session, email: str) -> User:
    """
    Retrieve a user by their email address.

    Args:
        db (Session): The database session.
        email (str): The email address of the user to retrieve.

    Returns:
        User: The user object if found, otherwise None.
    """
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate) -> User:
    """
    Create a new user in the database.

    Args:
        db (Session): The database session.
        user (UserCreate): The user data including name, email, hashed password, and role.

    Returns:
        User: The created user object with an assigned ID.
    """
    db_user = User(
        name=user.name,
        email=user.email,
        hashed_password=user.password,  
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_event(db: Session, event_id: int) -> Event:
    """
    Retrieve an event by its unique identifier.

    Args:
        db (Session): The database session.
        event_id (int): The unique identifier of the event.

    Returns:
        Event: The event object if found, otherwise None.
    """
    return db.query(Event).filter(Event.id == event_id).first()

def create_event(db: Session, event: EventCreate, organizer_id: int) -> Event:
    """
    Create a new event in the database.

    Args:
        db (Session): The database session.
        event (EventCreate): The event data including name, date, venue, room, etc.
        organizer_id (int): The ID of the user organizing the event.

    Returns:
        Event: The created event object with an assigned ID.
    """
    db_event = Event(**event.model_dump(), organizer_id=organizer_id)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def enroll_user_in_event(db: Session, user_id: int, event_id: int) -> Enrollment:
    """
    Enroll a user in an event.

    Args:
        db (Session): The database session.
        user_id (int): The unique identifier of the user to enroll.
        event_id (int): The unique identifier of the event to enroll in.

    Returns:
        Enrollment: The created enrollment object linking the user to the event.
    """
    enrollment = Enrollment(user_id=user_id, event_id=event_id)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment

def get_event_by_id(db: Session, event_id: int) -> Event:
    """
    Retrieve an event by its unique identifier.

    Args:
        db (Session): The database session.
        event_id (int): The unique identifier of the event.

    Returns:
        Event: The event object if found, otherwise None.
    """
    return db.query(Event).filter(Event.id == event_id).first()

def update_event(db: Session, event: Event, event_data: EventCreate) -> Event:
    """
    Update an event's details in the database.

    Args:
        db (Session): The database session.
        event (Event): The event object to update.
        event_data (EventCreate): The new event data to apply.

    Returns:
        Event: The updated event object.
    """
    for key, value in event_data.model_dump().items():
        setattr(event, key, value)
    db.commit()
    db.refresh(event)
    return event

def delete_user(db: Session, user_id: int) -> User:
    """
    Delete a user by their unique identifier.

    Args:
        db (Session): The database session.
        user_id (int): The unique identifier of the user to delete.

    Returns:
        User: The deleted user object if found, otherwise None.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return user

def get_all_events(db: Session) -> list[Event]:
    """
    Retrieve all events from the database.

    Args:
        db (Session): The database session.

    Returns:
        list[Event]: A list of all event objects.
    """
    return db.query(Event).all()

def get_all_users(db: Session) -> list[User]:
    """
    Retrieve all users from the database.

    Args:
        db (Session): The database session.

    Returns:
        list[User]: A list of all user objects.
    """
    return db.query(User).all()

def delete_enrollment(db: Session, event_id: int, user_id: int) -> Enrollment:
    """
    Remove a user's enrollment from an event.

    Args:
        db (Session): The database session.
        event_id (int): The unique identifier of the event.
        user_id (int): The unique identifier of the user to unenroll.

    Returns:
        Enrollment: The deleted enrollment object if found, otherwise None.
    """
    enrollment = db.query(Enrollment).filter(
        Enrollment.event_id == event_id,
        Enrollment.user_id == user_id
    ).first()
    if enrollment:
        db.delete(enrollment)
        db.commit()
    return enrollment
