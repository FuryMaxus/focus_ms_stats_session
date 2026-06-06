import msgspec
from uuid import UUID
from datetime import datetime
from typing import Optional, List

class SessionStruct(msgspec.Struct):
    activity_type: str       
    start_time: datetime
    end_time: datetime
    client_reported_exp: int = 0  
    room_id: Optional[UUID] = None

    def __post_init__(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")

class SyncSessionPayload(msgspec.Struct):
    sessions: List[SessionStruct]

class SyncSessionResponse(msgspec.Struct):
    total_exp_gained: int
    time_trials_completed: int

class SessionReportItem(msgspec.Struct):
    id: UUID 
    user_id: UUID
    activity_type: str
    start_time: datetime
    end_time: datetime
    exp_earned: int
    room_id: Optional[UUID] = None

class SessionReportResponse(msgspec.Struct):
    reports: List[SessionReportItem]
    total_count: int