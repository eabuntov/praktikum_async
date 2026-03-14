import json
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="kafka:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)


def publish_notification(notification_id: str, priority: str = "high") -> None:
    producer.send(
        "notification.events.high",
        {
            "notification_id": notification_id,
            "priority": priority,
        },
    )
    producer.flush()
