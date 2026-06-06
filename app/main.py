from litestar import Litestar, get
from litestar.di import Provide
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db_config import db_plugin
from app.api.v1.sessionController import SessionController
from app.repositories.session_repository import FocusSessionRepository
from app.core.security import jwt_auth
from app.core.exceptions import GLOBAL_EXCEPTION_HANDLERS

async def provide_session_repo(db_session: AsyncSession) -> FocusSessionRepository:
    return FocusSessionRepository(session=db_session)

@get("/health")
async def health_check() -> dict:
    return {"status": "ok", "service": "ms_stats"}


app = Litestar( 
    route_handlers=[health_check, SessionController],
    plugins=[db_plugin],
    dependencies={
        "session_repo": Provide(provide_session_repo) 
    },
    exception_handlers=GLOBAL_EXCEPTION_HANDLERS,
    on_app_init=[jwt_auth.on_app_init],
    debug = False
)