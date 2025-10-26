# Notification Service  
  
A lightweight FastAPI-based microservice that receives webhook events (e.g. appointment lifecycle events), enqueues them for asynchronous processing, and simulates notification dispatch via a background worker.  
  
## Architecture Overview  
- FastAPI application (`app/main.py`).  
- Webhook ingestion endpoint (`/webhook/events`) validates and ACKs events.  
- In-memory asyncio queue (`app/services/queue_service.py`) for decoupling ingestion from processing.  
- Background worker (`app/workers/event_worker.py`) started on application startup consumes queued events.  
- Health endpoints: liveness `/healthcheck/live`, readiness `/healthcheck/ready`, general `/healthcheck/`.  
- Structured INFO logging to stdout (Docker-friendly).  
  
### Data Model (EventPayload)  
Fields accepted on POST /webhook/events:  
- event_type (str, required)  
- appointment_id (str, required)  
- patient_id (str, optional)  
- doctor_id (str, optional)  
- slot (object/dict, optional)  
- status (str, optional)  
- metadata (object/dict, optional)  
  
## Endpoints  
1. GET /healthcheck/  
   - Response: `{ "status": "ok", "trace_id": "<uuid>" }`  
   - Purpose: Simple liveness + trace id for correlation.  
2. GET /healthcheck/live  
   - Response: `{ "status": "alive" }`  
   - Purpose: Container/process liveness probe target.  
3. GET /healthcheck/ready  
   - Response: `{ "status": "ready" }` OR 503 `{ "detail": "worker not started" }`  
   - Purpose: Readiness (verifies background worker started).  
4. POST /webhook/events  
   - Request JSON body: see EventPayload above.  
   - Response: `{ "ack": true, "trace_id": "<uuid>" }`  
   - Side effect: Event placed onto internal async queue; worker processes it.  
  
### Example Requests
```bash
# Healthcheck
curl -s $(minikube service notification-service --url)/healthcheck/
# Liveness
curl -s $(minikube service notification-service --url)/healthcheck/live
# Readiness
curl -s $(minikube service notification-service --url)/healthcheck/ready
# Post an event
curl -X POST $(minikube service notification-service --url)/webhook/events \
  -H 'Content-Type: application/json' \
  -d '{"event_type":"APPOINTMENT_CREATED","appointment_id":"A123","patient_id":"P9","doctor_id":"D7","status":"created"}'
```  
  
## Local Development (Non-Kubernetes)  
```bash  
# Install deps  
pip install -r requirements.txt  
# Run  
bash run.sh  
# Access  
curl http://localhost:8000/healthcheck/live  
curl http://localhost:8000/healthcheck/ready  
```  
  
## Container Build & Run
```bash
docker build -t kams97/notification_service:latest .
docker run --rm -p 8000:8000 kams97/notification_service:latest
curl http://localhost:8000/healthcheck/live
```  
  
## Running on Minikube (Local Kubernetes)  
Prerequisites:  
- Docker installed  
- Minikube installed (`minikube start` succeeds)  
- kubectl configured (comes with Minikube)  
  
Steps:  
```bash  
# 1. Start Minikube  
minikube start  
  
# 2. (Optional) Build image inside Minikube Docker daemon to avoid pushing remotely  
eval $(minikube docker-env)  
docker build -t kams97/notification_service:latest .  
  
# 3. Apply manifests  
kubectl apply -f kube/deployment.yaml  
kubectl apply -f kube/service.yaml  
  
# 4. Access service (LoadBalancer mapped via Minikube helper)  
minikube service notification-service  
# or get raw URL  
minikube service notification-service --url  
```  
The Service definition exposes:  
- Service Port: 5000 (mapped to container 8000)  
- NodePort: 31110 (reachable at `http://$(minikube ip):31110` if needed)  
  
## Observability & Logging  
- INFO-level logs go to stdout (visible via `docker logs <container>` or `kubectl logs <pod>`).  
- Each request / event includes a `trace_id` UUID for correlation.  
- Future: metrics, external queue, PII masking.  
  
## Health & Readiness  
- Liveness: `/healthcheck/live` (returns alive if process running).  
- Readiness: `/healthcheck/ready` (200 only after worker started; 503 otherwise).  
- General: `/healthcheck/` (basic status + trace id).


## Troubleshooting  
- Readiness failing (503): worker not started yet; wait a few seconds after pod start.  
- No logs: Ensure image uses provided CMD `bash run.sh`.  
- 404 endpoints: Confirm trailing slashes and paths.  
  
## Quick Reference
```bash
eval $(minikube docker-env); docker build -t kams97/notification_service:latest .
kubectl apply -f kube/deployment.yaml -f kube/service.yaml
minikube service notification-service
curl $(minikube service notification-service --url)/healthcheck/ready
```

---
