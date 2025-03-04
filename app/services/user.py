from datetime import datetime
from uuid import UUID

from sqlalchemy import func
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status
from starlette.exceptions import HTTPException

from app.core.security import pwd_context
from app.models.user import User, UserRead
from app.schemas.user import UserCreate, PasswordChange, UserUpdate
from app.services.db_services import PaginationParams, PaginatedResponse, BaseCRUDService


class UserService():
    def __init__(self, db: AsyncSession):
        self.db = db
        self.crud_service = BaseCRUDService(self.db, User)

    async def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: UUID) -> User | None:
        return await self.crud_service.get(user_id)

    async def create(self, user_create: UserCreate) -> User:
        hashed_password = pwd_context.hash(user_create.password)

        db_user = User(
            email=user_create.email,
            first_name=user_create.first_name,
            last_name=user_create.last_name,
            hashed_password=hashed_password,
            is_superuser=user_create.is_superuser
        )

        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def update(self, user_id: UUID, user_update: UserUpdate) -> User:
        db_user = await self.get_by_id(user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        update_data = user_update.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_user, field, value)

        db_user.updated_at = datetime.now()
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def change_password(self, user_id: UUID, password_change: PasswordChange) -> bool:
        db_user = await self.get_by_id(user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Verify current password
        if not pwd_context.verify(password_change.current_password, db_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect password"
            )

        # Update password
        db_user.hashed_password = pwd_context.hash(password_change.new_password)
        db_user.updated_at = datetime.now()

        self.db.add(db_user)
        await self.db.commit()
        return True

    async def change_password_admin(self, user_id: UUID, password_change: PasswordChange) -> bool:
        db_user = await self.get_by_id(user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Update password
        db_user.hashed_password = pwd_context.hash(password_change.new_password)
        db_user.updated_at = datetime.now()

        self.db.add(db_user)
        await self.db.commit()
        return True

    async def delete(self, user_id: UUID) -> bool:
        db_user = await self.get_by_id(user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        await self.db.delete(db_user)
        await self.db.commit()
        return True

    async def get_paginated(
            self,
            pagination: PaginationParams
    ) -> PaginatedResponse[UserRead]:
        return await self.crud_service.get_paginated(pagination)
