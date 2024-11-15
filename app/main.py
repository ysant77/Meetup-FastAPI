# app/main.py

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from app import schemas
from app.database import engine, Base
from app.auth import create_access_token
from app.services import authenticate_user, register_user, create_event, enroll_user, check_user_exists
from app.dependencies import get_current_user, get_db
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()

# Initialize database
Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/signup/", response_model=schemas.User)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Use `check_user_exists` to check if the user already exists
    if check_user_exists(db, user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    return register_user(db=db, user_data=user)

@app.post("/token/")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Authenticate user with correct password verification
    user = authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/events/", response_model=schemas.Event)
def create_event_route(
    event: schemas.EventCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    if current_user.role != "event_organizer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    event = create_event(db=db, event_data=event, organizer_id=current_user.id)
    if not event:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Event conflict detected")
    return event

@app.post("/events/{event_id}/enroll/")
def enroll_in_event_route(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    enrollment = enroll_user(db=db, user_id=current_user.id, event_id=event_id)
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Enrollment failed (conflict or capacity reached)")
    return {"message": "Enrollment successful"}

