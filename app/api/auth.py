from datetime import timedelta, datetime, UTC
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse

from app.api.deps import refresh_user
from app.core.config import get_settings
from app.core.database import get_async_session
from app.core.security import (
    verify_password,
    create_access_token,
)
from app.models.user import User, UserCreate, UserRead, Token
from app.schemas.user import UserLogin
from app.services.user import UserService

settings = get_settings()
router = APIRouter()


def get_user_service(db: AsyncSession = Depends(get_async_session)) -> UserService:
    return UserService(db)


def create_access_token_and_cookies(email: str, response: Response) -> tuple[str, Response]:
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": email},
        expires_delta=access_token_expires
    )

    # Set cookie with token
    response.set_cookie(
        key="refresh_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=settings.access_token_expire_minutes * 60,
        samesite="lax"
    )
    return access_token, response


@router.post("/register", response_model=UserRead)
async def register(
        user_in: UserCreate,
        user_service: UserService = Depends(get_user_service)
):
    # Check if user exists by email or username
    existing_user = await user_service.get_by_email(user_in.email)

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email or username already registered"
        )

    # Create new user
    return await user_service.create(user_in)


@router.post("/login", response_model=Token)
async def login(
        response: Response,
        form_data: UserLogin,
        session: AsyncSession = Depends(get_async_session)
):
    # Authenticate user - check both email and username
    statement = select(User).where(
        User.email == form_data.username.lower()
    )
    result = await session.execute(statement)
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login
    user.last_login = datetime.now(UTC)
    session.add(user)
    await session.commit()

    access_token, response = create_access_token_and_cookies(user.email, response)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh")
async def refresh(
        response: Response,
        user: User = Depends(refresh_user)
):
    access_token, response = create_access_token_and_cookies(user.email, response)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(response: Response):
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    return response
