from fastapi import APIRouter, Request, HTTPException
from uuid import uuid4

router = APIRouter(prefix="/healthcheck", tags=["Healthcheck"])

@router.get("/")
async def healthcheck(request: Request):
    trace_id = str(uuid4())
    return {"status": "ok", "trace_id": trace_id}

