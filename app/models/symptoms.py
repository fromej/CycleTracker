from sqlmodel import SQLModel, Field, Relationship, Column
from uuid import UUID, uuid4
from typing import Optional, List


class SymptomBase(SQLModel):
    period_id: UUID = Field(foreign_key="period.id")
    name: str
    intensity: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = Field(default=None, max_length=500)


class Symptom(SymptomBase, table=True):
    id: Optional[UUID] = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )

    # Relationship back to Period
    period: "Period" = Relationship(back_populates="symptoms")
