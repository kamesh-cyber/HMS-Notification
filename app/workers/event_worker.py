import asyncio
from app.utils.logger import setup_logger

logger = setup_logger("event_worker")
async def process_event(event):
    trace_id = event["trace_id"]
    payload = event["payload"]
    logger.info(f"[{trace_id}] Processing {payload['event_type']} asynchronously...")

    # Simulate sending notification
    await asyncio.sleep(2)
    logger.info(f"[{trace_id}] Notification for {payload['event_type']} done ✅")