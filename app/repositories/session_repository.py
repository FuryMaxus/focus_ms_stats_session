from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from app.models.session import FocusSessionModel

class SessionRepository(SQLAlchemyAsyncRepository[FocusSessionModel]):
    model_type = FocusSessionModel