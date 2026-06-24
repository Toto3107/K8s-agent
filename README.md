# 🤖 AI Kubernetes Agent

> An AI-powered Kubernetes troubleshooting agent that behaves like a **Senior SRE** — collects cluster evidence, reasons about failures, and suggests fixes.

![Architecture](https://img.shields.io/badge/Stack-FastAPI%20%2B%20Next.js%20%2B%20OpenRouter-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Python](https://img.shields.io/badge/Python-3.12%2B-blue)
![Node](https://img.shields.io/badge/Node-20%2B-green)

---

## 📸 What It Does

```
User clicks "Investigate Cluster"
        ↓
Select any cluster from your kubeconfig
        ↓
Backend collects Kubernetes evidence
  ├── Check Pods (CrashLoopBackOff, OOMKilled, etc.)
  ├── Read Logs (errors, exceptions, missing env vars)
  ├── Analyze Events (FailedScheduling, BackOff, etc.)
  ├── Inspect Deployments (unavailable replicas)
  └── Check Networking (selector mismatches, no endpoints)
        ↓
AI reasons about the evidence (OpenRouter LLM)
        ↓
Returns:
  • Root Cause
  • Explanation
  • Suggested Fix
  • kubectl Commands
  • Confidence Score
  • Prevention Tips
```

---

## 🏗️ Architecture

```
Frontend (Next.js + Tailwind)
    ↓
FastAPI Backend (Orchestrator)
    ↓
Kubernetes Investigation Layer
  ├── Pod Inspector       — Detects CrashLoopBackOff, OOMKilled, etc.
  ├── Logs Collector      — Filters error logs from failing pods
  ├── Events Analyzer     — Surfaces FailedScheduling, BackOff, etc.
  ├── Deployment Inspector — Checks replica availability
  └── Network Inspector   — Detects selector mismatches
    ↓
AI Kubernetes Agent (OpenRouter LLM)
    ↓
Root Cause + Suggested Fix
```

---

## 🚀 Quick Start

### Option A — Run Locally (Recommended for Development)

**1. Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/ai-kubernetes-agent.git
cd ai-kubernetes-agent
```

**2. Set up environment**
```bash
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY
```

**3. Start the backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # Add your API key
uvicorn main:app --reload --port 8000
```

**4. Start the frontend** (new terminal)
```bash
cd frontend
npm install
npm run dev
```

**5. Open the app**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

### Option B — Docker Compose

```bash
# Copy and fill in your API key
cp .env.example .env

# Start everything
docker compose up --build

# Access
# Frontend → http://localhost:3000
# Backend  → http://localhost:8000
```

> **Note:** Docker mounts `~/.kube` from your host so the backend can access your clusters.

---

## ⚙️ Environment Variables

### Backend (`backend/.env`)

| Variable | Description | Default |
|---|---|---|
| `OPENROUTER_API_KEY` | Your OpenRouter API key — [get one here](https://openrouter.ai/keys) | (required for AI) |
| `OPENROUTER_MODEL` | LLM model to use | `anthropic/claude-3-haiku` |
| `KUBECONFIG_PATH` | Path to kubeconfig file | `~/.kube/config` |

### Frontend (`frontend/.env.local`)

| Variable | Description | Default |
|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | Backend URL | `http://localhost:8000` |

> **No AI key?** The agent still works — it uses heuristic analysis based on pod status. Add an OpenRouter key for full LLM-powered diagnosis.

---

## 🧪 Test Kubernetes Failure Scenarios

The repo includes 4 real failure scenarios you can apply to your cluster:

```bash
cd k8s-test-scenarios

# Apply all scenarios
./apply-scenarios.sh

# Or apply individually
./apply-scenarios.sh 1   # CrashLoopBackOff (missing env var)
./apply-scenarios.sh 2   # ImagePullBackOff (bad image tag)
./apply-scenarios.sh 3   # OOMKilled (memory limit too low)
./apply-scenarios.sh 4   # Service selector mismatch

# Watch pods go unhealthy
kubectl get pods -w

# Run investigation (the AI will detect and explain the failure)
curl -X POST http://localhost:8000/investigate | jq

# Clean up
./apply-scenarios.sh clean
```

### Scenarios

| # | Scenario | Failure Type | How It's Triggered |
|---|---|---|---|
| 1 | `payment-service` | CrashLoopBackOff | Missing `DATABASE_URL` env var |
| 2 | `auth-service` | ImagePullBackOff | Invalid image tag `nginx:this-tag-does-not-exist-999` |
| 3 | `memory-hog` | OOMKilled | Container tries to allocate 200MB with 50MB limit |
| 4 | `frontend-svc` | Selector Mismatch | Service selects `app: frontend-v2`, pod has `app: frontend` |

---

## 📡 API Reference

### `GET /health`
Health check.

```json
{ "status": "healthy", "service": "ai-kubernetes-agent" }
```

### `GET /clusters`
List all Kubernetes contexts from kubeconfig.

```json
{
  "status": "success",
  "clusters": [
    { "name": "minikube", "is_current": true },
    { "name": "production", "is_current": false }
  ]
}
```

### `POST /investigate?context=<ctx>`
Run full investigation + AI diagnosis.

**Query param:** `context` (optional) — which cluster context to investigate

**Response:**
```json
{
  "status": "success",
  "context": "minikube",
  "investigation": {
    "healthy": false,
    "pods": {
      "total_pods": 12,
      "problematic_count": 2,
      "problematic_pods": [
        { "name": "payment-service-abc", "namespace": "default", "status": "CrashLoopBackOff", "restart_count": 5 }
      ]
    },
    "events": { "critical_count": 3, "critical_events": [...] },
    "deployments": { "unhealthy_count": 1, "unhealthy_deployments": [...] },
    "network": { "issue_count": 1, "issues": [...] },
    "logs": { "default/payment-service-abc": { "error_lines": [...] } }
  },
  "diagnosis": {
    "root_cause": "APPLICATION FAILED: DATABASE_URL environment variable is missing",
    "explanation": "The payment-service container starts and immediately crashes...",
    "fix": "Add the DATABASE_URL environment variable to the deployment...",
    "kubectl_commands": ["kubectl describe pod payment-service-abc -n default", "kubectl edit deployment payment-service -n default"],
    "prevention": "Use ConfigMap/Secret validation in your CI pipeline",
    "confidence": 92,
    "severity": "critical",
    "affected_resources": ["default/payment-service-abc"]
  }
}
```

---

## 📁 Project Structure

```
ai-kubernetes-agent/
├── backend/
│   ├── main.py                      # FastAPI app entry point
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   ├── api/
│   │   └── routes.py                # API endpoints
│   ├── core/
│   │   └── config.py                # Settings / env vars
│   ├── kubernetes/
│   │   ├── kubectl_executor.py      # Safe kubectl subprocess wrapper
│   │   ├── pod_inspector.py         # Detects unhealthy pods
│   │   ├── logs_collector.py        # Fetches/filters pod logs
│   │   ├── events_analyzer.py       # Surfaces critical events
│   │   ├── deployment_inspector.py  # Checks deployment health
│   │   └── network_inspector.py     # Detects network issues
│   └── services/
│       ├── investigation_service.py # Orchestrates all inspectors
│       └── ai_service.py            # OpenRouter LLM integration
├── frontend/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx                 # Main dashboard
│   │   └── globals.css
│   ├── components/
│   │   ├── Header.tsx
│   │   ├── ClusterSelector.tsx      # Kubeconfig cluster picker
│   │   ├── InvestigationPanel.tsx   # Progress steps UI
│   │   ├── DiagnosisCard.tsx        # AI diagnosis display
│   │   ├── EvidencePanel.tsx        # Raw K8s evidence tabs
│   │   └── QueryProvider.tsx
│   ├── hooks/
│   │   ├── useInvestigation.ts      # Investigation state/logic
│   │   └── useClusters.ts           # Cluster list fetching
│   ├── package.json
│   └── Dockerfile
├── k8s-test-scenarios/
│   ├── 01-crashloop.yaml
│   ├── 02-imagepull.yaml
│   ├── 03-oomkilled.yaml
│   ├── 04-selector-mismatch.yaml
│   └── apply-scenarios.sh
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, React Query |
| Backend | FastAPI, Python 3.12, Uvicorn, Pydantic |
| K8s Integration | kubectl via subprocess (no SDK) |
| AI Reasoning | OpenRouter API (Claude, GPT-4, etc.) |
| HTTP Client | HTTPX (async) |
| Logging | Loguru |
| Containerization | Docker + Docker Compose |

---

## 🎯 How AI Diagnosis Works

Without AI key (heuristic mode):
- Detects pod status (CrashLoopBackOff, ImagePullBackOff, OOMKilled)
- Applies pattern matching to generate diagnosis
- Still useful for common failures

With OpenRouter key (full AI mode):
- Sends structured investigation payload to LLM
- LLM correlates logs + events + deployment state
- Returns natural language root cause, fix, and prevention

### Supported Models (via OpenRouter)

Any model available on OpenRouter works. Recommended:
- `anthropic/claude-3-haiku` — Fast, cheap, great at structured output
- `anthropic/claude-3.5-sonnet` — More thorough analysis
- `openai/gpt-4o-mini` — Good alternative
- `google/gemini-flash-1.5` — Very fast

---

## 🐛 Troubleshooting

**Backend can't reach cluster:**
```bash
kubectl cluster-info
kubectl get pods -A
# Make sure kubectl works locally before running the agent
```

**Docker backend can't access kubeconfig:**
```bash
# Check that ~/.kube/config exists
ls ~/.kube/config

# Or set KUBECONFIG_PATH in .env
KUBECONFIG_PATH=/path/to/your/kubeconfig
```

**OpenRouter returns errors:**
```bash
# Test your API key
curl https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer YOUR_KEY"
```

**Frontend can't reach backend:**
```bash
# Check NEXT_PUBLIC_API_BASE_URL in frontend/.env.local
# Should match your backend port (default: 8000)
```

---

## 📋 Commands Reference

```bash
# Start backend dev server
cd backend && uvicorn main:app --reload --port 8000

# Start frontend dev server
cd frontend && npm run dev

# Start both via Docker
docker compose up --build

# Test investigation via curl
curl -X POST http://localhost:8000/investigate | jq

# Investigate specific cluster
curl -X POST "http://localhost:8000/investigate?context=minikube" | jq

# List clusters
curl http://localhost:8000/clusters | jq

# Health check
curl http://localhost:8000/health

# Apply test scenarios
cd k8s-test-scenarios && ./apply-scenarios.sh

# Watch pods
kubectl get pods -A -w

# Clean up test scenarios
cd k8s-test-scenarios && ./apply-scenarios.sh clean
```

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m 'Add my feature'`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

MIT — see [LICENSE](LICENSE) for details.

---

## ⭐ Star this repo if it helped you!

Built for learning, tutorials, and real-world Kubernetes debugging.
