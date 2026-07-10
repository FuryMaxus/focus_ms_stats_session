from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from typing import Sequence, Optional
from datetime import datetime
from uuid import UUID
from advanced_alchemy.filters import OrderBy, LimitOffset
from sqlalchemy import select, func, desc, cast, Date

from app.domain.structs import LeaderboardItem, GraphItem
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

    async def get_room_leaderboard(self, room_id: UUID, limit: int = 10) -> list[LeaderboardItem]:

        stmt = (
            select(
                self.model_type.user_id,
                func.sum(self.model_type.exp_earned).label("total_xp")
            )
            .where(self.model_type.room_id == room_id)
            .group_by(self.model_type.user_id)
            .order_by(desc("total_xp"))
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        return [LeaderboardItem(user_id=row.user_id, total_xp=int(row.total_xp)) for row in rows]

    async def get_xp_by_date(self, room_id: UUID, start_date: datetime, end_date: datetime) -> list[GraphItem]:
        date_col = cast(self.model_type.start_time, Date).label("session_date")

        stmt = (
            select(
                date_col,
                func.sum(self.model_type.exp_earned).label("daily_xp")
            )
            .where(
                (self.model_type.room_id == room_id) &
                (self.model_type.start_time >= start_date) &
                (self.model_type.start_time <= end_date)
            )
            .group_by(date_col)
            .order_by(date_col)
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        return [GraphItem(date=str(row.session_date), xp=int(row.daily_xp)) for row in rows]