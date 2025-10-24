from fastapi import APIRouter, Request, HTTPException
from uuid import uuid4
from app.services.queue_service import worker_started

router = APIRouter(prefix="/healthcheck", tags=["Healthcheck"])

@router.get("/")
async def healthcheck(request: Request):
    trace_id = str(uuid4())
    return {"status": "ok", "trace_id": trace_id}

@router.get("/live")
async def liveness():
    # Basic process up indicator
    return {"status": "alive"}

@router.get("/ready")
async def readiness():
    if not worker_started:
        # Not ready yet, worker hasn't started
        raise HTTPException(status_code=503, detail="worker not started")
    return {"status": "ready"}
