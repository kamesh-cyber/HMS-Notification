# Notification Service  
  
A lightweight FastAPI-based microservice that receives webhook events (e.g. appointment lifecycle events), enqueues them for asynchronous processing, and simulates notification dispatch via a background worker.  
  
## Architecture Overview  
- FastAPI application (`app/main.py`).  
- **Versioned APIs**: All endpoints are under `/v1/` prefix for API versioning.
- **Basic Authentication**: Webhook endpoints require HTTP Basic Auth credentials.
- Webhook ingestion endpoint (`/v1/webhook/events`) validates and ACKs events.  
- In-memory asyncio queue (`app/services/queue_service.py`) for decoupling ingestion from processing.  
- Background worker (`app/workers/event_worker.py`) started on application startup consumes queued events.  
- Health endpoints: liveness `/v1/healthcheck/live`, readiness `/v1/healthcheck/ready`, general `/v1/healthcheck/`.  
- Structured INFO logging to stdout (Docker-friendly).  
  
### Data Model (EventPayload)  
Fields accepted on POST /v1/webhook/events:  
- event_type (str, required)  
- appointment_id (str, required)  
- patient_id (str, optional)  
- doctor_id (str, optional)  
- slot (object/dict, optional)  
- status (str, optional)  
- metadata (object/dict, optional)  

## Authentication

The service uses HTTP Basic Authentication for webhook endpoints:
- **Default Username**: `admin`
- **Default Password**: `secret123`

These can be configured via environment variables:
- `BASIC_AUTH_USERNAME`: Set custom username
- `BASIC_AUTH_PASSWORD`: Set custom password

**Note**: Health check endpoints (`/v1/healthcheck/*`) do NOT require authentication as they're used by Kubernetes probes.
  
## Endpoints  
1. GET /  
   - Response: `{ "service": "Notification Service", "version": "1.0.0", "api_version": "v1", "docs": "/docs" }`  
   - Purpose: Service information and API documentation link.
2. GET /v1/healthcheck/  
   - Response: `{ "status": "ok", "trace_id": "<uuid>" }`  
   - Purpose: Simple liveness + trace id for correlation.  
   - Auth: Not required
3. GET /v1/healthcheck/live  
   - Response: `{ "status": "alive" }`  
   - Purpose: Container/process liveness probe target.  
   - Auth: Not required
4. GET /v1/healthcheck/ready  
   - Response: `{ "status": "ready" }` OR 503 `{ "detail": "worker not started" }`  
   - Purpose: Readiness (verifies background worker started).  
   - Auth: Not required
5. POST /v1/webhook/events  
   - Request JSON body: see EventPayload above.  
   - Response: `{ "ack": true, "trace_id": "<uuid>" }`  
   - Side effect: Event placed onto internal async queue; worker processes it.  
   - **Auth: Required (Basic Auth)**
  
### Example Requests
```bash
# Service info
curl -s $(minikube service notification-service --url)/

# Healthcheck (no auth required)
curl -s $(minikube service notification-service --url)/v1/healthcheck/

# Liveness
curl -s $(minikube service notification-service --url)/v1/healthcheck/live

# Readiness
curl -s $(minikube service notification-service --url)/v1/healthcheck/ready

# Post an event (with basic auth)
curl -X POST $(minikube service notification-service --url)/v1/webhook/events \
  -u admin:secret123 \
  -H 'Content-Type: application/json' \
  -d '{"event_type":"APPOINTMENT_CREATED","appointment_id":"A123","patient_id":"P9","doctor_id":"D7","status":"created"}'

# Post an event (alternative with auth header)
curl -X POST $(minikube service notification-service --url)/v1/webhook/events \
  -H 'Authorization: Basic YWRtaW46c2VjcmV0MTIz' \
  -H 'Content-Type: application/json' \
  -d '{"event_type":"APPOINTMENT_UPDATED","appointment_id":"A456","status":"confirmed"}'
```  
  
## Local Development (Non-Kubernetes)  
```bash  
# Install deps  
pip install -r requirements.txt  

# (Optional) Set custom auth credentials
export BASIC_AUTH_USERNAME=myuser
export BASIC_AUTH_PASSWORD=mypassword

# Run  
bash run.sh  

# Access  
curl http://localhost:8000/v1/healthcheck/live  
curl http://localhost:8000/v1/healthcheck/ready  

# Test webhook with auth
curl -X POST http://localhost:8000/v1/webhook/events \
  -u admin:secret123 \
  -H 'Content-Type: application/json' \
  -d '{"event_type":"TEST","appointment_id":"A1"}'
```  
  
## Container Build & Run
```bash
docker build -t kams97/notification_service:latest .

# Run with default credentials
docker run --rm -p 8000:8000 kams97/notification_service:latest

# Run with custom credentials
docker run --rm -p 8000:8000 \
  -e BASIC_AUTH_USERNAME=myuser \
  -e BASIC_AUTH_PASSWORD=mypassword \
  kams97/notification_service:latest

# Test
curl http://localhost:8000/v1/healthcheck/live
curl -X POST http://localhost:8000/v1/webhook/events \
  -u myuser:mypassword \
  -H 'Content-Type: application/json' \
  -d '{"event_type":"TEST","appointment_id":"A1"}'
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

### Environment Variables in Kubernetes
The deployment sets the following environment variables:
- `BASIC_AUTH_USERNAME`: admin (default)
- `BASIC_AUTH_PASSWORD`: secret123 (default)
- `ENV`: production
- `DEBUG`: False

**Security Note**: For production, use Kubernetes Secrets instead of plain environment variables:
```bash
# Create secret
kubectl create secret generic notification-auth \
  --from-literal=username=admin \
  --from-literal=password=secret123

# Update deployment.yaml to reference the secret:
# env:
#   - name: BASIC_AUTH_USERNAME
#     valueFrom:
#       secretKeyRef:
#         name: notification-auth
#         key: username
#   - name: BASIC_AUTH_PASSWORD
#     valueFrom:
#       secretKeyRef:
#         name: notification-auth
#         key: password
```
  
## Observability & Logging  
- INFO-level logs go to stdout (visible via `docker logs <container>` or `kubectl logs <pod>`).  
- Each request / event includes a `trace_id` UUID for correlation.  
- Future: metrics, external queue, PII masking.  
  
## Health & Readiness  
- Liveness: `/v1/healthcheck/live` (returns alive if process running).  
- Readiness: `/v1/healthcheck/ready` (200 only after worker started; 503 otherwise).  
- General: `/v1/healthcheck/` (basic status + trace id).
- **All health endpoints are accessible without authentication.**


## Troubleshooting  
- Readiness failing (503): worker not started yet; wait a few seconds after pod start.  
- No logs: Ensure image uses provided CMD `bash run.sh`.  
- 404 endpoints: Confirm paths use `/v1/` prefix.
- 401 Unauthorized: Check that you're providing correct Basic Auth credentials with webhook requests.
- Health checks failing: Ensure you're using `/v1/healthcheck/live` and `/v1/healthcheck/ready` paths.
  
## Quick Reference
```bash
# Build and deploy
eval $(minikube docker-env); docker build -t kams97/notification_service:latest .
kubectl apply -f kube/deployment.yaml -f kube/service.yaml
minikube service notification-service

# Test endpoints
curl $(minikube service notification-service --url)/v1/healthcheck/ready
curl -X POST $(minikube service notification-service --url)/v1/webhook/events \
  -u admin:secret123 \
  -H 'Content-Type: application/json' \
  -d '{"event_type":"TEST","appointment_id":"A1"}'
```

---
