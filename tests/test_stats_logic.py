import pytest
from datetime import datetime, timezone, timedelta
from app.services.stats_logic import calculate_real_exp


EXPECTED_30M_NORMAL_SOLO = 300
EXPECTED_20M_TIME_TRIAL_ROOM = 437
EXPECTED_CHEAT_OR_MICRO = 0


def test_calculate_real_exp_normal_solo():
    start = datetime(2026, 5, 12, 10, 0, 0, tzinfo=timezone.utc)
    end = start + timedelta(minutes=30)
    
    exp = calculate_real_exp(start, end, activity_type="NORMAL", is_in_room=False)
    
    assert exp == EXPECTED_30M_NORMAL_SOLO

def test_calculate_real_exp_time_trial_in_room():
    start = datetime(2026, 5, 12, 10, 0, 0, tzinfo=timezone.utc)
    end = start + timedelta(minutes=20)
    
    exp = calculate_real_exp(start, end, activity_type="TIME_TRIAL", is_in_room=True)
    
    assert exp == EXPECTED_20M_TIME_TRIAL_ROOM

def test_calculate_real_exp_time_travel_cheat():
    start = datetime(2026, 5, 12, 10, 30, 0, tzinfo=timezone.utc)
    end = start - timedelta(minutes=30) 
    
    exp = calculate_real_exp(start, end, activity_type="NORMAL", is_in_room=False)
    
    assert exp == EXPECTED_CHEAT_OR_MICRO

def test_calculate_real_exp_micro_session():
    start = datetime(2026, 5, 12, 10, 0, 0, tzinfo=timezone.utc)
    end = start + timedelta(seconds=5)
    
    exp = calculate_real_exp(start, end, activity_type="NORMAL", is_in_room=False)
    
    assert exp == EXPECTED_CHEAT_OR_MICRO