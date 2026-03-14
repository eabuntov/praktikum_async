from datetime import datetime

from pydantic import BaseModel, Field
from typing import Optional, Any
from uuid import UUID


class InstantNotificationRequest(BaseModel):
    event_key: str
    user_id: UUID
    payload: dict
    idempotency_key: Optional[str] = Field(default=None)


class ScheduledNotificationRequest(BaseModel):
    event_key: str
    user_id: UUID
    payload: dict[str, Any]
    scheduled_at: datetime
    idempotency_key: Optional[str] = None


class PeriodicNotificationRequest(BaseModel):
    event_key: str
    user_id: UUID
    payload: dict[str, Any]
    cron_expression: str = None
    start_at: Optional[datetime] = None
    repeat_until: Optional[datetime] = None
    idempotency_key: Optional[str] = None


class NotificationResponse(BaseModel):
    notification_id: UUID
    status: str
