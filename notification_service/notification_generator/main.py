import asyncio

from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource

from broker import broker
import tasks  # noqa: F401

scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)

async def run():
    await broker.startup()
    await scheduler.startup()
    while True:
        task = await tasks.generate_one_time_notification.kiq(1)
        await task.wait_result(timeout=2)
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(run())
