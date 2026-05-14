from litestar import Controller, post, Request
from litestar.exceptions import NotAuthorizedException
from app.domain.structs import SessionStruct
from app.services.session_service import process_focus_sessions

from app.repositories.session_repository import SessionRepository

class SessionController(Controller):

    path = "/sessions"

    @post("/sync")
    async def sync_session(
            self,
            request: Request,   
            data: list[SessionStruct],
            session_repo: SessionRepository
        ) -> dict:

        user_id_from_token = request.user
        
        for session in data:
            if str(session.user_id) != user_id_from_token:
                raise NotAuthorizedException(
                    "Hacker detectado: No puedes registrar sesiones a nombre de otro usuario."
                )
            
        result = await process_focus_sessions(data, session_repo)

        return {
            "status": "success",
            "data": result
        }