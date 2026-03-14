from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db import SessionLocal
from schemas import (
    InstantNotificationRequest,
    ScheduledNotificationRequest,
    PeriodicNotificationRequest,
    NotificationResponse,
)
from services import NotificationService

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/v1/notifications/instant",
    response_model=NotificationResponse,
)
def create_instant_notification(
    request: InstantNotificationRequest,
    db: Session = Depends(get_db),
):
    service = NotificationService(db)
    notification = service.create_instant_notification(
        event_key=request.event_key,
        user_id=str(request.user_id),
        payload=request.payload,
        idempotency_key=request.idempotency_key,
    )

    return NotificationResponse(
        notification_id=notification.id,
        status=notification.status,
    )

@router.post(
    "/v1/notifications/scheduled",
    response_model=NotificationResponse,
)
def create_scheduled_notification(
    request: ScheduledNotificationRequest,
    db: Session = Depends(get_db),
):
    service = NotificationService(db)

    notification = service.create_scheduled_notification(
        event_key=request.event_key,
        user_id=str(request.user_id),
        payload=request.payload,
        scheduled_at=request.scheduled_at,
        idempotency_key=request.idempotency_key,
    )

    return NotificationResponse(
        notification_id=notification.id,
        status=notification.status,
    )


@router.post(
    "/v1/notifications/periodic",
    response_model=NotificationResponse,
)
def create_periodic_notification(
    request: PeriodicNotificationRequest,
    db: Session = Depends(get_db),
):
    service = NotificationService(db)

    notification = service.create_periodic_notification(
        event_key=request.event_key,
        user_id=str(request.user_id),
        payload=request.payload,
        cron_expression=request.cron_expression,
        start_at=request.start_at,
        repeat_until=request.repeat_until,
        idempotency_key=request.idempotency_key,
    )

    return NotificationResponse(
        notification_id=notification.id,
        status=notification.status,
    )
