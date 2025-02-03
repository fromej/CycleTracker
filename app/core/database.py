from sqlmodel import SQLModel, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .config import get_settings

settings = get_settings()

# Database URL handling
DATABASE_URL = settings.database_url
ASYNC_DATABASE_URL = DATABASE_URL.replace("sqlite:", "sqlite+aiosqlite:")

# Synchronous engine and session maker
sync_engine = create_engine(DATABASE_URL, echo=True)
sync_session = sessionmaker(bind=sync_engine, expire_on_commit=False)

# Asynchronous engine and session maker
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)
async_session = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)


# Dependency for sync session
def get_sync_session():
    with sync_session() as session:
        yield session


# Dependency for async session
async def get_async_session():
    async with async_session() as session:
        yield session


# Initialize the database
def init_db():
    SQLModel.metadata.create_all(sync_engine)
