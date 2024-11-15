from sqlalchemy.orm import Session
from app.models import User, Event, Enrollment
from app.schemas import UserCreate, EventCreate
from app.auth import get_password_hash

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
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

def get_event(db: Session, event_id: int):
    return db.query(Event).filter(Event.id == event_id).first()

def create_event(db: Session, event: EventCreate, organizer_id: int):
    db_event = Event(**event.model_dump(), organizer_id=organizer_id)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def enroll_user_in_event(db: Session, user_id: int, event_id: int):
    enrollment = Enrollment(user_id=user_id, event_id=event_id)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment
