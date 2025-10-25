import json
import os
from abc import ABC, abstractmethod
from datetime import datetime
from redis import Redis
from typing import Any, Optional


class BaseStorage(ABC):
    """Abstract base class for saving and retrieving ETL state."""

    @abstractmethod
    def save_state(self, key: str, value: Any) -> None:
        """Save a state value by key."""
        pass

    @abstractmethod
    def retrieve_state(self, key: str) -> Optional[Any]:
        """Retrieve a previously saved value by key."""
        pass


class RedisStorage(BaseStorage):
    """Redis-backed implementation of state storage."""

    def __init__(self, redis_adapter: Redis = None, namespace: str = "etl_state:"):
        self.redis_adapter = redis_adapter or Redis(
            host=os.getenv("REDIS_HOST", "redis"),
            port=int(os.getenv("REDIS_PORT", "6739")),
            db=0,
            decode_responses=True,
        )
        self.namespace = namespace

    def _full_key(self, key: str) -> str:
        return f"{self.namespace}{key}"

    def save_state(self, key: str, value: Any) -> None:
        """охраняем состояние в виде даты или JSON-строки"""
        self.redis_adapter.set(self._full_key(key),
                               value.isoformat() if isinstance(value, datetime) else json.dumps(value))

    def retrieve_state(self, key: str) -> Optional[str | dict]:
        """Получение состояния."""
        data = self.redis_adapter.get(self._full_key(key))
        if data is None:
            return None
        try:
            datetime.fromisoformat(data)
            return data
        except:
            return json.loads(data)
