from litestar import Controller, post
from app.domain.structs import SessionStruct
from app.services.session_service import process_focus_sessions

from app.repositories.session_repository import SessionRepository

class SessionController(Controller):

    path = "/sessions"

    @post("/sync")
    async def sync_session(
        self,
        data: list[SessionStruct],
        session_repo: SessionRepository
        ) -> dict:

        result = await process_focus_sessions(data, session_repo)

        return {
            "status": "success",
            "data": result
        }