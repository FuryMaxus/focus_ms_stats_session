from litestar import Controller, post, Request,get  
import msgspec
from typing import Optional
from datetime import datetime
from uuid import UUID
from litestar.exceptions import ClientException
from app.domain.structs import SessionStruct, SessionReportResponse
from app.services.session_service import process_focus_sessions
from app.repositories.session_repository import FocusSessionRepository
from app.services.session_service import fetch_session_reports


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
    
    @get("/reports")
    async def get_reports(
        self,
        request: Request,
        session_repo: "FocusSessionRepository",
        user_id: Optional[UUID] = None,
        room_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        sort_order: str = "desc",
        limit: int = 50,
        offset: int = 0
    ) -> SessionReportResponse:
        
        logged_user_id = UUID(str(request.user))
        
        token_payload = request.auth if isinstance(request.auth, dict) else {}
        user_role = token_payload.get("role", "student")

        if user_role == "student":
            query_user_id = logged_user_id
            query_room_id = room_id 
        else:
            query_user_id = user_id
            query_room_id = room_id

        return await fetch_session_reports(
            session_repo=session_repo,
            user_id=query_user_id,
            room_id=query_room_id,
            start_date=start_date,
            end_date=end_date,
            sort_order=sort_order,
            limit=limit,
            offset=offset
        )