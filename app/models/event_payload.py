from pydantic import BaseModel
from typing import Optional, Dict, Any

class EventPayload(BaseModel):
    event_type: str
    appointment_id: str
    patient_id: Optional[str] = None
    doctor_id: Optional[str] = None
    slot: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
