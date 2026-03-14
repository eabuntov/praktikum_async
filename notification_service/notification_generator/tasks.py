import os
from datetime import datetime, timedelta
import requests
from taskiq import TaskiqDepends, Context
from broker import broker
from analytics import has_events_since
from state import GeneratorState
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("NOTIF_DB_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

BASE_URL = "http://notification_api:8000/v1/internal/notifications"
INSTANT_URL = f"{BASE_URL}/instant"
SCHEDULED_URL = f"{BASE_URL}/scheduled"
PERIODIC_URL = f"{BASE_URL}/periodic"


def get_or_create_state(db, job_name: str, default_delta: timedelta) -> GeneratorState:
    state = db.get(GeneratorState, job_name)
    print(job_name)
    if state is None:
        state = GeneratorState(job_name, default_delta)
    if not state:
        state = GeneratorState(
            job_name=job_name,
            last_processed_at=datetime.utcnow() - default_delta,
            version="v1",
        )
        db.add(state)
        db.commit()

    return state


@broker.task
async def generate_one_time_notification(
    event_key: str,
    target_type: str,
    target_value: str,
    payload: dict,
    context: Context = TaskiqDepends(),
):
    """
    Create a one-time notification immediately.
    """

    response = requests.post(
        INSTANT_URL,
        json={
            "event_key": event_key,
            "target": {
                "type": target_type,
                "value": target_value,
            },
            "payload": payload,
        },
        timeout=5,
    )
    response.raise_for_status()

@broker.task(schedule=[{"cron": "* * * * *"}])
async def every_minute_notifications(context: Context = TaskiqDepends()):
    """
    Runs every minute.
    """

    db = SessionLocal()

    try:
        state = get_or_create_state(db, "minute_job", timedelta(minutes=1))

        if not has_events_since(state.last_processed_at):
            return

        payload = {
            "timestamp": datetime.now().isoformat(),
        }

        response = requests.post(
            INSTANT_URL,
            json={
                "event_key": "minute_event",
                "target": {
                    "type": "segment",
                    "value": "active_users",
                },
                "payload": payload,
            },
            timeout=5,
        )
        response.raise_for_status()

        state.last_processed_at = datetime.now()
        db.commit()

    finally:
        db.close()


@broker.task(schedule=[{"cron": "0 9 * * *"}])
async def daily_digest(context: Context = TaskiqDepends()):
    """
    Runs every day at 09:00 UTC.
    """

    db = SessionLocal()

    try:
        state = get_or_create_state(db, "daily_digest", timedelta(days=1))

        if not has_events_since(state.last_processed_at):
            return

        payload = {
            "date": datetime.now().strftime("%Y-%m-%d"),
        }

        response = requests.post(
            INSTANT_URL,
            json={
                "event_key": "daily_digest",
                "target": {
                    "type": "segment",
                    "value": f"daily_active_{state.version}",
                },
                "payload": payload,
            },
            timeout=5,
        )
        response.raise_for_status()

        state.last_processed_at = datetime.utcnow()
        db.commit()

    finally:
        db.close()



@broker.task(schedule=[{"cron": "0 9 * * 1"}])
async def weekly_digest(context: Context = TaskiqDepends()):
    """
    Runs every Monday at 09:00 UTC.
    """

    db = SessionLocal()

    try:
        state = get_or_create_state(db, "weekly_digest", timedelta(days=7))

        if not has_events_since(state.last_processed_at):
            return

        payload = {
            "week": datetime.now().strftime("%Y-W%U"),
        }

        response = requests.post(
            INSTANT_URL,
            json={
                "event_key": "weekly_digest",
                "target": {
                    "type": "segment",
                    "value": f"weekly_active_{state.version}",
                },
                "payload": payload,
            },
            timeout=5,
        )
        response.raise_for_status()

        state.last_processed_at = datetime.utcnow()
        db.commit()

    finally:
        db.close()

