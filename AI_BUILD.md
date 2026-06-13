# JIRACHI AI Build Handoff

## Source of Truth

- Main plan file: `CIVICOS_FINAL.md`
- Project name changed from CivicOS to `JIRACHI`.
- User instruction: follow phases strictly. Do not implement improvements or architecture changes without asking first.

## Current Status

Phase 0 foundation is mostly complete.

Completed:

- Initialized Git repo inside `C:\Users\ktkrr\Desktop\JIRACHI`.
- Installed/used `uv` via `python -m uv`.
- Installed/used `pnpm` through Corepack.
- Created backend project in `backend/`.
- Added exact backend dependencies from Phase 0:
  - FastAPI
  - uvicorn
  - SQLAlchemy async
  - asyncpg
  - Alembic
  - Pydantic
  - pydantic-settings
  - LangGraph
  - langchain-google-genai
  - google-genai
  - sse-starlette
  - supabase
  - reportlab
  - haversine
  - python-jose
- Created backend files:
  - `backend/app/main.py`
  - `backend/app/config.py`
  - `backend/app/db.py`
  - `backend/app/__init__.py`
- Backend `/health` returns:

```json
{"status":"ok","app":"JIRACHI"}
```

- Created frontend project in `frontend/`.
- Corrected scaffold to match planned stack:
  - Vite 5
  - React 19
  - TypeScript 5.6
  - Tailwind CSS v4
  - TanStack Router
  - TanStack Query
  - Zustand
  - Leaflet / react-leaflet
  - Recharts
  - Lucide React
  - Supabase JS
  - shadcn/ui
- Created frontend files:
  - `frontend/src/App.tsx`
  - `frontend/src/main.tsx`
  - `frontend/src/index.css`
  - `frontend/vite.config.ts`
  - `frontend/tailwind.config.ts`
  - `frontend/components.json`
  - `frontend/src/lib/utils.ts`
- Generated shadcn components from Phase 0:
  - `button`
  - `card`
  - `dialog`
  - `table`
  - `badge`
- Created root files:
  - `.env.example`
  - `.gitignore`
  - `README.md`

## Verification Already Done

Backend:

```powershell
cd C:\Users\ktkrr\Desktop\JIRACHI\backend
python -m uv run python -c "from fastapi.testclient import TestClient; from app.main import app; response = TestClient(app).get('/health'); print(response.status_code); print(response.json())"
```

Result:

```text
200
{'status': 'ok', 'app': 'JIRACHI'}
```

Frontend:

```powershell
cd C:\Users\ktkrr\Desktop\JIRACHI\frontend
corepack pnpm exec tsc --noEmit
corepack pnpm exec vite build
```

Result:

- TypeScript check passed.
- Vite production build passed.

Dev servers were started for Phase 0 verification:

- Backend: `http://127.0.0.1:8000`
- Frontend: `http://127.0.0.1:5173`

Both responded successfully:

- `GET http://127.0.0.1:8000/health` returned 200.
- `GET http://127.0.0.1:5173` returned 200.

Logs are in:

- `logs/backend.out.log`
- `logs/backend.err.log`
- `logs/frontend.out.log`
- `logs/frontend.err.log`

## Important Notes

- Browser visual verification was about to start but was interrupted by the user. Do not assume it was completed.
- Local Python is `3.13.7`, but the planned stack says Python `3.12`. `backend/pyproject.toml` was set to `>=3.12,<3.14` so the project still targets the planned stack while running locally.
- `uv` is not directly on PATH. Use:

```powershell
python -m uv ...
```

- `pnpm` is available through Corepack. Use:

```powershell
corepack pnpm ...
```

- pnpm required approving `esbuild` build scripts. This was already approved with:

```powershell
corepack pnpm approve-builds esbuild
```

## Secrets Needed Later

Do not hardcode secrets. Ask the user to create `.env` from `.env.example`.

Required values from `.env.example`:

- Line 2: `DATABASE_URL`
- Line 3: `SUPABASE_URL`
- Line 4: `SUPABASE_ANON_KEY`
- Line 5: `GEMINI_API_KEY`
- Line 11: `VITE_SUPABASE_URL`
- Line 12: `VITE_SUPABASE_ANON_KEY`

For Phase 1 database work, the next AI will need `DATABASE_URL` first.

## Resume Point

Resume from Phase 1: Data Layer + Delhi Seed.

Next steps, strictly from `CIVICOS_FINAL.md`:

1. Initialize Alembic in `backend/`.
2. Create `backend/app/models.py` with the four locked tables:
   - `incidents`
   - `resources`
   - `assignments`
   - `audit_logs`
3. Create `backend/app/schemas.py` with Pydantic v2 request/response schemas.
4. Configure Alembic autogenerate from SQLAlchemy models.
5. Ask user for `DATABASE_URL` before running migrations.
6. Create `backend/app/seed.py` with Delhi resources:
   - 8 hospitals from the plan.
   - 12 ambulances inside Delhi bbox `[28.55-28.72, 77.10-77.30]`.
   - 10 police units inside same bbox.
7. Add `GET /resources`.
8. Add stub `GET /kpi`.

Do not start Phase 3 until Phase 1 and Phase 2 are done as planned.

## Known Strictness Issues To Preserve

These were noticed in the plan, but no architecture change was made:

- API table has `/incidents/simulate`, while Phase 6 mentions `/incidents/simulate/mass-casualty`.
- Diagram mentions `/export/pdf`, while endpoint table uses `/incidents/{id}/pdf`.
- KPI section mentions ICU fields, but locked DB schema only has generic `capacity_total` and `capacity_used`.

Ask the user before resolving these.
