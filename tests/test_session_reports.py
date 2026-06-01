import os
import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from unittest.mock import AsyncMock, patch

from litestar.testing import TestClient

os.environ["SECRET_KEY"] = "clave_super_secreta"

from app.main import app 
from app.models.focus_session import FocusSessionModel

@pytest.fixture
def client():
    with TestClient(app=app) as client:
        yield client

@pytest.fixture
def mock_session_records():
    return [
        FocusSessionModel(
            id=uuid4(),
            user_id=uuid4(),
            room_id=None,
            activity_type="NORMAL",
            start_time=datetime(2026, 5, 26, 10, 0, tzinfo=timezone.utc),
            end_time=datetime(2026, 5, 26, 11, 0, tzinfo=timezone.utc),
            exp_earned=100
        ),
        FocusSessionModel(
            id=uuid4(),
            user_id=uuid4(),
            room_id=uuid4(),
            activity_type="TIME_TRIAL",
            start_time=datetime(2026, 5, 25, 15, 0, tzinfo=timezone.utc),
            end_time=datetime(2026, 5, 25, 16, 0, tzinfo=timezone.utc),
            exp_earned=150
        )
    ]

def get_auth_headers(role: str, user_id: str) -> dict:
    import jwt
    now = datetime.now(timezone.utc)
    from app.core.security import jwt_auth
    payload = {
        "sub": user_id, 
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=15)
    }
    token = jwt.encode(payload, jwt_auth.token_secret, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}


@patch("app.api.v1.sessionController.FocusSessionRepository.get_reports_dynamically", new_callable=AsyncMock)
def test_student_can_only_query_own_data(mock_get_reports, client: TestClient, mock_session_records):
    mock_get_reports.return_value = mock_session_records
    
    student_id = str(uuid4())
    other_user_id = str(uuid4())
    headers = get_auth_headers(role="student", user_id=student_id)

    response = client.get(
        f"/api/v1/sessions/reports?user_id={other_user_id}", 
        headers=headers
    )

    assert response.status_code == 200
    
    called_kwargs = mock_get_reports.call_args.kwargs
    assert str(called_kwargs["user_id"]) == student_id
    assert str(called_kwargs["user_id"]) != other_user_id


@patch("app.api.v1.sessionController.FocusSessionRepository.get_reports_dynamically", new_callable=AsyncMock)
def test_dm_can_query_other_users_data(mock_get_reports, client: TestClient, mock_session_records):
    mock_get_reports.return_value = mock_session_records
    
    dm_id = str(uuid4())
    target_student_id = str(uuid4())
    headers = get_auth_headers(role="dm", user_id=dm_id)

    response = client.get(
        f"/api/v1/sessions/reports?user_id={target_student_id}", 
        headers=headers
    )

    assert response.status_code == 200
    
    called_kwargs = mock_get_reports.call_args.kwargs
    assert str(called_kwargs["user_id"]) == target_student_id


@patch("app.api.v1.sessionController.FocusSessionRepository.get_reports_dynamically", new_callable=AsyncMock)
def test_pagination_and_filters_are_passed_correctly(mock_get_reports, client: TestClient, mock_session_records):
    mock_get_reports.return_value = mock_session_records
    
    student_id = str(uuid4())
    headers = get_auth_headers(role="student", user_id=student_id)

    response = client.get(
        "/api/v1/sessions/reports?limit=10&offset=20&sort_order=asc&start_date=2026-01-01T00:00:00Z", 
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    
    assert data["total_count"] == 2
    assert len(data["reports"]) == 2
    
    called_kwargs = mock_get_reports.call_args.kwargs
    assert called_kwargs["limit"] == 10
    assert called_kwargs["offset"] == 20
    assert called_kwargs["sort_order"] == "asc"
    assert called_kwargs["start_date"] is not None