# SCDIS - Smart Campus Decision Intelligence System

SCDIS is an AI-powered energy optimization and decision intelligence platform with:

- `backend`: FastAPI services for decisioning, monitoring, autonomous runtime, and model operations
- `frontend`: Next.js dashboard for live telemetry, AI decisions, events, alerts, and model controls

## Tech Stack

- Backend: FastAPI, Uvicorn, scikit-learn, pandas, numpy
- Frontend: Next.js 16, React 19, TypeScript, Tailwind, Framer Motion
- Deployment: Render (backend) + Vercel (frontend)

## Repository Structure

```text
.
+-- backend/                 # FastAPI app and AI runtime
|   +-- app.py               # FastAPI entrypoint
|   +-- routes/              # API routes
|   +-- services/            # Runtime/monitoring services
|   +-- ai_engine/           # Forecast/RL/anomaly/retraining logic
|   +-- requirements.txt     # Python dependencies
+-- frontend/                # Next.js dashboard
|   +-- app/                 # App router pages
|   +-- components/          # UI components/tabs
|   +-- lib/api.ts           # Frontend API client
+-- render.yaml              # Render deployment blueprint
```

## Features

- Live laptop/edge telemetry monitoring
- Runtime modes: `LIVE_EDGE`, `SIMULATION`, `HYBRID`
- Scenario injection: `normal`, `peak_load`, `low_load`, `grid_failure`
- AI decision timeline and optimization insights
- AI model actions:
  - Retrain model
  - View logs
  - Export weights
- Autonomous background runtime services

## Local Development

## Prerequisites

- Python `3.11+`
- Node.js `18+` (recommended `20+`)

## 1) Backend Setup

```bash
cd backend
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies and run:

```bash
pip install -r requirements.txt
python -m uvicorn app:app --host 0.0.0.0 --port 8010
```

Backend health:

```bash
curl http://localhost:8010/
curl http://localhost:8010/openapi.json
```

## 2) Frontend Setup

In a new terminal:

```bash
cd frontend
npm install
```

Set API base URL in `frontend/.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8010
```

Run frontend:

```bash
npm run dev
```

Open:

- Dashboard: `http://localhost:3000`

## API Docs

- Swagger UI: `http://localhost:8010/docs`
- OpenAPI JSON: `http://localhost:8010/openapi.json`

## Deployment

## Backend on Render

This repo includes `render.yaml` and `backend/requirements.txt`.

1. Push code to GitHub
2. In Render: `New` -> `Blueprint`
3. Select this repository
4. Render auto-creates `scdis-backend` using `render.yaml`
5. After deploy, copy backend URL

## Backend on Oracle Always Free VM (Alternative)

Use this detailed guide:

- `docs/deploy-oracle-vercel.md`

Quick path:

1. Create Oracle Always Free VM
2. Open ingress ports `22`, `80`, `443`
3. Clone repo on VM to `/opt/scdis`
4. Run:

```bash
bash backend/deploy/oracle_vm_setup.sh /opt/scdis ubuntu
```

(Use `opc` as the second argument on Oracle Linux images.)

>>>>>>> d98ef0c (Add Oracle VM + Vercel deployment setup)
## Frontend on Vercel

1. In Vercel: `New Project`
2. Import this repository
3. Set **Root Directory** to `frontend`
4. Add environment variable:

```env
NEXT_PUBLIC_API_BASE_URL=https://<your-render-backend-url>
```

5. Deploy

## Post-Deploy Checks

Replace `<backend-url>` and run:

```bash
curl https://<backend-url>/
curl https://<backend-url>/monitoring/laptop/live-dashboard
curl https://<backend-url>/monitoring/ai-models/retrain -X POST
```

## Troubleshooting

- `API 404 {"detail":"Not Found"}` in UI:
  - Frontend is pointing to the wrong backend URL
  - Verify `NEXT_PUBLIC_API_BASE_URL`
  - Confirm route exists in `https://<backend>/openapi.json`
- Frontend changes not reflecting:
  - restart dev server after env changes
- Render cold start delay:
  - first request can take longer on free tier

## Notes

- Some runtime features depend on host machine telemetry and local model/data files.
- For production-grade persistence, use external storage for logs/artifacts (DB/S3/object storage), because ephemeral disk can reset on redeploy.
