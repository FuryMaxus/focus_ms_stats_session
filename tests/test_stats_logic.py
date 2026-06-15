import uuid
import pytest
from datetime import datetime, timezone, timedelta
from app.services.stats_logic import calculate_real_exp
from app.domain.structs import SessionStruct

EXPECTED_30M_NORMAL_SOLO = 300
EXPECTED_20M_TIME_TRIAL_ROOM = 437
EXPECTED_CHEAT_OR_MICRO = 0

def test_calculate_real_exp_normal_solo():
    start = datetime(2026, 5, 12, 10, 0, 0, tzinfo=timezone.utc)
    end = start + timedelta(minutes=30)
    
    session = SessionStruct(
        activity_type="NORMAL",
        start_time=start,
        end_time=end,
        room_id=None,
        xp_multiplier=1.0
    )
    exp = calculate_real_exp(session)
    
    assert exp == EXPECTED_30M_NORMAL_SOLO

def test_calculate_real_exp_time_trial_in_room():
    start = datetime(2026, 5, 12, 10, 0, 0, tzinfo=timezone.utc)
    end = start + timedelta(minutes=20)
    
    # El multiplicador x1.25 de sala ahora viene inyectado
    session = SessionStruct(
        activity_type="TIME_TRIAL",
        start_time=start,
        end_time=end,
        room_id=str(uuid.uuid4()), 
        xp_multiplier=1.25
    )
    exp = calculate_real_exp(session)
    
    assert exp == EXPECTED_20M_TIME_TRIAL_ROOM

def test_calculate_real_exp_time_travel_cheat():
    start = datetime(2026, 5, 12, 10, 30, 0, tzinfo=timezone.utc)
    end = start - timedelta(minutes=30) 
    
    with pytest.raises(ValueError) as exc:
        SessionStruct(
            activity_type="NORMAL",
            start_time=start,
            end_time=end,
            room_id=None,
            xp_multiplier=1.0
        )
        
    assert "after start_time" in str(exc.value)

def test_calculate_real_exp_micro_session():
    start = datetime(2026, 5, 12, 10, 0, 0, tzinfo=timezone.utc)
    end = start + timedelta(seconds=5)
    
    session = SessionStruct(
        activity_type="NORMAL",
        start_time=start,
        end_time=end,
        room_id=None,
        xp_multiplier=1.0
    )
    exp = calculate_real_exp(session)
    
    assert exp == EXPECTED_CHEAT_OR_MICRO