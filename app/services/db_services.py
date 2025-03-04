from pydantic import BaseModel
from sqlalchemy import func
from typing import Type, List, Tuple, TypeVar, Generic, Any
from fastapi import Query
from sqlmodel import select, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    limit: int
    total_pages: int

    @classmethod
    def create(cls, data: List[T], total: int, page: int, limit: int):
        total_pages = (total + limit - 1) // limit
        return cls(items=data, total=total, page=page, limit=limit, total_pages=total_pages)


class PaginationParams:
    def __init__(
            self,
            page: int = Query(1, ge=1, description="Page number (must be >= 1)"),
            limit: int = Query(10, ge=1, le=100, description="Number of items per page (1-100)"),
    ):
        self.page = page
        self.limit = limit

    @property
    def skip(self) -> int:
        """Calculate the offset for the database query."""
        return (self.page - 1) * self.limit


async def paginate_query(
        query, db: AsyncSession, model: Type, pagination: PaginationParams
) -> Tuple[List, int]:
    """
    Paginate a SQLAlchemy async query.
    - query: SQLAlchemy select query.
    - db: Async database session.
    - model: SQLAlchemy model.
    - pagination: Pagination parameters (page, limit, skip).
    Returns:
    - List of items for the current page.
    - Total count of all items in the query.
    """
    # Execute count query
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.execute(count_query)
    total = total.scalar()

    # Execute paginated query
    paginated_query = query.offset(pagination.skip).limit(pagination.limit)
    result = await db.execute(paginated_query)
    items = result.scalars().all()

    return items, total


class BaseCRUDService:
    def __init__(self, db: AsyncSession, model: SQLModel):
        self.db = db
        self.model = model

    async def get_paginated(
            self, pagination: PaginationParams
    ) -> PaginatedResponse:
        """
        Get paginated results for a model.
        - db: Async SQLAlchemy database session.
        - pagination: Pagination parameters.
        Returns:
        - PaginatedResponse with items and pagination metadata.
        """
        query = select(self.model)  # Build the select query for the model
        items, total = await paginate_query(query, self.db, self.model, pagination)
        return PaginatedResponse.create(
            data=items,
            total=total,
            page=pagination.page,
            limit=pagination.limit
        )

    async def create(self, obj_in: dict) -> T:
        """
        Create a new record.
        """
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def get(self, obj_id: Any) -> T | None:
        """
        Get a record by ID.
        """
        query = select(self.model).where(self.model.id == obj_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(
            self, *, skip: int = 0, limit: int = 100
    ) -> List[T]:
        """
        Get multiple records with optional skip/limit.
        """
        query = select(self.model).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update(
            self, *, db_obj: T, obj_in
    ) -> T:
        """
        Update a record.
        """
        obj_data = db_obj.__dict__
        update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, *, object_id: Any) -> bool:
        """
        Delete a record.
        """
        obj = await self.get(object_id)
        if obj:
            await self.db.delete(obj)
            await self.db.commit()
            return True
        return False
