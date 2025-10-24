from fastapi import FastAPI
from app.routes import webhook,healtcheck
from app.services.queue_service import start_queue_worker

app = FastAPI(title="Notification Service")

# Include routes
app.include_router(webhook.router)
app.include_router(healtcheck.router)

@app.on_event("startup")
async def startup_event():
    await start_queue_worker()
