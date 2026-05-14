from litestar import Litestar
from litestar.di import Provide
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db_config import db_plugin
from app.api.v1.sessionController import SessionController
from app.repositories.session_repository import SessionRepository

async def provide_session_repo(db_session: AsyncSession) -> SessionRepository:
    return SessionRepository(session=db_session)

app = Litestar(
    route_handlers=[SessionController],
    plugins=[db_plugin],
    dependencies={
        "session_repo": Provide(provide_session_repo) 
    }
)