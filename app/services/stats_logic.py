from datetime import datetime
from app.domain.structs import SessionStruct

ACTIVITY_MULTIPLIERS = {
    "NORMAL" : 1.0,
    "TIME_TRIAL" : 1.75,
}

BASE_EXP_PER_MIN = 10


def calculate_real_exp(
        session: SessionStruct
    ) -> int:
    duration_minutes = (session.end_time - session.start_time).total_seconds() / 60.0

    activity_exp_mult = ACTIVITY_MULTIPLIERS.get(session.activity_type.upper(), 1.0)
    

    multiplier = session.xp_multiplier  * activity_exp_mult

    total_exp = int(duration_minutes * BASE_EXP_PER_MIN * multiplier)

    return max(0, total_exp)
