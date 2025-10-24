from fastapi import APIRouter, Request, HTTPException
from uuid import uuid4
from app.models.event_payload import EventPayload
from app.services.queue_service import event_queue
from app.utils.logger import setup_logger

logger = setup_logger("webhook")

router = APIRouter(prefix="/webhook", tags=["Webhook"])

@router.post("/events")
async def receive_event(payload: EventPayload, request: Request):
    trace_id = str(uuid4())

    # Basic validation (can add signature check later)
    if not payload.event_type or not payload.appointment_id:
        raise HTTPException(status_code=400, detail="Invalid payload")

    logger.info(f"[{trace_id}] Received event: {payload.event_type}")

    # Push to internal queue
    await event_queue.put({"trace_id": trace_id, "payload": payload.dict()})

    return {"ack": True, "trace_id": trace_id}
