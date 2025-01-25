from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from .database import Base
import enum


class EventType(enum.Enum):
    CYCLE_START = "Cycle Start"
    CYCLE_END = "Cycle End"
    SYMPTOMS_START = "Symptoms Start"
    SYMPTOMS_END = "Symptoms End"
    PAIN_LEVEL = "Pain Level"
    MOOD = "Mood"
    NOTE = "Personal Note"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    events = relationship("MenstrualEvent", back_populates="user")


class MenstrualEvent(Base):
    __tablename__ = "menstrual_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    event_date = Column(Date)
    event_type = Column(Enum(EventType))
    event_value = Column(String, nullable=True)
    additional_notes = Column(String, nullable=True)

    user = relationship("User", back_populates="events")
