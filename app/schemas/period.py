from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional, List
from uuid import UUID
from enum import Enum


class FlowIntensity(str, Enum):
    LIGHT = "Light"
    MEDIUM = "Medium"
    HEAVY = "Heavy"


class SymptomCreate(BaseModel):
    name: str
    intensity: Optional[str] = None
    notes: Optional[str] = None


class SymptomResponse(SymptomCreate):
    id: UUID
    period_id: UUID


class PeriodCreate(BaseModel):
    start_date: date
    end_date: Optional[date] = None
    flow_intensity: Optional[FlowIntensity] = None
    notes: Optional[str] = Field(default=None, max_length=500)
    symptoms: Optional[List[SymptomCreate]] = []


class PeriodUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    flow_intensity: Optional[FlowIntensity] = None
    notes: Optional[str] = Field(default=None, max_length=500)


class PeriodResponse(PeriodCreate):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    symptoms: List[SymptomResponse] = []

    model_config = ConfigDict(from_attributes=True)


class DateIntensityCount(BaseModel):
    date: date
    count: int
