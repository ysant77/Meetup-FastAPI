# app/schemas.py

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class EventBase(BaseModel):
    name: str
    date: datetime
    venue: str
    room: str
    speaker: Optional[str] = None
    description: Optional[str] = None
    max_pax: int

class EventCreate(EventBase):
    pass

class Event(EventBase):
    id: int
    organizer_id: int

    class Config:
        orm_mode = True
