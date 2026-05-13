from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class FocusSession(Base):
    __tablename__ = "focus_sessions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(nullable=False)
    room_id: Mapped[UUID] = mapped_column(nullable=True)
    activity_type: Mapped[str] = mapped_column(nullable=False)
    start_time: Mapped[datetime] = mapped_column(nullable=False)
    end_time: Mapped[datetime] = mapped_column(nullable=False)
    xp_earned: Mapped[int] = mapped_column(default=0)