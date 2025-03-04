from datetime import timedelta
from typing import Callable, Awaitable

import pytest
from httpx import ASGITransport, AsyncClient
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.config import get_settings, Settings
from app.core.database import get_async_session
from app.core.security import create_access_token
from app.main import app
from app.models.period import Period, FlowIntensity
from app.models.user import User, UserCreate
from app.services.user import UserService

get_settings.cache_clear()

engine = create_async_engine(get_settings().async_database_url, echo=False, future=True)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
async def override_get_session(setup_db):
    """Provide a fresh database session for each test"""

    async def _override():
        async with async_session_maker() as session:
            yield session

    return _override


@pytest.fixture
async def a_session(setup_db):
    """A session to use as connection to the db"""
    async with async_session_maker() as session:
        yield session


@pytest.fixture(autouse=True)
def test_app(override_get_session):
    """App fixture for standard overwrites"""
    app.dependency_overrides[get_async_session] = override_get_session
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
async def setup_db():
    """Create and drop the database for each test (fully async)"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield  # Test runs here
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture
async def client(test_app):
    """Use FastAPI's TestClient for synchronous setup"""
    async with AsyncClient(
            transport=ASGITransport(app=test_app), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
async def normal_user(override_get_session, faker):
    """Fixture to create a normal user."""

    async for session in override_get_session():
        user_service = UserService(db=session)
        user_data = UserCreate(
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            password="password",
            email=faker.email()
        )
        user = await user_service.create(user_data)
        yield user  # This will provide the created user to the test
        # Cleanup after test
        # await session.delete(user)
        # await session.commit()


@pytest.fixture
async def superuser(override_get_session, faker):
    """Fixture to create a superuser."""

    async for session in override_get_session():
        user_service = UserService(db=session)
        user_data = UserCreate(
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            password=faker.password(length=8),
            email=faker.email(),
            is_superuser=True,
        )
        user = await user_service.create(user_data)

        yield user  # Provide the created superuser to the test
        # Cleanup after test
        await session.delete(user)
        await session.commit()


@pytest.fixture
async def user_client(normal_user, test_app):
    """Fixture to create a TestClient with a bearer token for the authenticated user"""
    access_token = create_access_token(data={"sub": normal_user.email}, expires_delta=timedelta(minutes=15))

    # Create the TestClient with the Bearer token in the headers
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # Use TestClient to make requests with the headers
    async with AsyncClient(
            transport=ASGITransport(app=test_app), base_url="http://test"
    ) as client:
        # Set the headers for every request
        client.headers.update(headers)
        yield client, normal_user


@pytest.fixture
async def admin_client(superuser: User, test_app):
    """Fixture to create a TestClient with a bearer token for the authenticated user"""
    access_token = create_access_token(data={"sub": superuser.email}, expires_delta=timedelta(minutes=15))

    # Create the TestClient with the Bearer token in the headers
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # Use TestClient to make requests with the headers
    async with AsyncClient(
            transport=ASGITransport(app=test_app), base_url="http://test"
    ) as client:
        # Set the headers for every request
        client.headers.update(headers)
        yield client, admin_client


@pytest.fixture
def a_period(a_session: AsyncSession, faker) -> Callable[[User], Awaitable[Period]]:
    async def _a_period(user: User) -> Period:
        period = Period(
            user_id=user.id,
            start_date=faker.date_object(),
            end_date=faker.date_object(),
            flow_intensity=FlowIntensity.MEDIUM,
            notes=faker.text(max_nb_chars=50)
        )
        a_session.add(period)
        await a_session.commit()
        await a_session.refresh(period)
        return period

    return _a_period

