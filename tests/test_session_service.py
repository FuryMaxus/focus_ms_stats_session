import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from datetime import datetime, timezone, timedelta

from app.domain.structs import SessionStruct
from app.services.session_service import process_focus_sessions

@pytest.mark.asyncio
async def test_process_focus_sessions_calculates_math_correctly():
    
    mock_repo = AsyncMock()
    mock_repo.add_many = AsyncMock(return_value=None)
    
    seguro_user_id = str(uuid4())
    ahora = datetime.now(timezone.utc)

    sessions = [
        SessionStruct(
            activity_type="NORMAL",
            start_time=ahora,
            end_time=ahora + timedelta(minutes=30),  
            client_reported_exp=0,
            room_id=None
        ),
        SessionStruct(
            activity_type="TIME_TRIAL",
            start_time=ahora + timedelta(hours=1),
            end_time=ahora + timedelta(hours=1, minutes=15), 
            client_reported_exp=0,
            room_id=uuid4() 
        )
    ]

    result = await process_focus_sessions(seguro_user_id, sessions, mock_repo)


    assert "total_exp" in result
    assert "time_trials_completed" in result
    assert result["time_trials_completed"] == 1
    assert result["total_exp"] > 0 

    mock_repo.add_many.assert_called_once()
    modelos_guardados = mock_repo.add_many.call_args[0][0]
    assert len(modelos_guardados) == 2
    assert str(modelos_guardados[0].user_id) == seguro_user_id


@pytest.mark.asyncio
async def test_process_focus_sessions_empty_list():
    mock_repo = AsyncMock()
    result = await process_focus_sessions(str(uuid4()), [], mock_repo)

    assert result["total_exp"] == 0
    assert result["time_trials_completed"] == 0
    mock_repo.add_many.assert_not_called()