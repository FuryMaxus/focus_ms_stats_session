from datetime import datetime
from domain.structs import SessionStruct
from sqlalchemy.ext.asyncio import AsyncSession
from models.session import FocusSession

ACTIVITY_MULTIPLIERS = {
    "NORMAL" : 1.0,
    "TIME_TRIAL" : 1.75,
}

BASE_EXP_PER_MIN = 10
IN_ROOM_MULT = 1.25


async def process_focus_sessions(
        sessions: list[SessionStruct],
        db_session: AsyncSession
    ) -> dict:
    
    total_xp_for_batch = 0

    for data in sessions:
        is_in_room = True if data.room_id else False

        real_exp = calculate_real_exp(
            data.start_time,
            data.end_time,
            data.activity_type,
            is_in_room)
        
        total_xp_for_batch += real_exp

        new_session = FocusSession(
            user_id = data.user_id,
            room_id = data.room_id,
            activity_type = data.activity_type,
            start_time = data.start_time,
            end_time = data.end_time,
            xp_earned = real_exp
        )

        db_session.add(new_session)

    #Here go the calls to the other services

    #
    
    return {
        "total_xp": total_xp_for_batch
    }


def calculate_real_exp(
        start_time: datetime,
        end_time: datetime, 
        activity_type: str,
        is_in_room: bool
    ) -> int:
    duration_minutes = (end_time - start_time).total_seconds() / 60.0

    activity_exp_mult = multiplier = ACTIVITY_MULTIPLIERS.get(activity_type.upper(), 1.0)
    
    room_mult = IN_ROOM_MULT if is_in_room else 1.0

    multiplier = room_mult * activity_exp_mult

    total_exp = int(duration_minutes * BASE_EXP_PER_MIN * multiplier)

    return max(0, total_exp)


    