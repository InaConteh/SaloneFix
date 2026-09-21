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

## Quick start

```bash
# Backend
cd backend
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt     # Windows
cp ../.env.example .env
.venv/Scripts/python.exe -m alembic upgrade head                  # create/upgrade schema
.venv/Scripts/python.exe main.py                                  # http://localhost:8000/docs

# Frontend (second terminal)
cd frontend
npm install
npm run dev                                                       # http://localhost:5173
```

## Using it from a phone

The Vite dev server listens on all interfaces and proxies `/api` to the backend, so a phone on the **same Wi-Fi / hotspot** only needs the laptop's address:

1. Start both servers as above.
2. Find the laptop's IPv4 address (`ipconfig` → Wi-Fi → IPv4, e.g. `172.20.10.10`).
3. On the phone open `http://<that-address>:5173`.

If it does not load, Windows Firewall is blocking Node: allow **Node.js** on private networks when prompted, or run once as administrator:
`netsh advfirewall firewall add rule name="Vite dev server" dir=in action=allow protocol=TCP localport=5173`.
The backend stays bound to `127.0.0.1` and is only reachable through the proxy.

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
