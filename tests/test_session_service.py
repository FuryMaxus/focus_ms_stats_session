import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4
from datetime import datetime, timezone, timedelta

from app.domain.structs import SessionStruct
from app.services.session_service import process_focus_sessions

@pytest.mark.asyncio
async def test_process_focus_sessions():
    mock_session_repo = AsyncMock()
    
    start = datetime(2026, 5, 12, 10, 0, 0, tzinfo=timezone.utc)
    session_data = SessionStruct(
        user_id=uuid4(),
        activity_type="TIME_TRIAL",
        start_time=start,
        end_time=start + timedelta(minutes=20),
        client_reported_xp=437,
        room_id=uuid4() 
    )
    
    with patch("app.services.session_service._notify_auth", new_callable=AsyncMock) as mock_auth, \
         patch("app.services.session_service._notify_inventory", new_callable=AsyncMock) as mock_inv:
        
        mock_auth.return_value = {"new_xp": 1500, "leveled_up": True, "current_level": 5}
        
        mock_inv.return_value = ["espada_legendaria"]

        result = await process_focus_sessions([session_data], mock_session_repo)        
        assert result["total_xp"] > 0
        assert result["auth_status"]["leveled_up"] is True
        assert "espada_legendaria" in result["new_items"]
        
        mock_session_repo.add_many.assert_called_once()
        
        assert mock_inv.call_count == 2