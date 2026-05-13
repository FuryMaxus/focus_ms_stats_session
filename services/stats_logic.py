from datetime import datetime

ACTIVITY_MULTIPLIERS = {
    "NORMAL" : 1.0,
    "TIME_TRIAL" : 1.75,
}

BASE_EXP_PER_MIN = 10
IN_ROOM_MULT = 1.25

def calculate_real_ex(
        start_time: datetime,
        end_time: datetime, 
        activity_type: str,
        is_in_room: bool) -> int:
    duration_minutes = (end_time - start_time).total_seconds() / 60.0

    activity_exp_mult = multiplier = ACTIVITY_MULTIPLIERS.get(activity_type.upper(), 1.0)
    
    room_mult = IN_ROOM_MULT if is_in_room else 1.0

    multiplier = room_mult * activity_exp_mult

    total_exp = int(duration_minutes * BASE_EXP_PER_MIN * multiplier)

    return max(0, total_exp)


    