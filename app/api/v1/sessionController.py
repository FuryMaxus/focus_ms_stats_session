from litestar import Controller, post, Request
import msgspec
from litestar.exceptions import ClientException
from app.domain.structs import SessionStruct
from app.services.session_service import process_focus_sessions
from app.repositories.session_repository import FocusSessionRepository

class SessionController(Controller):
    path = "/api/v1/sessions"

    @post("/batch")
    async def sync_session(
            self,
            request: Request,
            data: dict,
            session_repo: "FocusSessionRepository"
        ) -> dict:

        seguro_user_id = request.user
        raw_sessions = data.get("sessions", [])
        try:
            session_structs = [msgspec.convert(s, type=SessionStruct) for s in raw_sessions]
        except msgspec.ValidationError as e:
            raise ClientException(detail=f"Error de validación en fechas: {str(e)}")
        
            
        result = await process_focus_sessions(seguro_user_id, session_structs, session_repo)

        return result