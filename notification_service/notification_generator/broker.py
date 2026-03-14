from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

result_backend = RedisAsyncResultBackend(redis_url="redis://notification_redis:6379/1")

broker = ListQueueBroker(url="redis://notification_redis:6379/1").with_result_backend(result_backend)