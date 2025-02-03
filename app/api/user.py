from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status
from starlette.exceptions import HTTPException

from app.api.deps import get_current_user, get_current_user_admin
from app.core.database import get_async_session
from app.models.user import UserRead, User
from app.schemas.user import UserCreate, UserUpdate, PasswordChange
from app.services.db_services import PaginatedResponse, PaginationParams
from app.services.user import UserService

router = APIRouter(prefix="/users")


def get_user_service(db: AsyncSession = Depends(get_async_session)) -> UserService:
    return UserService(db)


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
        user_create: UserCreate,
        user_service: UserService = Depends(get_user_service),
        current_user: User = Depends(get_current_user_admin)
):
    db_user = await user_service.get_by_email(user_create.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return await user_service.create(user_create)


@router.get("/me", response_model=UserRead)
async def read_user_me(
        current_user: User = Depends(get_current_user)  # Any authenticated user can access their own info
):
    """Get current user information"""
    return current_user


@router.patch("/me", response_model=UserRead)
async def update_user_me(
        user_update: UserUpdate,
        user_service: UserService = Depends(get_user_service),
        current_user: User = Depends(get_current_user)
):
    """Update current user information"""
    return await user_service.update(current_user.id, user_update)


@router.post("/me/change-password", status_code=status.HTTP_200_OK)
async def change_password_me(
        password_change: PasswordChange,
        user_service: UserService = Depends(get_user_service),
        current_user: User = Depends(get_current_user)
):
    """Change current user password"""
    await user_service.change_password(current_user.id, password_change)
    return {"message": "Password changed successfully"}


@router.get("/{user_id}", response_model=UserRead)
async def read_user(
        user_id: UUID,
        user_service: UserService = Depends(get_user_service),
        current_user: User = Depends(get_current_user_admin)
):
    db_user = await user_service.get_by_id(user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user


@router.get("/", response_model=PaginatedResponse[UserRead])
async def read_users(
        pagination: PaginationParams = Depends(),
        user_service: UserService = Depends(get_user_service),
        current_user: User = Depends(get_current_user_admin)
):
    return await user_service.get_paginated(pagination)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
        user_id: UUID,
        user_update: UserUpdate,
        user_service: UserService = Depends(get_user_service),
        current_user: User = Depends(get_current_user_admin)
):
    return await user_service.update(user_id, user_update)


@router.post("/{user_id}/change-password", status_code=status.HTTP_200_OK)
async def change_password(
        user_id: UUID,
        password_change: PasswordChange,
        user_service: UserService = Depends(get_user_service),
        current_user: User = Depends(get_current_user_admin)
):
    await user_service.change_password(user_id, password_change)
    return {"message": "Password changed successfully"}


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        user_id: UUID,
        user_service: UserService = Depends(get_user_service),
        current_user: User = Depends(get_current_user_admin)
):
    await user_service.delete(user_id)
    return None
