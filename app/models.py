from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)  # Roles: 'admin', 'event_organizer', 'participant'
    events = relationship("Enrollment", back_populates="user")

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    date = Column(DateTime, index=True)
    venue = Column(String, index=True)
    room = Column(String)
    speaker = Column(String)
    description = Column(String)
    max_pax = Column(Integer)  # Maximum number of participants
    organizer_id = Column(Integer, ForeignKey("users.id"))
    organizer = relationship("User")
    participants = relationship("Enrollment", back_populates="event")

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    event_id = Column(Integer, ForeignKey("events.id"))
    user = relationship("User", back_populates="events")
    event = relationship("Event", back_populates="participants")
