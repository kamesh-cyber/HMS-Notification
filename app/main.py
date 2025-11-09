from fastapi import FastAPI
from app.routes import webhook, healtcheck
from app.services.queue_service import start_queue_worker

app = FastAPI(
    title="Notification Service",
    description="A webhook-based notification service with versioned APIs and basic authentication",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include v1 routes
app.include_router(webhook.router)
app.include_router(healtcheck.router)

@app.on_event("startup")
async def startup_event():
    await start_queue_worker()

@app.get("/")
async def root():
    return {
        "service": "Notification Service",
        "version": "1.0.0",
        "api_version": "v1",
        "docs": "/docs"
    }

