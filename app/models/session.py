from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class FocusSessionModel(Base):
    __tablename__ = "focus_sessions"

    user_id: Mapped[UUID] = mapped_column(nullable=False)
    room_id: Mapped[UUID] = mapped_column(nullable=True)
    activity_type: Mapped[str] = mapped_column(nullable=False)
    start_time: Mapped[datetime] = mapped_column(nullable=False)
    end_time: Mapped[datetime] = mapped_column(nullable=False)
    exp_earned: Mapped[int] = mapped_column(default=0)