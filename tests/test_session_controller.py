from litestar.testing import TestClient
from app.main import app

def test_sync_sessions_endpoint():
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
        assert response.json()["status"] == "success"