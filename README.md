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

## Tests

```bash
cd backend && .venv/Scripts/python.exe -m pytest -q
cd frontend && npm run lint && npm test && npm run build
```

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
