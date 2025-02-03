from typing import Optional

from sqlmodel import select, delete
from uuid import UUID

from app.models.period import Period
from app.models.symptoms import Symptom
from app.services.db_services import PaginatedResponse, paginate_query, BaseCRUDService, PaginationParams


class PeriodService(BaseCRUDService):
    async def create(self, obj_in: dict) -> Period:
        """
        Create a new period with optional symptoms.
        """
        # Separate symptoms from period data
        symptoms_data = obj_in.pop('symptoms', [])

        # Create the period
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.flush()  # Flush to get the ID without committing

        # Create symptoms if provided
        if symptoms_data:
            for symptom_data in symptoms_data:
                symptom = Symptom(
                    period_id=db_obj.id,
                    **symptom_data
                )
                self.db.add(symptom)

        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, *, db_obj: Period, obj_in) -> Period:
        """
        Update a period, potentially including symptoms.
        """
        # Separate symptoms from update data
        symptoms_data = obj_in.pop('symptoms', None)

        # Update period base fields
        obj_data = db_obj.__dict__
        update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        self.db.add(db_obj)
        await self.db.flush()

        # Handle symptoms if provided
        if symptoms_data is not None:
            # Remove existing symptoms
            await self.db.execute(
                delete(Symptom).where(Symptom.period_id == db_obj.id)
            )

            # Add new symptoms
            for symptom_data in symptoms_data:
                symptom = Symptom(
                    period_id=db_obj.id,
                    **symptom_data
                )
                self.db.add(symptom)

        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def get_user_periods(
        self,
        user_id: UUID,
        pagination: PaginationParams
    ) -> PaginatedResponse:
        """
        Get periods for a specific user with pagination.
        """
        query = select(self.model).where(self.model.user_id == user_id)
        items, total = await paginate_query(query, self.db, self.model, pagination)
        return PaginatedResponse.create(
            data=items,
            total=total,
            page=pagination.page,
            limit=pagination.limit
        )

    async def get_recent_period(self, user_id: UUID) -> Optional[Period]:
        """
        Get the most recent period for a user.
        """
        query = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .order_by(self.model.start_date.desc())
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()