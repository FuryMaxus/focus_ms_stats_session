import msgspec
from uuid import UUID
from datetime import datetime
from typing import Optional

class SessionStruct(msgspec.Struct):
    user_id: UUID
    activity_type: str       
    start_time: datetime
    end_time: datetime
    client_reported_xp: int  
    room_id: Optional[UUID] = None

    def __post_init__(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")