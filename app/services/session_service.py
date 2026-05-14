import httpx
import os
from uuid import UUID
from app.domain.structs import SessionStruct
from app.models.session import FocusSessionModel
from app.services.stats_logic import calculate_real_exp
from app.repositories.session_repository import SessionRepository

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")


async def process_focus_sessions(
        sessions: list[SessionStruct],
        session_repo: SessionRepository
    ) -> dict:

    if not sessions:
        return {"total_exp": 0, "auth_status": None, "new_items": []}
    
    user_id = str(sessions[0].user_id)

    total_exp, time_trials_completed = await _save_sessions_to_db(sessions, session_repo)
    new_level_data = None
    loot_drops = []

    if total_exp > 0:
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            new_level_data = await _notify_auth(client, user_id, total_exp)
            
            if time_trials_completed > 0:
                drops_tt = await _notify_inventory(
                    client,
                    user_id,
                    time_trials_completed, 
                    "TIME_TRIAL_VICTORY"
                )
                loot_drops.extend(drops_tt)

            if new_level_data and new_level_data.get("leveled_up") is True:
                drops_level = await _notify_inventory(
                    client,
                    user_id,1, 
                    "LEVEL_UP_REWARD"
                )
                loot_drops.extend(drops_level)
    
    return {
        "total_exp": total_exp,
        "auth_status": new_level_data,
        "new_items": loot_drops
    }


async def _save_sessions_to_db(
        sessions: list[SessionStruct],
        session_repo: SessionRepository
    ) -> tuple[int, int]:

    total_exp = 0
    time_trials = 0
    models_to_insert = []

    for data in sessions:
        is_in_room = data.room_id is not None
        real_exp = calculate_real_exp(
            data.start_time,
            data.end_time,
            data.activity_type,
            is_in_room
        )
        total_exp += real_exp
        if data.activity_type == "TIME_TRIAL":
            time_trials += 1
        new_session = FocusSessionModel(
            user_id=data.user_id,
            room_id=data.room_id,
            activity_type=data.activity_type,
            start_time=data.start_time,
            end_time=data.end_time,
            exp_earned=real_exp
        )
        models_to_insert.append(new_session)
        
    if models_to_insert:
        await session_repo.add_many(models_to_insert)

    return total_exp, time_trials

async def _notify_auth(
        client: httpx.AsyncClient,
        user_id: str,
        total_exp: int
    ) -> dict | None:

    try:
        response = await client.patch(
            f"${AUTH_SERVICE_URL}/internal/users/{user_id}/add-exp",
            json={"exp_to_add": total_exp}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error al conectar con Auth: {e}")
        return {
            "new_exp": total_exp, 
            "leveled_up": False, 
            "current_level": 1,
            "error": "Auth service unavailable"
        }
    

async def _notify_inventory(
        client: httpx.AsyncClient,
        user_id: str,
        amount: int,
        event_type: str
    ) -> list[str]:
    drops = []

    for _ in range(amount):
        try:
            response = await client.post(
                "http://inventory-service:8000/internal/trigger-reward",
                json={"user_id": user_id, "event_type": event_type}
            )
            if response.status_code == 200:
                reward = response.json().get("item_id")
                if reward:
                    drops.append(reward)
        except Exception as e:
            print(f"Warning: Inventory service unreachable for event {event_type}: {e}")

    return drops


    