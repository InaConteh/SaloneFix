# SaloneFix

Freetown public-service incident reporting prototype. Citizens report civic issues (potholes, drainage, waste, public facilities); human moderators verify and cluster them into incidents; institutional officers resolve them with evidence; auditors can inspect the full lifecycle.

**Current phase:** Human-First Foundation Launch — AI and WhatsApp integrations are disabled by design. Start with [`docs/WALKTHROUGH.md`](docs/WALKTHROUGH.md) for how the system works end to end, [`docs/specs/README.md`](docs/specs/README.md) for the phase plan, and [`CLAUDE.md`](CLAUDE.md) for engineering conventions.

## Layout

```
backend/     FastAPI + SQLAlchemy 2 + SQLite API (Python 3.12+)
frontend/    React 19 + TypeScript + Vite client
scripts/     run_demo.py — end-to-end lifecycle walkthrough
docs/
  specs/     Numbered specification pack (PRD, design, API contract, workflows, security, testing, delivery)
  diagrams/  UML / architecture diagrams (+ Mermaid source for the use-case diagram)
  proposal/  Project proposal (PDF / DOCX)
```

## Running the application

The app is two processes: a **FastAPI backend** on port 8000 and a **Vite dev server** on port 5173. The dev server proxies `/api` and `/health` to the backend, so the browser only ever talks to `localhost:5173` — no CORS setup, and the backend never has to be exposed.

### Prerequisites

| | Version | Notes |
|---|---|---|
| Python | 3.12 or newer | CI uses 3.12; 3.13/3.14 also work |
| Node.js | 22 or newer | CI uses 22; 24 also works |
| Git | any recent | |

No database server is needed — SQLite lives in a file the app creates for itself.

### 1. First-time setup

Run these once after cloning. **Windows (PowerShell or Git Bash):**

```bash
# Backend
cd backend
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
cp ../.env.example .env
```

```bash
# Frontend (from the repo root)
cd frontend
npm install
cp .env.example .env.local
```

**macOS / Linux** — identical, except the interpreter is `.venv/bin/python` instead of `.venv/Scripts/python.exe` everywhere below.

The two `.env` files are gitignored and the defaults work as-is for local development. Change the secrets in `backend/.env` before deploying anywhere real.

### 2. Start the servers

Two terminals, one each. Leave both running.

**Terminal 1 — backend** (from `backend/`):

```bash
.venv/Scripts/python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

On startup it applies database migrations, seeds the reference data (categories, institutions, demo accounts) if they are missing, and serves interactive API docs at <http://localhost:8000/docs>. You do not need to run migrations by hand.

**Terminal 2 — frontend** (from `frontend/`):

```bash
npm run dev
```

Then open **<http://localhost:5173>**.

> `python main.py` also starts the backend, but it binds `0.0.0.0` (every network interface). The `uvicorn` command above keeps it on `127.0.0.1`, which is what you want on a shared or public network.

**Using the Claude desktop app instead?** `.claude/launch.json` already defines both servers — start `backend` and `frontend` from the Browser pane and skip the terminals.

### 3. Check it is working

```bash
curl http://localhost:5173/health
```

Expected — note this comes *through* the proxy, so it proves both processes and the link between them:

```json
{"status":"healthy","phase":"Human-First Foundation Launch","ai_enabled":false,"whatsapp_enabled":false}
```

### 4. Sign in

On the login page, either create a citizen account or click one of the **demo personas** (see the table at the end of this file) to jump straight into a role. Each role opens a different workspace:

| Role | What you see |
|---|---|
| Citizen | Submit a report (camera + GPS), track status, my reports, dispute a resolution |
| Moderator | Review queue (verify / clarify / merge / reject / escalate), incident cases, evidence review, reopen, close |
| Officer | Cases assigned to your institution: accept/decline, submit resolution evidence with photos, escalate |
| Auditor | The full append-only audit trail, filterable by case and entity |
| Admin | Provision staff accounts and institutions, plus the moderator workspace |

For a guided tour of the whole lifecycle, see [`docs/WALKTHROUGH.md`](docs/WALKTHROUGH.md).

### Stopping

`Ctrl+C` in each terminal. Nothing is left running in the background.

### Running it from a phone

The dev server listens on all interfaces and proxies the API, so a phone on the **same Wi-Fi / hotspot** only needs the laptop's address:

1. Start both servers as above.
2. Find the laptop's IPv4 address — `ipconfig` on Windows (Wi-Fi → IPv4), `ipconfig getifaddr en0` on macOS. For example `172.20.10.10`.
3. On the phone open `http://<that-address>:5173`.

