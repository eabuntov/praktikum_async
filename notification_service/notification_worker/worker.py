import uuid
from sqlalchemy.exc import IntegrityError

from db import SessionLocal
from kafka_consumer import consumer
from models import (
    Notification,
    NotificationTarget,
    NotificationSendLog,
)
from notif_email import send_email
from templates import render_template
from settings import can_send_email


def resolve_targets(db, notification_id):
    targets = (
        db.query(NotificationTarget)
        .filter(NotificationTarget.notification_id == notification_id)
        .all()
    )

    users = set()

    for target in targets:
        if target.target_type == "user":
            users.add(target.target_value)

        elif target.target_type == "segment":
            # Stub: resolve segment → user_ids
            users.update(resolve_segment(target.target_value))

    return users


def resolve_segment(segment_name: str) -> list[str]:
    # Placeholder: ClickHouse / materialized view
    return []


def process_notification(notification_id: str):
    db = SessionLocal()

    try:
        notification = (
            db.query(Notification)
            .filter(Notification.id == notification_id)
            .one()
        )

        users = resolve_targets(db, notification.id)

        for user_id in users:
            if not can_send_email(user_id):
                continue

            send_log = NotificationSendLog(
                notification_id=notification.id,
                user_id=uuid.UUID(user_id),
                channel="email",
                status="pending",
            )

            try:
                db.add(send_log)
                db.commit()
            except IntegrityError:
                db.rollback()
                continue  # already sent

            try:
                subject = f"Notification: {notification.event_key}"
                body = render_template(
                    "Hello {{ user_id }}",
                    {"user_id": user_id},
                )
                send_email("user@example.com", subject, body)

                send_log.status = "sent"
                db.commit()

            except Exception as e:
                send_log.status = "failed"
                send_log.error = str(e)
                db.commit()

    finally:
        db.close()


def run():
    for msg in consumer:
        notification_id = msg.value["notification_id"]

        process_notification(notification_id)

        consumer.commit()


if __name__ == "__main__":
    run()
