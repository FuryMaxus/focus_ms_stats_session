import os
import pytest
import jwt
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

from litestar import Litestar
from litestar.testing import TestClient
from litestar.di import Provide

from app.api.v1.sessionController import SessionController
from app.core.security import jwt_auth
from app.repositories.session_repository import FocusSessionRepository

os.environ["SECRET_KEY"] = "tu_clave_super_secreta"

def get_test_token() -> str:

    secret = jwt_auth.token_secret

    if not isinstance(secret, str):
        secret = str(secret)

    now = datetime.now(timezone.utc)
    payload = {
        "sub": "123e4567-e89b-12d3-a456-426614174000",
        "exp": now + timedelta(minutes=10),
        "iat": now
    }
    
    return jwt.encode(payload, secret, algorithm="HS256")

@pytest.fixture
def auth_headers():
    return {"Authorization": f"Bearer {get_test_token()}"}

@pytest.fixture
def mock_repo():
    repo = AsyncMock(spec=FocusSessionRepository) 
    repo.add_many = AsyncMock(return_value=None)
    return repo

@pytest.fixture
def client(mock_repo):
    test_app = Litestar(
        route_handlers=[SessionController],
        on_app_init=[jwt_auth.on_app_init],
        dependencies={
            "session_repo": Provide(lambda: mock_repo, sync_to_thread=False)
        },
        debug=True
    )
    with TestClient(app=test_app) as client:
        yield client

def test_controller_batch_sync_success(client: TestClient, auth_headers: dict, mock_repo: AsyncMock):
    payload = {
        "sessions": [
            {
                "activity_type": "NORMAL",
                "start_time": "2026-05-26T10:00:00Z",
                "end_time": "2026-05-26T10:45:00Z",
                "client_reported_exp": 135,
                "room_id": None
            }
        ]
    }

    response = client.post("/api/v1/sessions/batch", json=payload, headers=auth_headers)
    
    assert response.status_code == 201, f"Error: {response.text}"
    data = response.json()
    assert "total_exp" in data
    assert "time_trials_completed" in data
    mock_repo.add_many.assert_called_once()

def test_controller_batch_sync_invalid_times(client: TestClient, auth_headers: dict):
    payload = {
        "sessions": [
            {
                "activity_type": "NORMAL",
                "start_time": "2026-05-26T12:00:00Z",
                "end_time": "2026-05-26T11:00:00Z",  
                "room_id": None
            }
        ]
    }
    response = client.post("/api/v1/sessions/batch", json=payload, headers=auth_headers)
    assert response.status_code == 400, f"Error: {response.text}"