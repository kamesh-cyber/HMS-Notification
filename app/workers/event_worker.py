import asyncio
import base64
from app.utils.logger import setup_logger
import httpx

logger = setup_logger("event_worker")
async def process_event(event):
    trace_id = event["trace_id"]
    payload = event["payload"]
    logger.info(f"[{trace_id}] Processing {payload} asynchronously...")
    # Get patient and appointment details from DB (simulated here)
    async with httpx.AsyncClient(verify=False, timeout=300.0) as client:
        credentials = 'admin:password'
        # encode in base64
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        headers = {"Authorization": f"Basic {encoded_credentials}"}
        patient_id = payload.get("patient_id")
        response = await client.get(f"http://host.docker.internal:8081/v1/patients/{patient_id}", headers=headers)
        patient_details = response.json()
        print(f"[{trace_id}] Patient details: {patient_details}")
    await asyncio.sleep(1)
    logger.info(f"[{trace_id}] Fetched details for patient {payload['patient_id']}")
    # Simulate sending notification
    await asyncio.sleep(2)
    logger.info(f"[{trace_id}] Notification for {payload['event_type']} done ✅")