from litestar.testing import TestClient
from unittest.mock import patch as mock_patch, AsyncMock
from litestar.di import Provide
import os

os.environ["DATABASE_URL"] = "postgresql+asyncpg:///:memory:"

from app.main import app

@mock_patch("app.api.v1.sessionController.process_focus_sessions", new_callable=AsyncMock)
def test_sync_sessions_endpoint(mock_process)-> None:

    mock_process.return_value = {"total_exp": 300, "auth_status": None, "new_items": []}
    app.dependencies["session_repo"] = Provide(lambda: AsyncMock(), sync_to_thread=False)

    with TestClient(app=app) as client:
        response = client.post(
            "/sessions/sync",
            json=[{
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "activity_type": "NORMAL",
                "start_time": "2026-05-12T10:00:00Z",
                "end_time": "2026-05-12T10:30:00Z",
                "client_reported_xp": 300,
                "room_id": None
            }]
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["total_exp"] == 300