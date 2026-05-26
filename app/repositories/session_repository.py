from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from app.models.focus_session import FocusSessionModel

class FocusSessionRepository(SQLAlchemyAsyncRepository[FocusSessionModel]):
    model_type = FocusSessionModel