import asyncio
from app.workers.event_worker import process_event
from app.utils.logger import setup_logger

# Global event queue

logger = setup_logger('queue_service')
__all__ = ["event_queue", "start_queue_worker", "worker_started"]

event_queue = asyncio.Queue()
worker_started = False

async def start_queue_worker():
    global worker_started
    logger.info("Starting background queue worker...")
    asyncio.create_task(queue_consumer())
    worker_started = True

async def queue_consumer():
    while True:
        event = await event_queue.get()
        try:
            await process_event(event)
        finally:
            event_queue.task_done()
