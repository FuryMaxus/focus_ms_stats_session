from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from typing import Sequence, Optional
from datetime import datetime
from uuid import UUID
from advanced_alchemy.filters import OrderBy, LimitOffset
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
        
        query_filters = []

        if user_id:
            query_filters.append(FocusSessionModel.user_id == user_id)
        if room_id:
            query_filters.append(FocusSessionModel.room_id == room_id)
        if start_date:
            query_filters.append(FocusSessionModel.start_time >= start_date)
        if end_date:
            query_filters.append(FocusSessionModel.end_time <= end_date)
        
        order_rule = OrderBy(
            field_name="start_time", 
            sort_order="desc" if sort_order.lower() == "desc" else "asc"
        )
        query_filters.append(order_rule)
        query_filters.append(LimitOffset(limit=limit, offset=offset))        
        return await self.list(*query_filters)