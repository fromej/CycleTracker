from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Optional

from app.api.deps import get_current_user
from app.core.database import get_async_session
from app.models.user import User
from app.models.period import Period
from app.schemas.period import PeriodUpdate, PeriodResponse, PeriodCreate
from app.services.db_services import PaginationParams, PaginatedResponse
from app.services.period import PeriodService

period_router = APIRouter(prefix="/periods")


def get_period_service(db: AsyncSession = Depends(get_async_session)) -> PeriodService:
    return PeriodService(db, Period)


@period_router.post("/", response_model=PeriodResponse)
async def create_period(
        period: PeriodCreate,
        period_service: PeriodService = Depends(get_period_service),
        current_user: User = Depends(get_current_user)
):
    """
    Create a new period entry for the current user.
    """
    period_data = period.model_dump()
    period_data['user_id'] = current_user.id

    try:
        created_period = await period_service.create(period_data)
        return created_period
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@period_router.get("/", response_model=PaginatedResponse[PeriodResponse])
async def list_periods(
        pagination: PaginationParams = Depends(),
        period_service: PeriodService = Depends(get_period_service),
        current_user: User = Depends(get_current_user)
):
    """
    List periods for the current user with pagination.
    """
    return await period_service.get_user_periods(current_user.id, pagination)


@period_router.get("/recent", response_model=Optional[PeriodResponse])
async def get_recent_period(
        period_service: PeriodService = Depends(get_period_service),
        current_user: User = Depends(get_current_user)
):
    """
    Get the most recent period for the current user.
    """
    return await period_service.get_recent_period(current_user.id)


@period_router.get("/{period_id}", response_model=PeriodResponse)
async def get_period(
        period_id: UUID,
        period_service: PeriodService = Depends(get_period_service),
        current_user: User = Depends(get_current_user)
):
    """
    Get a specific period by ID.
    """
    period = await period_service.get(period_id)

    if not period or period.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Period not found")

    return period


@period_router.patch("/{period_id}", response_model=PeriodResponse)
async def update_period(
        period_id: UUID,
        period_update: PeriodUpdate,
        period_service: PeriodService = Depends(get_period_service),
        current_user: User = Depends(get_current_user)
):
    """
    Update a specific period entry.
    """
    # First, get the existing period
    existing_period = await period_service.get(period_id)

    if not existing_period or existing_period.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Period not found")

    try:
        updated_period = await period_service.update(
            db_obj=existing_period,
            obj_in=period_update
        )
        return updated_period
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@period_router.delete("/{period_id}", response_model=dict)
async def delete_period(
        period_id: UUID,
        period_service: PeriodService = Depends(get_period_service),
        current_user: User = Depends(get_current_user)
):
    """
    Delete a specific period entry.
    """
    # First, get the existing period
    existing_period = await period_service.get(period_id)

    if not existing_period or existing_period.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Period not found")

    deleted = await period_service.delete(object_id=period_id)

    if not deleted:
        raise HTTPException(status_code=400, detail="Could not delete period")

    return {"detail": "Period successfully deleted"}