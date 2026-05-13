from litestar import Controller, post
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.structs import SessionStruct
from app.services.session_service import process_focus_sessions

class SessionController(Controller):

    path = "/sessions"

    @post("/sync")
    async def sync_session(
        self,
        data: list[SessionStruct],
        db_session: AsyncSession
        ) -> dict:

        result = await process_focus_sessions(
            data,
            db_session)

        return {
            "status": "success",
            "sessions_synced": len(data),
            "total_xp_granted": result["total_xp"]
        }