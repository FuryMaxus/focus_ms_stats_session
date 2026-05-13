import httpx
from app.domain.structs import SessionStruct
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.session import FocusSession
from app.services.stats_logic import calculate_real_exp

async def process_focus_sessions(
        sessions: list[SessionStruct],
        db_session: AsyncSession
    ) -> dict:

    if not sessions:
        return {"total_xp": 0, "auth_status": None, "new_items": []}
    
    user_id = str(sessions[0].user_id)

    total_xp, time_trials_completed = _save_sessions_to_db(sessions, db_session)
    new_level_data = None
    loot_drops = []

    if total_xp > 0:
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            new_level_data = await _notify_auth(client, user_id, total_xp)
            
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
        "total_xp": total_xp,
        "auth_status": new_level_data,
        "new_items": loot_drops
    }


def _save_sessions_to_db(
        sessions: list[SessionStruct],
        db_session: AsyncSession
    ) -> tuple[int, int]:

    total_xp = 0
    time_trials = 0

    for data in sessions:
        is_in_room = True if data.room_id else False
        real_exp = calculate_real_exp(
            data.start_time,
            data.end_time,
            data.activity_type,
            is_in_room
        )
        total_xp += real_exp
        if data.activity_type == "TIME_TRIAL":
            time_trials += 1
        new_session = FocusSession(
            user_id=data.user_id,
            room_id=data.room_id,
            activity_type=data.activity_type,
            start_time=data.start_time,
            end_time=data.end_time,
            xp_earned=real_exp
        )
        db_session.add(new_session)

    return total_xp, time_trials

async def _notify_auth(
        client: httpx.AsyncClient,
        user_id: str,
        total_xp: int
    ) -> dict | None:

    try:
        response = await client.patch(
            f"http://auth-service:8000/internal/users/{user_id}/add-xp",
            json={"gained_xp": total_xp}
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Warning: Auth service unreachable: {e}")
    return None

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


    