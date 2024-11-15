from sqlalchemy.orm import Session
from app.models import User, Event, Enrollment
from app.schemas import UserCreate, EventCreate
from app.auth import get_password_hash

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(name=user.name, email=user.email, hashed_password=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_event(db: Session, event_id: int):
    return db.query(Event).filter(Event.id == event_id).first()

def create_event(db: Session, event: EventCreate, organizer_id: int):
    db_event = Event(**event.dict(), organizer_id=organizer_id)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def enroll_user_in_event(db: Session, user_id: int, event_id: int):
    event = get_event(db, event_id)
    if len(event.participants) >= event.max_pax:
        return None  # Event is full
    for enrollment in db.query(Enrollment).filter(Enrollment.user_id == user_id).all():
        if enrollment.event.date == event.date:
            return None  # Conflict
    enrollment = Enrollment(user_id=user_id, event_id=event_id)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment
