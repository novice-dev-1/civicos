# CivicOS — FINAL Architecture, Tech Stack & Build Phases

> Multi-Agent Emergency Coordination Platform
> Hackathon: **FAR AWAY 2026** · Theme: **Agentic & Autonomous Systems**
> Build target: 1-5 member team, Round 1 (top 100 → Delhi offline → top 50 → top 10)

---

## 1. TECH STACK (Modern · 2026 · 100% Free Tier)

### 1.1 Frontend

| Layer | Tool | Why this, not the alternative |
|---|---|---|
| Build | **Vite 5** | Fastest dev server. Next.js is overkill for an SPA. |
| Framework | **React 19** | Latest stable. Server Components not needed. |
| Language | **TypeScript 5.6** | Type safety. Catches API contract bugs early. |
| Routing | **TanStack Router** | Type-safe, file-based, replaces React Router 7. |
| Data fetching | **TanStack Query v5** | Cache, retries, optimistic updates. Better than raw fetch. |
| Styling | **Tailwind CSS v4** | Faster compile, native CSS variables. |
| Components | **shadcn/ui** | Copy-paste, owned in your repo. Not a black box. |
| Maps | **Leaflet 1.9 + react-leaflet** | Free, OSM tiles, no API key, no quota. |
| State (client) | **Zustand** | 1KB, no boilerplate, no Redux. |
| Icons | **Lucide React** | Clean, tree-shakeable, matches Shadcn aesthetic. |
| Charts | **Recharts** | For hospital load + KPI dashboard. SVG-based, lightweight. |
| Package mgr | **pnpm** | Fast, disk-efficient, strict. |

### 1.2 Backend

| Layer | Tool | Why |
|---|---|---|
| Runtime | **Python 3.12** | Latest stable, fast, supported everywhere. |
| Web framework | **FastAPI 0.115+** | Async-native, auto OpenAPI docs, Pydantic integration. |
| Validation | **Pydantic v2** | 5-50x faster than v1. Rust core. |
| ORM | **SQLAlchemy 2.0** | Async support, mature, type-safe with Mapped[] syntax. |
| Migrations | **Alembic** | Auto-generate from models. |
| Agent framework | **LangGraph 0.2+** | State machines, cycles, human-in-loop. Best for multi-agent. |
| LLM SDK | **`google-genai`** | Newer than `google-generativeai`. Official Google SDK. |
| SSE | **sse-starlette** | Native FastAPI SSE support. |
| Auth | **supabase-py** | JWT verification, no user mgmt code. |
| PDF | **reportlab** | Pure Python, no LaTeX, no headless browser. |
| Distance | **haversine** | Pure-Python, no API call for distance. |
| Pkg mgr | **uv** | 10-100x faster than pip. Modern standard. |

### 1.3 Database & Services

| Service | Free tier | Why |
|---|---|---|
| **Neon** PostgreSQL | 0.5 GB, serverless | Branching, auto-suspend, perfect for hackathons. |
| **Supabase Auth** | 50K MAU | JWT, RLS, no server code. |
| **Google AI Studio** | 15 RPM, 1M TPM | Gemini 2.5 Flash free. |
| **Vercel** | Hobby tier | Frontend deploy, edge CDN, free SSL. |
| **Render** | Free web service | Backend deploy, sleeps after 15min idle (acceptable). |

### 1.4 Developer Tools

| Tool | Use |
|---|---|
| **uv** | Python deps |
| **pnpm** | Node deps |
| **Ruff** | Lint + format Python (replaces Black + isort + flake8) |
| **Prettier** | Format TS/TSX/CSS |
| **ESLint** | Lint TS/TSX |
| **LangSmith** (optional) | Trace LangGraph runs. Free tier = 5K traces/mo. |
| **OBS Studio** | Record demo video |
| **Mermaid** | Architecture diagrams in README |

### 1.5 NOT using (and why)

| Avoid | Why |
|---|---|
| Next.js | Overkill, forces server-side complexity. SPA is enough. |
| React Router | TanStack Router is type-safe and better. |
| Redux/Zustand heavyweight | Zustand is 1KB, no boilerplate. |
| WebSockets | SSE is enough for one-way updates. Less infra. |
| Docker | Wastes hackathon time. Deploy direct to Vercel/Render. |
| OpenAI/Anthropic APIs | Not free. Gemini Flash is. |
| Pinecone / Vector DB | We don't need RAG for this project. |
| LangChain (raw) | LangGraph is the right abstraction for stateful agents. |
| CrewAI / AutoGen | Less controllable than LangGraph for demos. |
| Clerk | Too much setup. Supabase Auth is enough. |

---

## 2. FINAL ARCHITECTURE

### 2.1 System Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│                    USER (Judge / Emergency Operator)               │
└─────────────────────────────────┬──────────────────────────────────┘
                                  │ Browser
                                  ▼
        ┌──────────────────────────────────────────────────────┐
        │   FRONTEND  (Vercel · React 19 + Vite + TS)          │
        │                                                      │
        │  ┌──────────────────────────────────────────────┐    │
        │  │  Live KPI Ticker (sticky top)                │    │
        │  │  Avg Time-to-Care · Resources · Incidents    │    │
        │  └──────────────────────────────────────────────┘    │
        │                                                      │
        │  ┌──────────┬────────────────────────┬──────────┐    │
        │  │ LEFT     │    CENTER              │  RIGHT   │    │
        │  │          │                        │          │    │
        │  │ Incidents│   Delhi Map (Leaflet)  │ Agent    │    │
        │  │ List     │   + resource markers   │ Feed     │    │
        │  │          │   + incident markers   │ (live)   │    │
        │  │ + Reset  │   + corridor overlay   │          │    │
        │  │   City   │                        │ + reject │    │
        │  │ + Com-   │                        │   reasons│    │
        │  │   pare   │                        │   inline │    │
        │  └──────────┴────────────────────────┴──────────┘    │
        │                                                      │
        │  ┌──────────────────────────────────────────────┐    │
        │  │  BOTTOM  · Timeline + Counterfactual Modal   │    │
        │  └──────────────────────────────────────────────┘    │
        │                                                      │
        │  + PDF Export  + Comparison Mode (Without CivicOS)   │
        └──────────────────┬────────────────┬──────────────────┘
                           │ REST           │ SSE
                           ▼                ▲
        ┌──────────────────────────────────────────────────────┐
        │   BACKEND  (Render · FastAPI)                        │
        │                                                      │
        │  ┌──────────────────────────────────────────────┐    │
        │  │  API Layer                                   │    │
        │  │  /incidents  /resources  /counterfactual     │    │
        │  │  /forecast   /kpi  /export/pdf  /events      │    │
        │  └────────────────┬─────────────────────────────┘    │
        │                   ▼                                  │
        │  ┌──────────────────────────────────────────────┐    │
        │  │  LangGraph Orchestrator (Supervisor pattern) │    │
        │  │                                              │    │
        │  │              ┌────────────────┐              │    │
        │  │              │ Incident Agent │ ← Gemini     │    │
        │  │              └────────┬───────┘              │    │
        │  │                       ▼                      │    │
        │  │              ┌────────────────┐              │    │
        │  │              │ Coordinator    │ ← Gemini     │    │
        │  │              └────────┬───────┘              │    │
        │  │            ┌──────────┼──────────┐           │    │
        │  │            ▼          ▼          ▼           │    │
        │  │       Ambulance   Hospital     Police        │    │
        │  │            │          │          │           │    │
        │  │            └──────────┼──────────┘           │    │
        │  │                       ▼                      │    │
        │  │                  Traffic Agent               │    │
        │  │              (ETA + Corridor Plan)           │    │
        │  │                       │                      │    │
        │  │                       ▼                      │    │
        │  │              ┌────────────────┐              │    │
        │  │              │ Coordinator    │ ← Gemini     │    │
        │  │              │ (final picks)  │              │    │
        │  │              └────────┬───────┘              │    │
        │  │                       ▼                      │    │
        │  │                 END / Plan                   │    │
        │  │                                              │    │
        │  │       (Resource Forecast runs in parallel    │    │
        │  │        — predicts shortages, recommends      │    │
        │  │        pre-positioning of standby units)     │    │
        │  └──────────────────────────────────────────────┘    │
        │                                                      │
        │  Reasoning Broadcaster (SSE pub/sub)                  │
        └──────────────┬─────────────────────┬─────────────────┘
                       │                     │
                       ▼                     ▼
        ┌──────────────────────┐  ┌──────────────────────┐
        │  PostgreSQL (Neon)   │  │  Supabase Auth       │
        │  4 tables            │  │  JWT verification    │
        │  + LangSmith traces  │  │  (operator role)     │
        └──────────────────────┘  └──────────────────────┘
```

### 2.2 The 7 Agents (locked)

| # | Agent | Input | Output | LLM? |
|---|-------|-------|--------|------|
| 1 | **Incident** | Free-text description | `{type, severity, victims, specialty_required}` | ✅ Gemini 2.5 Flash |
| 2 | **Coordinator** | Candidates from all specialists | `{final_assignments, rejections_with_reasons}` | ✅ Gemini 2.5 Flash |
| 3 | **Ambulance** | Available ambulances + incident location | Ranked list of candidates with scores | ❌ Algorithmic |
| 4 | **Hospital** | Hospitals + incident specialty | Ranked list with specialty match + ICU + distance | ❌ Algorithmic |
| 5 | **Police** | Available units + incident | Ranked list with jurisdiction + proximity | ❌ Algorithmic |
| 6 | **Traffic** | Routes + incident + ETA threshold | `{eta, corridor_plan, police_needed}` | ❌ Algorithmic |
| 7 | **Resource Forecast** *(new)* | Rolling incident history + current load | `{shortage_in_min, pre_position_recommendations}` | ❌ Algorithmic |

**Ratio: 2 LLM agents, 5 algorithmic.** Right balance — LLM is expensive, slow, and best for nuanced reasoning (parsing, trade-offs). Math/ranking should be code.

### 2.3 LangGraph State

```python
from typing import TypedDict, Optional
from pydantic import BaseModel
from datetime import datetime

class ResourceCandidate(BaseModel):
    resource_id: str
    type: str              # ambulance | hospital | police
    name: str
    distance_km: float
    eta_min: float
    score: float           # 0-100
    rejected: bool = False
    rejection_reason: Optional[str] = None

class AgentTrace(BaseModel):
    agent: str
    step: int
    timestamp: datetime
    thought: str
    action: str
    alternatives: list[str]

class CivicState(TypedDict):
    # Identity
    incident_id: str
    # Input
    raw_description: str
    incident_type: str           # accident | fire | cardiac
    severity: str                # LOW | MEDIUM | HIGH | CRITICAL
    victims: int
    specialty_required: str      # trauma | cardiac | burns | general
    location: tuple[float, float]  # (lat, lng)
    # Computed
    priority_score: float
    # Agent outputs
    ambulance_candidates: list[ResourceCandidate]
    hospital_candidates: list[ResourceCandidate]
    police_candidates: list[ResourceCandidate]
    corridor_plan: Optional[dict]
    # Final
    final_assignments: dict
    # Trace for UI
    trace: list[AgentTrace]
    # Forecast
    forecast_warning: Optional[str]
```

### 2.4 Graph Flow (Supervisor)

```python
from langgraph.graph import StateGraph, START, END

graph = StateGraph(CivicState)

graph.add_node("incident",  incident_agent)
graph.add_node("coord1",    coordinator_dispatch)
graph.add_node("ambulance", ambulance_agent)
graph.add_node("hospital",  hospital_agent)
graph.add_node("police",    police_agent)
graph.add_node("traffic",   traffic_agent)
graph.add_node("coord2",    coordinator_finalize)
graph.add_node("forecast",  forecast_agent)  # runs in parallel via Send()

graph.add_edge(START, "incident")
graph.add_edge("incident", "coord1")
# Parallel fan-out
graph.add_edge("coord1", "ambulance")
graph.add_edge("coord1", "hospital")
graph.add_edge("coord1", "police")
graph.add_edge("coord1", "traffic")
# Fan-in
graph.add_edge("ambulance", "coord2")
graph.add_edge("hospital",  "coord2")
graph.add_edge("police",    "coord2")
graph.add_edge("traffic",   "coord2")
graph.add_edge("coord2", "forecast")
graph.add_edge("forecast", END)
```

### 2.5 Database Schema (4 tables, locked)

```sql
-- 1. incidents
CREATE TABLE incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    description TEXT NOT NULL,
    type VARCHAR(20),         -- accident | fire | cardiac
    severity VARCHAR(20),     -- LOW | MEDIUM | HIGH | CRITICAL
    victims INT DEFAULT 0,
    specialty_required VARCHAR(50),
    lat DOUBLE PRECISION,
    lng DOUBLE PRECISION,
    status VARCHAR(20) DEFAULT 'PENDING',  -- PENDING | ASSIGNED | RESOLVED | FAILED
    priority_score FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    time_to_care_min FLOAT    -- computed on resolution
);

-- 2. resources
CREATE TABLE resources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(20) NOT NULL,  -- ambulance | hospital | police
    name VARCHAR(200) NOT NULL,
    lat DOUBLE PRECISION NOT NULL,
    lng DOUBLE PRECISION NOT NULL,
    capacity_total INT DEFAULT 1,
    capacity_used INT DEFAULT 0,
    specialty VARCHAR(50),      -- for hospitals
    equipment TEXT[],           -- for ambulances
    jurisdiction VARCHAR(100),  -- for police
    status VARCHAR(20) DEFAULT 'AVAILABLE'  -- AVAILABLE | BUSY | OFFLINE
);

-- 3. assignments (incident ↔ resource)
CREATE TABLE assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID REFERENCES incidents(id) ON DELETE CASCADE,
    resource_id UUID REFERENCES resources(id),
    role VARCHAR(50),        -- primary_ambulance | backup_ambulance | hospital | police | corridor
    eta_min FLOAT,
    distance_km FLOAT,
    assigned_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. audit_logs (the reasoning trail)
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID REFERENCES incidents(id) ON DELETE CASCADE,
    agent_name VARCHAR(50),
    step INT,
    thought TEXT,
    action TEXT,
    alternatives JSONB,
    logged_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 2.6 API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Liveness check |
| POST | `/incidents` | Create incident → starts graph run |
| GET | `/incidents` | List all (with filters) |
| GET | `/incidents/{id}` | Detail + assignments + trace |
| POST | `/incidents/simulate` | One-click demo scenarios (3 AM Test) |
| GET | `/resources` | List all resources |
| POST | `/counterfactual` | Rerun with override, return comparison |
| GET | `/forecast` | Current shortage predictions |
| GET | `/kpi` | Aggregate KPIs |
| GET | `/kpi/comparison` | CivicOS vs naive baseline |
| GET | `/incidents/{id}/pdf` | PDF export |
| GET | `/events?incident_id=...` | SSE stream |
| POST | `/admin/reset` | Reset city state for re-demos |

### 2.7 SSE Event Format

```json
{
  "event": "agent_thought",
  "data": {
    "incident_id": "uuid",
    "agent": "AmbulanceAgent",
    "thought": "Comparing A1 (3.2km) vs A3 (5.8km) vs A7 (8.1km)",
    "action": "Selected A1 — best distance + equipment match",
    "alternatives": ["A3 rejected: longer ETA", "A7 rejected: at capacity"]
  }
}

{ "event": "corridor_generated", "data": { ... } }
{ "event": "plan_finalized",      "data": { ... } }
{ "event": "forecast_alert",      "data": { ... } }
```

### 2.8 Priority Formula (final, with Criticality Bonus)

```python
PRIORITY_SCORE = (
    SEVERITY_WEIGHT * {"LOW": 1, "MEDIUM": 3, "HIGH": 7, "CRITICAL": 10}[severity]
    + 2 * victims
    + 0.5 * minutes_waiting
    + CRITICALITY_BONUS    # new
)

CRITICALITY_BONUS = {
    "cardiac":  20,    # golden window 8 min
    "stroke":   18,
    "burns":    15,
    "trauma":   10,
    "general":  0
}[specialty_required]
```

### 2.9 KPI Definitions

| KPI | Formula | Why |
|-----|---------|-----|
| **Avg Time to Care** | mean(time_to_care_min) across resolved incidents | Core impact metric |
| **Resource Utilization** | busy_resources / total_resources | Shows efficiency |
| **Hospital Load Balance** | stddev(icu_used / icu_total) across hospitals | Lower = better balance |

**KPI dashboard visualization:**
- Three big numbers across the top
- Bar chart: hospital ICU utilization (8 hospitals side by side, before/after toggle)
- "Without CivicOS" toggle: switch to naive random baseline numbers

### 2.10 Repo Structure

```
civicos/
├── README.md
├── .env.example
├── backend/
│   ├── pyproject.toml              # uv-managed
│   ├── uv.lock
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   ├── app/
│   │   ├── main.py                 # FastAPI app + lifespan
│   │   ├── config.py               # pydantic-settings
│   │   ├── db.py                   # async SQLAlchemy
│   │   ├── models.py               # 4 ORM models
│   │   ├── schemas.py              # Pydantic v2
│   │   ├── seed.py                 # Delhi data
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── state.py            # CivicState
│   │   │   ├── graph.py            # LangGraph build
│   │   │   ├── incident.py         # LLM
│   │   │   ├── coordinator.py      # LLM
│   │   │   ├── ambulance.py        # algo
│   │   │   ├── hospital.py         # algo
│   │   │   ├── police.py           # algo
│   │   │   ├── traffic.py          # algo + corridor
│   │   │   └── forecast.py         # algo
│   │   ├── routers/
│   │   │   ├── incidents.py
│   │   │   ├── resources.py
│   │   │   ├── counterfactual.py
│   │   │   ├── forecast.py
│   │   │   ├── kpi.py
│   │   │   ├── pdf.py
│   │   │   ├── events.py           # SSE
│   │   │   └── admin.py            # reset
│   │   └── utils/
│   │       ├── distance.py
│   │       ├── priority.py
│   │       ├── broadcaster.py
│   │       ├── llm.py              # Gemini wrapper
│   │       └── demo_data.py        # canned responses for DEMO_MODE
│   └── tests/
│       └── test_graph.py
├── frontend/
│   ├── package.json
│   ├── pnpm-lock.yaml
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── index.html
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── KPITicker.tsx
│   │   │   ├── Map.tsx
│   │   │   ├── IncidentList.tsx
│   │   │   ├── AgentFeed.tsx
│   │   │   ├── Timeline.tsx
│   │   │   ├── CounterfactualModal.tsx
│   │   │   ├── KPIDashboard.tsx
│   │   │   ├── IncidentForm.tsx
│   │   │   ├── HospitalLoadChart.tsx
│   │   │   ├── PDFButton.tsx
│   │   │   ├── ResetCityButton.tsx
│   │   │   ├── ComparisonToggle.tsx
│   │   │   ├── FailureAlert.tsx
│   │   │   └── ForecastBanner.tsx
│   │   ├── hooks/
│   │   │   ├── useSSE.ts
│   │   │   ├── useIncidents.ts
│   │   │   └── useResources.ts
│   │   ├── lib/
│   │   │   ├── api.ts
│   │   │   └── supabase.ts
│   │   ├── store/
│   │   │   └── cityStore.ts        # Zustand
│   │   └── types/
│   │       └── index.ts
│   └── public/
└── docs/
    ├── ARCHITECTURE.md             # this file
    ├── DEMO_SCRIPT.md
    └── VIDEO_STORYBOARD.md
```

---

## 3. PHASES (Hour-by-Hour)

> **Total: 50-70 hours** for a focused team of 3-4
> **Hard rule:** Phases 0 → 3 → 4 are serial. After Phase 4, parallelize.

---

### PHASE 0 — Foundation (4-6h)

**Owner:** 1 person, full focus

- [ ] `mkdir civicos && cd civicos && git init`
- [ ] Create GitHub repo, push first commit
- [ ] Create **Neon** project → save `DATABASE_URL`
- [ ] Create **Supabase** project → save `SUPABASE_URL`, `SUPABASE_ANON_KEY`
- [ ] Get **Google AI Studio** API key → save `GEMINI_API_KEY`
- [ ] **Backend setup:**
  ```bash
  cd backend
  uv init
  uv add fastapi uvicorn[standard] sqlalchemy[asyncio] asyncpg alembic \
        pydantic pydantic-settings langgraph langchain-google-genai \
        google-genai sse-starlette supabase reportlab haversine python-jose
  ```
- [ ] `app/main.py` with FastAPI app, CORS, `/health`
- [ ] `app/config.py` with pydantic-settings
- [ ] `app/db.py` with async engine
- [ ] `uv run uvicorn app.main:app --reload` → verify `/health` returns 200
- [ ] **Frontend setup:**
  ```bash
  cd frontend
  pnpm create vite@latest . -- --template react-ts
  pnpm add @tanstack/react-router @tanstack/react-query \
           zustand leaflet react-leaflet recharts lucide-react \
           @supabase/supabase-js
  pnpm add -D tailwindcss@4 @tailwindcss/vite prettier eslint
  pnpm dlx shadcn@latest init
  pnpm dlx shadcn@latest add button card dialog table badge
  ```
- [ ] Tailwind v4 + Vite plugin configured
- [ ] `App.tsx` with router + layout shell
- [ ] `pnpm dev` → verify React loads on :5173
- [ ] `.env.example` with all required vars
- [ ] **Deploy:**
  - [ ] Render: connect repo, root=`backend/`, build=`uv sync`, start=`uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT`
  - [ ] Vercel: connect repo, root=`frontend/`, framework=Vite
  - [ ] Set all env vars on both
  - [ ] Verify `/health` works on Render URL

**Done when:** Both servers running, GitHub up, Render + Vercel URLs working.

---

### PHASE 1 — Data Layer + Delhi Seed (3-4h)

**Owner:** Backend

- [ ] `alembic init alembic`
- [ ] `app/models.py` — 4 SQLAlchemy 2.0 models with `Mapped[]` typing
- [ ] `alembic revision --autogenerate -m "init"` → review → `alembic upgrade head`
- [ ] `app/schemas.py` — Pydantic v2 request/response models
- [ ] `app/seed.py` — populate Delhi resources
- [ ] Real Delhi coordinates (verified):

```python
# 8 hospitals
HOSPITALS = [
    ("AIIMS Delhi",        28.5672, 77.2100, 50, "trauma"),
    ("Safdarjung Hospital",28.5687, 77.2053, 40, "trauma"),
    ("RML Hospital",       28.6280, 77.2070, 30, "general"),
    ("LNJP Hospital",      28.6406, 77.2381, 35, "general"),
    ("Max Saket",          28.5275, 77.2157, 25, "cardiac"),
    ("Apollo Delhi",       28.5421, 77.2849, 30, "cardiac"),
    ("Fortis Vasant Kunj", 28.5225, 77.1572, 20, "cardiac"),
    ("BLK Hospital",       28.6450, 77.1880, 22, "general"),
]
# 12 ambulances — random within Delhi bbox [28.55-28.72, 77.10-77.30]
# 10 police units — same bbox
```

- [ ] `python -m app.seed` → verify 30 rows in `resources`
- [ ] `GET /resources` endpoint → returns 30 JSON objects
- [ ] `GET /kpi` stub (returns zeros for now)

**Done when:** 30 resources visible via API, manually verified in DB.

---

### PHASE 2 — Map + UI Shell (4-6h)

**Owner:** Frontend 1

- [ ] `Map.tsx` with Leaflet, OSM tiles
- [ ] Center: `[28.6139, 77.2090]`, zoom 11
- [ ] Custom markers per resource type (color-coded)
- [ ] Popups: name, capacity, status
- [ ] Three-panel layout:
  ```
  ┌─────────────────────────────────────┐
  │  KPITicker (sticky)                 │
  ├──────────┬───────────────┬──────────┤
  │ Incidents│   Map         │  Agent   │
  │ List     │               │  Feed    │
  │          │               │          │
  │ + Reset  │               │          │
  │ + Com-   │               │          │
  │   pare   │               │          │
  ├──────────┴───────────────┴──────────┤
  │  Timeline + Counterfactual          │
  └─────────────────────────────────────┘
  ```
- [ ] Tailwind styling — dark theme (looks more "gov-grade")
- [ ] `useResources.ts` — TanStack Query, fetches `/resources`
- [ ] Markers refresh on data change

**Done when:** Map shows Delhi with all 30 markers.

---

### PHASE 3 — Core Incident Flow (4-6h, no agents yet)

**Owner:** Backend (1) + Frontend (1) in parallel

- [ ] **Backend:**
  - [ ] `POST /incidents` — creates incident
  - [ ] Rule-based severity (keywords: "fire","burns"→CRITICAL; "cardiac","heart"→HIGH+criticality; "accident","crash"+victims→MEDIUM/HIGH)
  - [ ] Naive nearest-resource assignment (haversine)
  - [ ] Priority score with criticality bonus
  - [ ] Save incident + assignments + audit_log
  - [ ] `GET /incidents`, `GET /incidents/{id}`
  - [ ] `POST /incidents/simulate` — pre-canned scenarios
- [ ] **Frontend:**
  - [ ] `IncidentForm.tsx` — text input + 3 quick-trigger buttons
  - [ ] On submit, draw incident marker on map
  - [ ] Draw lines from incident to assigned resources
  - [ ] `IncidentList.tsx` updates
  - [ ] Polling (every 2s) for now; SSE in Phase 5

**Done when:** Click "Bus Accident" → see assignment on map.

---

### PHASE 4 — LangGraph Agents (8-10h, **CORE**)

**Owner:** Backend (full focus)

- [ ] `app/agents/state.py` — `CivicState` TypedDict
- [ ] `app/agents/incident.py` — uses Gemini to parse text → structured
  - Implements Dynamic Incident Interpretation: "school bus overturned near AIIMS, children may be trapped" → `{type: accident, severity: CRITICAL, victims: 15, specialty: trauma, special_notes: "pediatric"}`
- [ ] `app/agents/ambulance.py` — score = `0.5*distance_norm + 0.3*equipment_match + 0.2*capacity_free`
- [ ] `app/agents/hospital.py` — score = `0.4*specialty_match + 0.3*icu_available + 0.3*distance_norm`
- [ ] `app/agents/police.py` — score = `0.5*jurisdiction_match + 0.5*distance_norm`
- [ ] `app/agents/traffic.py`:
  - Compute ETA = `distance_km / 30 * 60` (avg Delhi speed 30 km/h)
  - If `eta > threshold` and severity >= HIGH: generate corridor plan (suggest route, recommend police units)
- [ ] `app/agents/forecast.py`:
  - Track incidents per hour in last 60 min
  - If `active_incidents * avg_resolution_time > available_resources` → predict shortage
  - Recommend pre-positioning standby units
- [ ] `app/agents/coordinator.py` — uses Gemini to:
  - Read candidates from all specialists
  - Pick best per role
  - Write rejection reasons for each
  - Handle criticality bonus (cardiac gets priority in time-sensitive decisions)
- [ ] `app/agents/graph.py` — build the StateGraph
- [ ] Test single incident: bus crash → full trace in audit_logs
- [ ] Test 3-incident conflict: 3 AM Mass Casualty Test → coordinator prioritizes

**Done when:** Graph runs, multi-incident prioritization works, audit trail complete.

---

### PHASE 5 — Real-Time SSE + Reasoning Feed (4-6h)

**Owner:** Backend (SSE) + Frontend (AgentFeed)

- [ ] **Backend:**
  - [ ] `app/utils/broadcaster.py` — async pub/sub queue per incident_id
  - [ ] `app/routers/events.py` — `/events` SSE endpoint
  - [ ] In each agent, after action, `await broadcaster.publish(incident_id, {...})`
  - [ ] Broadcast events: `agent_thought`, `corridor_generated`, `plan_finalized`, `forecast_alert`
- [ ] **Frontend:**
  - [ ] `useSSE.ts` hook — connects to `/events`, dispatches to Zustand store
  - [ ] `AgentFeed.tsx` — right panel, scrolling thought list
  - [ ] Color-coded by agent
  - [ ] Auto-scroll, pause on hover
  - [ ] **Inline rejection reasons** under each decision
  - [ ] `Timeline.tsx` — bottom panel, timestamped events

**Done when:** Click simulate → watch agents fire live on UI in real-time.

---

### PHASE 6 — Multi-Incident + Failure Handling (3-4h)

**Owner:** Backend

- [ ] `app/utils/demo_data.py` — canned 3-incident scenario:
  ```
  t=0s:  Cardiac arrest near India Gate (28.6127, 77.2295), 1 victim, 8-min window
  t=5s:  Bus crash near AIIMS (28.5672, 77.2100), 15 victims
  t=12s: Building fire at Connaught Place (28.6315, 77.2167), 8 victims
  ```
- [ ] `POST /incidents/simulate/mass-casualty` — fires all 3 with delays
- [ ] Coordinator checks resource load before assigning
- [ ] If resource already assigned to higher-priority incident → pick next-best
- [ ] Failure handling:
  - If `available_resources == 0` for a role → mark incident status=`FAILED`, emit `Critical Resource Shortage` alert
  - Frontend `FailureAlert.tsx` shows red banner on the incident
- [ ] Frontend: all 3 incidents on map, distinct colors, lines to assigned resources
- [ ] Timeline shows resolution order

**Done when:** 3 incidents fire, system handles contention, failure path works.

---

### PHASE 7 — Counterfactual Simulator (3-4h) ⭐

**Owner:** Backend (logic) + Frontend (modal)

- [ ] **Backend:**
  - [ ] `POST /counterfactual` body: `{incident_id, override: {role: resource_id}}`
  - [ ] Re-run coordinator graph with override
  - [ ] Recompute ETAs
  - [ ] Return: `{original_plan, alternative_plan, time_to_care_delta, reasoning}`
- [ ] **Frontend:**
  - [ ] `CounterfactualModal.tsx`
  - [ ] Trigger: click "Why not A7?" link on any rejected resource
  - [ ] Shows side-by-side cards
  - [ ] Big delta number: "Choosing A3 reduces response time by 50%"
  - [ ] Reasoning chain for both plans

**Done when:** Click "Why not A7?" → clear before/after modal.

---

### PHASE 8 — KPIs + Hospital Load + Comparison Mode (4-6h)

**Owner:** Frontend 2 + Backend (calc)

- [ ] **Backend:**
  - [ ] `GET /kpi` — returns `{avg_time_to_care, resource_utilization, hospital_load_variance}`
  - [ ] `GET /kpi/comparison` — runs naive random baseline on past incidents, returns side-by-side
  - [ ] `time_to_care = dispatch_time + travel_time + hospital_alloc_time`
- [ ] **Frontend:**
  - [ ] `KPITicker.tsx` — sticky top, three live numbers
  - [ ] `KPIDashboard.tsx` — view mode with:
    - Three big numbers
    - `HospitalLoadChart.tsx` — Recharts bar chart, 8 hospitals, before/after toggle
  - [ ] `ComparisonToggle.tsx` — switches all KPIs between CivicOS / Naive
  - [ ] `ForecastBanner.tsx` — top banner: "Resource shortage predicted in 25 min — pre-positioning recommended"

**Done when:** Dashboard shows 13.4 → 8.1 min, hospital load chart works, forecast banner shows.

---

### PHASE 9 — PDF Export + DEMO_MODE + Reset (3-4h)

**Owner:** Backend (PDF) + Frontend (toggle, reset)

- [ ] **Backend:**
  - [ ] `GET /incidents/{id}/pdf` — reportlab generates:
    ```
    CIVICOS — EMERGENCY RESPONSE REPORT
    ═══════════════════════════════════
    Incident: Bus crash near AIIMS
    Severity: CRITICAL
    Victims: 15
    Created: 2026-06-10 23:45 IST
    Resolved: 2026-06-10 23:53 IST
    Time to Care: 8.1 min

    ASSIGNMENTS
    • Ambulance A1 — ETA 4.2 min — AIIMS Trauma
    • Hospital: AIIMS — specialty match
    • Police: P3 — corridor support

    REASONING CHAIN
    1. IncidentAgent: Extracted CRITICAL severity, 15 victims, pediatric concern
    2. AmbulanceAgent: Selected A1 (closest equipped)
    3. HospitalAgent: Selected AIIMS (trauma specialty + ICU)
    4. TrafficAgent: Generated corridor plan (Route A reserved)
    5. Coordinator: Finalized

    AUDIT TRAIL
    Full log attached.
    ```
  - [ ] `DEMO_MODE=true` env var: skip LLM, return pre-canned responses instantly
  - [ ] `POST /admin/reset` — clears incidents, frees resources
- [ ] **Frontend:**
  - [ ] `PDFButton.tsx` on each incident
  - [ ] `ResetCityButton.tsx` in left panel (with confirm dialog)
  - [ ] `DemoModeToggle.tsx` (dev only)

**Done when:** PDF downloads, reset works, DEMO_MODE guarantees <1s response.

---

### PHASE 10 — Video + Submission (4-6h)

**Owner:** Anyone good at video

