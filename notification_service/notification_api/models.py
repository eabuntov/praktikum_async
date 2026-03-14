import uuid
from sqlalchemy import (
    Column,
    String,
    JSON,
    DateTime,
    Enum,
    ForeignKey,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_key = Column(String, nullable=False)
    template_id = Column(UUID(as_uuid=True), nullable=True)
    payload = Column(JSON, nullable=False)
    status = Column(String, default="queued")
    idempotency_key = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("event_key", "idempotency_key", name="uniq_event_idempotency"),
    )

    targets = relationship("NotificationTarget", back_populates="notification")


class NotificationTarget(Base):
    __tablename__ = "notification_targets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notification_id = Column(
        UUID(as_uuid=True),
        ForeignKey("notifications.id", ondelete="CASCADE"),
    )
    target_type = Column(String, nullable=False)  # user | segment
    target_value = Column(String, nullable=False)

    notification = relationship("Notification", back_populates="targets")
