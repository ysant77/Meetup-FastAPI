# app/main.py

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from app import crud, models, schemas
from app.database import SessionLocal, engine, Base
from app.auth import create_access_token, verify_password
from app.services import check_event_conflict
from app.dependencies import get_db
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()

# Initialize database
Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/signup/", response_model=schemas.User)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/events/", response_model=schemas.Event)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, "supersecretkey", algorithms=["HS256"])
        organizer_email = payload.get("sub")
        organizer = crud.get_user_by_email(db, email=organizer_email)
        if not organizer or organizer.role != "event_organizer":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        
        # Check for event conflict
        if not check_event_conflict(db, event.venue, event.room, event.date):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Event conflict detected")
        
        return crud.create_event(db=db, event=event, organizer_id=organizer.id)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@app.post("/events/{event_id}/enroll/")
def enroll_in_event(event_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, "supersecretkey", algorithms=["HS256"])
        user_email = payload.get("sub")
        user = crud.get_user_by_email(db, email=user_email)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        enrollment = crud.enroll_user_in_event(db=db, user_id=user.id, event_id=event_id)
        if not enrollment:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Enrollment failed (conflict or capacity reached)")
        return {"message": "Enrollment successful"}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
