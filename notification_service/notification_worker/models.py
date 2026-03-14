import uuid
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Enum,
    ForeignKey,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True)
    event_key = Column(String, nullable=False)
    payload = Column(String)
    template_id = Column(UUID(as_uuid=True))


class NotificationTarget(Base):
    __tablename__ = "notification_targets"

    id = Column(UUID(as_uuid=True), primary_key=True)
    notification_id = Column(UUID(as_uuid=True), ForeignKey("notifications.id"))
    target_type = Column(String)  # user | segment
    target_value = Column(String)


class NotificationSendLog(Base):
    __tablename__ = "notification_send_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notification_id = Column(UUID(as_uuid=True))
    user_id = Column(UUID(as_uuid=True))
    channel = Column(String)
    status = Column(String)
    error = Column(String, nullable=True)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint(
            "notification_id",
            "user_id",
            "channel",
            name="uniq_notification_user_channel",
        ),
    )