Everything works from the phone, including the real camera and GPS on the citizen report form.

If the page does not load, Windows Firewall is blocking Node: allow **Node.js** on private networks when prompted, or run once in an **administrator** terminal:

```powershell
netsh advfirewall firewall add rule name="Vite dev server" dir=in action=allow protocol=TCP localport=5173
```

The backend stays bound to `127.0.0.1` and is reachable only through the proxy.

### If a port is already in use

**Port 5173 (frontend)** — Vite will offer the next free port; just use the URL it prints.

**Port 8000 (backend)** — start the backend on another port and point the proxy at it. In `frontend/.env.local`:

```
API_PROXY_TARGET=http://127.0.0.1:8010
```

then run the backend with `--port 8010`. Restart the dev server so it picks up the change. Nothing else needs editing, because the frontend addresses the API through the relative `/api/v1` path.

To find out what is holding a port:

```powershell
netstat -ano | findstr :8000     # last column is the PID
```

### Everything in containers (staging / demo)

Needs `JWT_SECRET` and `SESSION_SECRET` in a `.env` file at the repo root:

```bash
docker compose up --build
```

Frontend on <http://localhost:8080>, with the API proxied under `/api/` by nginx. The backend container is not published to the host.

### Seeing the lifecycle without the UI

Drives a full report → moderation → assignment → evidence → dispute → reopen cycle through the service layer and prints the resulting audit trail:

```bash
cd backend && .venv/Scripts/python.exe ../scripts/run_demo.py
```

### Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `ModuleNotFoundError: No module named 'fastapi'` | Using system Python. Use the venv interpreter (`.venv/Scripts/python.exe`), or re-run the install step. |
| Login fails, or the page shows a network error | Backend is not running, or is on a different port than `API_PROXY_TARGET`. Check `curl http://localhost:5173/health`. |
| `/health` returns something that is not SaloneFix | Another project is on port 8000 and the proxy is reaching it. See *If a port is already in use*. |
| Page loads but every action errors | Restart the dev server after any change to `.env.local` — Vite reads it only at startup. |
| Want to start from clean data | Stop the backend, delete `backend/salonefix.db` and `backend/media_storage/`, start again. Schema and demo accounts are recreated. |
| Demo persona buttons should not appear | Set `VITE_DEMO_PERSONAS=false` in `frontend/.env.local` and restart the dev server. |

## Checking a branch

One command runs every gate (migrations on an empty DB, human-first start-up check, pytest, oxlint, vitest, production build) and prints a scoreboard:

```powershell
.\scripts\check.ps1            # all gates       (-Quick skips the build, -Backend / -Frontend to narrow)
```

Individually:

```bash
cd backend && .venv/Scripts/python.exe -m pytest -q
cd frontend && npm run lint && npm test && npm run build
```

## Working on features safely (git worktrees)

`main` stays runnable at all times; each feature or fix lives in its own worktree with its **own database, media folder and ports**, while sharing the installed `.venv` and `node_modules` through directory junctions so nothing is reinstalled.

```powershell
.\scripts\new-worktree.ps1 -Name feat/my-feature            # -> ..\salone-fix.wt\feat-my-feature on ports 8001 / 5174
.\scripts\new-worktree.ps1 -Name fix/other -BackendPort 8002 -FrontendPort 5175
```

Inside the worktree: run `.\scripts\check.ps1`, start the servers (the generated `.claude\launch.json` already uses the right ports), commit, push, open a PR. When merged:

```powershell
.\scripts\remove-worktree.ps1 -Name feat/my-feature -DeleteBranch
```

Always use `remove-worktree.ps1` rather than deleting the folder: it unlinks the junctions first so the shared `.venv` / `node_modules` are never deleted along with the worktree.

## Demo personas

| Role | Contact | Password |
|---|---|---|
| Citizen | `citizen@freetown.sl` | `CitizenPass123!` |
| Moderator | `moderator@salonefix.gov.sl` | `ModPass123!` |
| Officer (FCC) | `officer.fcc@salonefix.gov.sl` | `OfficerPass123!` |
| Officer (SLRA) | `officer.slra@salonefix.gov.sl` | `OfficerPass123!` |
| Auditor | `auditor@salonefix.gov.sl` | `AuditorPass123!` |
| Admin | `admin@salonefix.gov.sl` | `AdminPass123!` |

Seeded on first start for development only.
