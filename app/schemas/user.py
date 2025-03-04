from uuid import UUID

from pydantic import BaseModel, EmailStr, constr


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    is_superuser: bool = False


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: UUID
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None

    class Config:
        from_attributes = True


class PasswordChangeAdmin(BaseModel):
    new_password: constr(min_length=8, max_length=64)


class PasswordChange(PasswordChangeAdmin):
    current_password: str


class UserLogin(BaseModel):
    username: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None