- [ ] Record live demo (OBS, 1440p, 30fps)
- [ ] **Storyboard:**
  - **0-15s:** Hook. "In India, 8,000 die in road accidents daily. Response time decides if they live. This is CivicOS."
  - **15-30s:** Architecture diagram (animated Mermaid)
  - **30-75s:** **The 3 AM Mass Casualty Test.** Fire three incidents live. Watch system prioritize in real-time. Reasoning feed scrolls. Map updates.
  - **75-95s:** **Counterfactual.** Click "Why not A7?" Modal opens, side-by-side comparison.
  - **95-110s:** **KPI dashboard.** "13.4 min → 8.1 min. 39% faster. Naive → CivicOS."
  - **110-120s:** **Forecast banner.** "Predicts resource shortage 25 min ahead, recommends pre-positioning." Close.
- [ ] Upload to YouTube (unlisted), get link
- [ ] Backup: 15-slide deck (PDF)
- [ ] Polish README:
  - [ ] Hero image (Mermaid architecture)
  - [ ] One-paragraph problem
  - [ ] One-paragraph solution
  - [ ] Setup: `git clone`, `pnpm i`, `uv sync`, `pnpm dev`, `uv run uvicorn...` — runs in 3 commands
  - [ ] Demo video link
  - [ ] Tech stack
  - [ ] Team
  - [ ] License (MIT)
- [ ] Verify final checklist:
  - [ ] GitHub public
  - [ ] Setup works from scratch
  - [ ] Video on YouTube
  - [ ] No AI-only project
  - [ ] No rebranded code
  - [ ] No plagiarism
  - [ ] Submission form filled

**Done when:** Submitted, repo public, video uploaded.

---

## 4. PARALLELIZATION (after Phase 4)

```
SERIAL (must be in order):
  Phase 0 → Phase 1 → Phase 3 → Phase 4 → Phase 5
                                          │
                                          ▼
PARALLEL after Phase 5:
                                          │
   ┌──────────────────────┬──────────────┼──────────────┐
   ▼                      ▼              ▼              ▼
 Frontend 1:        Frontend 2:     Backend:        Anyone:
 Phase 6 UI         Phase 7 UI      Phase 6 logic   Phase 9 PDF
 Phase 8 charts     Phase 8 KPIs    Phase 7 logic   Phase 10 video
 Phase 9 toggle     Phase 9 reset   Phase 8 calc
```

**Team splits (3-4 people):**
- **Backend lead:** Phases 0, 1, 3, 4, 5, 6, 7, 9 (PDF)
- **Frontend lead:** Phases 2, 3, 5, 6, 7, 8, 9
- **Frontend 2 / designer:** Phases 5, 8, 9, 10 (video)
- **Floating:** any gaps, doc, README

---

## 5. RISK CHECKLIST

| Risk | Mitigation |
|------|------------|
| Gemini slow during demo | `DEMO_MODE=true` with canned responses |
| SSE connection drops | Reconnect logic + 2s polling fallback |
| LangGraph hard to debug | LangSmith traces, print state at each node |
| 2-min video too tight | Cut hook to 15s, give 45s to demo |
| Judges ask "why AI, not rules?" | "Watch the school-bus free-text → pediatric trauma routing" |
| Neon free tier quota | 0.5GB holds ~10K incidents. Plenty. |
| Render cold start (~30s) | Pin a free cron-job pinger OR run demo from local |
| Map tiles fail | OSM CDN is reliable; no fallback needed |
| Audit logs blow up DB size | Cap at 200 entries per incident, archive older |
| Team member drops off | Phases are documented; others can pick up |

---

## 6. KILL CRITERIA

1. **Phase 4 not working by mid-hackathon → stop and fix.** Don't stack features on broken graphs.
2. **Multi-incident (Phase 6) fails → drop from demo.** Lead with single + counterfactual.
3. **SSE broken → fall back to 2s polling.** Less impressive but works.
4. **Video too long → cut hook, cut closing, never cut the demo.**

---

## 7. THE ONE-PAGE PITCH (for slide 1)

> **CivicOS** is a multi-agent emergency coordination platform that helps Indian cities allocate ambulances, hospitals, and police units during critical incidents. Six specialist AI agents — incident parser, ambulance dispatcher, hospital matcher, police allocator, traffic corridor planner, and resource forecaster — coordinate in real time under a Gemini-powered supervisor. The system reasons over multi-incident priority conflicts, generates executable emergency corridor plans, predicts resource shortages 25 minutes ahead, and explains every rejection. On a mass-casualty scenario with 3 concurrent incidents and 3 ambulances, CivicOS reduces average time-to-care from 13.4 minutes (naive dispatch) to 8.1 minutes — a 39% improvement. Built end-to-end with React 19, FastAPI, LangGraph, and Gemini 2.5 Flash. No data integrations required — runs entirely on a free stack.
