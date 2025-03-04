from datetime import datetime, timedelta
from typing import Optional, List

from sqlmodel import select, delete
from uuid import UUID

from app.models.period import Period, FlowIntensity
from app.models.symptoms import Symptom
from app.schemas.period import DateIntensityCount, PeriodCreate, PeriodUpdate
from app.services.db_services import PaginatedResponse, paginate_query, BaseCRUDService, PaginationParams


class PeriodService(BaseCRUDService):
    async def create(self, obj_in: PeriodCreate) -> Period:
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

    async def update(self, db_obj: Period, obj_in: PeriodUpdate) -> Period:
        """
        Update a period
        """
        # Update period base fields
        obj_data = db_obj.model_dump()
        update_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        self.db.add(db_obj)
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

    async def get_period_intensity_counts(self, user_id: UUID) -> List[DateIntensityCount]:
        """
        Get a list of dates and their corresponding flow intensity counts for the last year.
        Returns List[DateIntensityCount] where count is:
        0 for low intensity
        1 for medium intensity
        2 for high intensity
        """
        # Calculate date one year ago from today
        one_year_ago = datetime.now().date() - timedelta(days=365)

        # Query to get all periods in the last year
        query = (
            select(self.model)
            .where(
                self.model.user_id == user_id,
                self.model.start_date >= one_year_ago
            )
            .order_by(self.model.start_date)
        )

        result = await self.db.execute(query)
        periods = result.scalars().all()

        # Dictionary to store date counts
        date_counts = {}

        for period in periods:
            # Convert flow intensity to count
            intensity_count = {
                FlowIntensity.LIGHT: 0,
                FlowIntensity.MEDIUM: 1,
                FlowIntensity.HEAVY: 2
            }.get(period.flow_intensity, 0)

            if period.end_date is None:
                # If no end date, just add the start date
                date_counts[period.start_date] = intensity_count
            else:
                # For each day in the period, add to the dictionary
                current_date = period.start_date
                while current_date <= period.end_date:
                    date_counts[current_date] = intensity_count
                    current_date += timedelta(days=1)

        # Convert dictionary to list of DateIntensityCount objects
        return [
            DateIntensityCount(date=date, count=count)
            for date, count in sorted(date_counts.items())
        ]
