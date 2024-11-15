from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError

from app import schemas
from app.database import engine, Base
from app.auth import create_access_token
import app.services as service  # Import services with a namespace for clarity
from app.dependencies import get_current_user, get_db

app = FastAPI()

# Initialize database
Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/signup/", response_model=schemas.User)
def signup_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user in the system.

    Args:
        user (UserCreate): The user data including name, email, password, and role.
        db (Session): The database session.

    Returns:
        User: The created user object with details.

    Raises:
        HTTPException: If the email is already registered.
    """
    if service.check_user_exists(db, user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    return service.register_user(db=db, user_data=user)

@app.post("/token/")
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate user and return a JWT access token.

    Args:
        form_data (OAuth2PasswordRequestForm): User login data including username (email) and password.
        db (Session): The database session.

    Returns:
        dict: Access token and token type.

    Raises:
        HTTPException: If the credentials are invalid.
    """
    user = service.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/events/", response_model=schemas.Event)
def create_event(
    event: schemas.EventCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Create a new event, accessible only by admin or event organizers.

    Args:
        event (EventCreate): Event data including name, date, venue, room, etc.
        db (Session): The database session.
        current_user (User): The current authenticated user.

    Returns:
        Event: The created event object.

    Raises:
        HTTPException: If the user is unauthorized to create an event.
    """
    if current_user.role not in ["admin", "event_organizer"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return service.admin_create_event(db=db, event_data=event, organizer_id=current_user.id)

@app.post("/events/{event_id}/enroll/")
def enroll_user_in_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Enroll a user in a specified event.

    Args:
        event_id (int): The ID of the event to enroll in.
        db (Session): The database session.
        current_user (User): The current authenticated user.

    Returns:
        dict: Success message if enrollment is successful.

    Raises:
        HTTPException: If enrollment fails due to conflicts or event capacity.
    """
    enrollment = service.enroll_user(db=db, user_id=current_user.id, event_id=event_id)
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Enrollment failed (conflict or capacity reached)")
    return {"message": "Enrollment successful"}

@app.get("/events/")
def list_events(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
    show_participants: bool = False
):
    """
    Retrieve all events with an optional parameter to include participants.

    Args:
        db (Session): The database session.
        current_user (User): The current authenticated user.
        show_participants (bool): Whether to include participant details in the event data.

    Returns:
        list[Event]: A list of all event objects with optional participant data.

    Raises:
        HTTPException: If the user is unauthorized to view all events.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return service.list_all_events(db=db, show_participants=show_participants)

@app.put("/events/{event_id}")
def update_event_details(
    event_id: int,
    event_data: schemas.EventCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Update the details of an event if the user is authorized.

    Args:
        event_id (int): The ID of the event to update.
        event_data (EventCreate): New event data to apply.
        db (Session): The database session.
        current_user (User): The current authenticated user.

    Returns:
        Event: The updated event object.

    Raises:
        HTTPException: If the event is not found or if the user is unauthorized.
    """
    try:
        return service.update_event(db=db, event_id=event_id, event_data=event_data, current_user=current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@app.delete("/admin/organizers/{organizer_id}")
def remove_event_organizer(
    organizer_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Remove an event organizer from the system, accessible only to admins.

    Args:
        organizer_id (int): The ID of the organizer to remove.
        db (Session): The database session.
        current_user (User): The current authenticated user.

    Returns:
        User: The removed organizer object.

    Raises:
        HTTPException: If the user is unauthorized or the organizer is not found.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    try:
        return service.remove_event_organizer(db=db, organizer_id=organizer_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@app.delete("/events/{event_id}/unenroll")
def unenroll_user_from_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Unenroll the current user from a specified event.

    Args:
        event_id (int): The ID of the event to unenroll from.
        db (Session): The database session.
        current_user (User): The current authenticated user.

    Returns:
        dict: Success message if unenrollment is successful.

    Raises:
        HTTPException: If the enrollment is not found.
    """
    try:
        return service.unenroll_from_event(db=db, event_id=event_id, user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@app.get("/admin/users/")
def list_all_users(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """
    Retrieve all users in the system, accessible only to admins.

    Args:
        db (Session): The database session.
        current_user (User): The current authenticated user.

    Returns:
        list[User]: A list of all user objects.

    Raises:
        HTTPException: If the user is unauthorized to view all users.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return service.get_all_users(db=db)
