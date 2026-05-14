from litestar.testing import TestClient
from unittest.mock import patch, AsyncMock
from litestar.di import Provide
import os
from litestar.security.jwt import Token
from datetime import datetime, timedelta, timezone
from uuid import uuid4

os.environ["DATABASE_URL"] = "postgresql+asyncpg:///:memory:"
os.environ["SECRET_KEY"] = "clave_secreta_para_tests"

from app.main import app
from app.core.security import SECRET_KEY

def test_sync_sessions_endpoint()-> None:

    app.dependencies["session_repo"] = Provide(lambda: AsyncMock(), sync_to_thread=False)

    test_uuid = uuid4()

    token_obj = Token(
        sub=str(test_uuid), 
        exp=datetime.now(timezone.utc) + timedelta(minutes=10)
    )
    encoded_token = token_obj.encode(secret=SECRET_KEY, algorithm="HS256")
    payload = [{
        "user_id": str(test_uuid),  
        "activity_type": "NORMAL",
        "start_time": "2026-05-14T10:00:00Z",
        "end_time": "2026-05-14T10:45:00Z",
        "client_reported_exp": 150,
        "room_id": None
    }]

    with patch("app.api.v1.sessionController.process_focus_sessions", new_callable=AsyncMock) as mock_process:        
        mock_process.return_value = {"new_exp": 150, "leveled_up": False}

        with TestClient(app=app) as client:
            response = client.post(
                "/sessions/sync", 
                json=payload,
                headers={"Authorization": f"Bearer {encoded_token}"}
            )
            
            assert response.status_code == 201 
            data = response.json()
            assert "success" in data["status"]