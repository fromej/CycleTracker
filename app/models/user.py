from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr, constr
from uuid import UUID, uuid4


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True)
    first_name: str = Field(default=False)
    last_name: str = Field(default=False)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)


class User(UserBase, table=True):
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    hashed_password: str = Field(max_length=1024)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": datetime.now}
    )
    last_login: Optional[datetime] = Field(default=None)
    periods: list["Period"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    password: constr(min_length=8, max_length=64)


class UserRead(UserBase):
    id: UUID
    created_at: datetime
    last_login: Optional[datetime]


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    email: Optional[str] = None
