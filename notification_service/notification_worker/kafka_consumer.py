import json
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    "notification.events.high",
    "notification.events.bulk",
    bootstrap_servers="kafka:9092",
    group_id="notification-workers",
    enable_auto_commit=False,
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
)
