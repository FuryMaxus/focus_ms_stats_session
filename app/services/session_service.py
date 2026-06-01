from uuid import UUID
from typing import Optional
from datetime import datetime
from app.domain.structs import SessionStruct
from app.models.focus_session import FocusSessionModel
from app.services.stats_logic import calculate_real_exp
from app.repositories.session_repository import FocusSessionRepository
from app.domain.structs import SessionReportResponse, SessionReportItem

async def process_focus_sessions(
        user_id: str, 
        sessions: list[SessionStruct],
        session_repo: FocusSessionRepository
    ) -> dict:
    
    if not sessions:
        return {"total_exp": 0, "time_trials_completed": 0}

    total_exp, time_trials_completed = await _save_sessions_to_db(user_id, sessions, session_repo)
    return {"total_exp": total_exp, "time_trials_completed": time_trials_completed}


async def _save_sessions_to_db(
        user_id: str,
        sessions: list[SessionStruct],
        session_repo: FocusSessionRepository
    ) -> tuple[int, int]:

    total_exp = 0
    time_trials = 0
    models_to_insert = []

    for data in sessions:
        is_in_room = data.room_id is not None
        
        real_exp = calculate_real_exp(
            data.start_time,
            data.end_time,
            data.activity_type,
            is_in_room
        )
        total_exp += real_exp
        
        if data.activity_type == "TIME_TRIAL":
            time_trials += 1
            
        new_session = FocusSessionModel(
            user_id=UUID(user_id),
            room_id=data.room_id,
            activity_type=data.activity_type,
            start_time=data.start_time,
            end_time=data.end_time,
            exp_earned=real_exp
        )
        models_to_insert.append(new_session)
        
    if models_to_insert:
        await session_repo.add_many(models_to_insert)

    return total_exp, time_trials

async def fetch_session_reports(
    session_repo: FocusSessionRepository,
    user_id: Optional[UUID] = None,
    room_id: Optional[UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    sort_order: str = "desc"
) -> SessionReportResponse:
    
    records = await session_repo.get_reports_dynamically(
        user_id=user_id,
        room_id=room_id,
        start_date=start_date,
        end_date=end_date,
        sort_order=sort_order
    )

    reports = [
        SessionReportItem(
            id=record.id, 
            user_id=record.user_id,
            activity_type=record.activity_type,
            start_time=record.start_time,
            end_time=record.end_time,
            exp_earned=record.exp_earned,
            room_id=record.room_id
        )
        for record in records
    ]

    return SessionReportResponse(reports=reports, total_count=len(reports))