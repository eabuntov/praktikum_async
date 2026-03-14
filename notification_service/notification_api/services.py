from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models import Notification, NotificationTarget
from kafka_producer import publish_notification


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def create_instant_notification(
        self,
        event_key: str,
        user_id: str,
        payload: dict,
        idempotency_key: str | None,
    ) -> Notification:
        notification = Notification(
            event_key=event_key,
            payload=payload,
            idempotency_key=idempotency_key,
        )

        target = NotificationTarget(
            target_type="user",
            target_value=str(user_id),
            notification=notification,
        )

        self.db.add(notification)
        self.db.add(target)

        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()

        publish_notification(str(notification.id))
        return notification

    def create_scheduled_notification(
            self,
            event_key: str,
            user_id: str,
            payload: dict,
            scheduled_at: datetime,
            idempotency_key: str | None,
    ):
        notification = Notification(
            event_key=event_key,
            payload=payload,
            status="queued",
            scheduled_at=scheduled_at,
            idempotency_key=idempotency_key,
        )

        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)

        # create target
        notification.add_user_target(user_id)

        return notification

    def create_periodic_notification(
            self,
            event_key: str,
            user_id: str,
            payload: dict,
            cron_expression: str,
            start_at: datetime | None,
            repeat_until: datetime | None,
            idempotency_key: str | None,
    ):
        notification = Notification(
            event_key=event_key,
            payload=payload,
            status="queued",
            scheduled_at=start_at,
            idempotency_key=idempotency_key,
            is_periodic=True,
            cron_expression=cron_expression,
            repeat_until=repeat_until,
        )

        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)

        notification.add_user_target(user_id)

        return notification
