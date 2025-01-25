from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional
from enum import Enum


# Authentication Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True


# Menstrual Cycle Schemas
class MenstrualCycleBase(BaseModel):
    start_date: date
    end_date: Optional[date] = None
    cycle_length: Optional[int] = None
    notes: Optional[str] = None


class MenstrualCycleCreate(MenstrualCycleBase):
    pass


class MenstrualCycle(MenstrualCycleBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class EventTypeEnum(str, Enum):
    CYCLE_START = "CYCLE_START"
    CYCLE_END = "CYCLE_END"
    SYMPTOMS_START = "SYMPTOMS_START"
    SYMPTOMS_END = "SYMPTOMS_END"
    PAIN_LEVEL = "PAIN_LEVEL"
    MOOD = "MOOD"
    NOTE = "NOTE"


class MenstrualEventBase(BaseModel):
    event_date: date
    event_type: EventTypeEnum
    event_value: Optional[str] = None
    additional_notes: Optional[str] = None


class MenstrualEventCreate(MenstrualEventBase):
    pass


class MenstrualEvent(MenstrualEventBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True
