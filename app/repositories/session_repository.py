from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from typing import Sequence, Optional
from datetime import datetime
from uuid import UUID
from advanced_alchemy.filters import OrderBy, LimitOffset
from sqlalchemy import select

from app.models.focus_session import FocusSessionModel


class FocusSessionRepository(SQLAlchemyAsyncRepository[FocusSessionModel]):
    model_type = FocusSessionModel

    async def get_reports_dynamically(
        self,
        user_id: Optional[UUID] = None,
        room_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        sort_order: str = "desc",
        limit: int = 50,
        offset: int = 0
    ) -> Sequence[FocusSessionModel]:
        
        stmt = select(self.model_type)

        if user_id:
            stmt = stmt.where(self.model_type.user_id == user_id)
        if room_id:
            stmt = stmt.where(self.model_type.room_id == room_id)
        if start_date:
            stmt = stmt.where(self.model_type.start_time >= start_date)
        if end_date:
            stmt = stmt.where(self.model_type.end_time <= end_date)

        order_rule = OrderBy(
            field_name="start_time",
            sort_order="desc" if sort_order.lower() == "desc" else "asc"
        )
        pagination = LimitOffset(limit=limit, offset=offset)
        return await self.list(order_rule, pagination, statement=stmt)