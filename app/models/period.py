from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime, date
from typing import Optional, List
from enum import Enum

from app.models.user import User
from app.models.symptoms import Symptom


class FlowIntensity(str, Enum):
    LIGHT = "Light"
    MEDIUM = "Medium"
    HEAVY = "Heavy"


class PeriodBase(SQLModel):
    user_id: UUID = Field(foreign_key="user.id")
    start_date: date
    end_date: Optional[date] = None
    flow_intensity: Optional[FlowIntensity] = None
    notes: Optional[str] = Field(default=None, max_length=500)


class Period(PeriodBase, table=True):
    id: Optional[UUID] = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": datetime.now}
    )

    # Relationship to User
    user: User = Relationship(back_populates="periods")

    # Relationship to Symptoms
    symptoms: List[Symptom] = Relationship(back_populates="period", sa_relationship_kwargs={"lazy": "selectin"})
