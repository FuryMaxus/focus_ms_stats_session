from litestar import Controller, post, Request,get  
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.domain.structs import SyncSessionPayload, SyncSessionResponse, SessionReportResponse
from app.services.session_service import process_focus_sessions
from app.repositories.session_repository import FocusSessionRepository
from app.services.session_service import fetch_session_reports


class SessionController(Controller):
    path = "/api/v1/sessions"

    @post("/batch")
    async def sync_session(
            self,
            request: Request,
            data: SyncSessionPayload,
            session_repo: "FocusSessionRepository"
        ) -> SyncSessionResponse:

        user_data = request.user
        seguro_user_id = str(user_data.get("sub")) if isinstance(user_data, dict) else str(user_data)
        print("DEBUG BACKEND: Petición recibida desde Android:")
        for session in data.sessions:
            print(f" -> Actividad: {session.activity_type}, RoomID: {session.room_id}")
        return await process_focus_sessions(seguro_user_id, data.sessions, session_repo)
        
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

        if isinstance(request.user, dict):
            logged_user_id = UUID(str(request.user.get("sub", request.user.get("id"))))
            user_role = str(request.user.get("role", "student")).lower()
        else:
            logged_user_id = UUID(str(request.user))
            user_role = "student"
            if isinstance(request.auth, dict):
                user_role = str(request.auth.get("role", "student")).lower()
            elif hasattr(request.auth, "extras"):
                user_role = str(request.auth.extras.get("role", "student")).lower()

        if user_role == "student":
            query_user_id = logged_user_id
            query_room_id = room_id
        else:
            if room_id is not None and user_id is None:
                query_user_id = None
            else:
                query_user_id = user_id if user_id is not None else logged_user_id
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
