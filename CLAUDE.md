# CLAUDE.md

Guidance for Claude Code when working in this repository.

## What this is

**SaloneFix** — a Freetown (Sierra Leone) public-service incident reporting prototype. Citizens report issues (potholes, drainage, waste, public facilities); human moderators verify and cluster them into incidents; institutional officers (FCC, SLRA, Guma Valley) resolve them with photo evidence; auditors can inspect the full lifecycle; administrators provision staff and institutions.

**Current phase: Human-First Foundation Launch.** AI and WhatsApp are *disabled by design* (`AI_ENABLED=False`, `WHATSAPP_ENABLED=False` in `backend/app/core/config.py`). Do not implement AI recommendations, autonomous routing, merging, or resolution unless the product owner explicitly authorizes a phase transition. The codebase must remain fully usable with AI off.

```text
Human-First Foundation → Human-Only MVP and Baseline → Hybrid Human + AI Assistance
```

## Source of truth

The numbered spec folders under `docs/specs/` are authoritative. Read them before changing behavior, in this order:

1. `01-product-requirements/PRD.md`
2. `02-design/design-guide.md`
3. `03-technical/technical-requirements.md`, `architecture.md`, `domain-data-model.md`, `api-contract.md`
4. `04-workflows/workflow-specification.md` — state machine + who may perform each transition
5. `05-security/security-privacy.md`
6. `06-ai/ai-strategy-and-build-rules.md`
7. `07-testing/testing-and-acceptance.md` — the TC-xxx acceptance cases
8. `08-delivery/agile-backlog.md`, `deployment-and-configuration.md`
9. `09-research/evaluation-protocol.md`
10. `10-ai-developer-instructions.md` — required engineering behavior and prohibited shortcuts

When requirements conflict, prioritize: **(1) safety/privacy/authorization → (2) human accountability & auditability → (3) current phase scope → (4) core user workflow → (5) performance/convenience → (6) future automation.**

Do not invent institutional policy. Record assumptions and ask when a decision affects permissions, privacy, lifecycle state, or scope.

## Repository layout

```
salone fix/
├── backend/                 FastAPI + SQLAlchemy 2 + SQLite (Python 3.12+)
│   ├── main.py              app factory, CORS, request-id + JSON request logging, error handlers, /health
│   ├── alembic/             migrations (0001 baseline, 0002+ changes); alembic.ini at backend root
│   ├── app/core/            config, security (JWT/bcrypt/signed media tokens), dependencies (auth/RBAC/rate limit),
│   │                        exceptions (typed error envelope), logging (JSON lines), pagination
│   ├── app/db/              session.py (engine/Base/get_db), init_db.py (runs migrations + idempotent seed)
│   ├── app/models/          entities.py (ORM), enums.py (all status/role enums)
│   ├── app/schemas/         Pydantic request/response models, one file per domain (incl. admin.py)
│   ├── app/services/        domain logic — report, moderation, incident, assignment, resolution, audit,
│   │                        notification, media_processor, media_links (signed URLs), storage
│   ├── app/api/v1/          router.py + endpoints/ (thin HTTP layer; admin.py = staff/institution provisioning)
│   ├── tests/               pytest suite (conftest: in-memory DB, per-role token fixtures, rate-limit reset)
│   ├── Dockerfile           non-root image; data on /data volume
│   ├── media_storage/       private uploaded images (gitignored, never served as static files)
│   └── .venv/               project virtualenv (Windows)
├── frontend/                React 19 + TypeScript + Vite (no router, no state lib) + Vitest
│   ├── src/App.tsx          auth gate (token → /auth/me) + role-based page switch
│   ├── src/api/client.ts    fetch wrapper: bearer token, ApiError, Page<T> via X-Total-Count, Idempotency-Key, mediaUrl()
│   ├── src/pages/           LoginView, CitizenView, ModeratorView, OfficerView, AuditorView, AdminView
│   ├── src/components/      Header, StatusBadge, IncidentCasesPanel (moderator incident workflow)
│   ├── src/styles/tokens.css design tokens (see docs/specs/02-design/design-guide.md)
│   ├── src/types/index.ts   TS mirrors of backend schemas/enums
│   ├── src/test/setup.ts    Vitest + Testing Library setup; tests live next to sources as *.test.ts(x)
│   └── Dockerfile, nginx.conf
├── scripts/
│   ├── run_demo.py          end-to-end lifecycle walkthrough calling services directly
│   ├── check.ps1            every quality gate with a PASS/FAIL scoreboard (use before push/merge)
│   ├── new-worktree.ps1     isolated feature worktree: own DB/media/ports, junctioned .venv + node_modules
│   └── remove-worktree.ps1  tear-down that unlinks junctions before git removes the worktree
├── docs/
│   ├── specs/               numbered specification pack (01…10) — the source of truth
│   ├── diagrams/            UML/architecture PNGs + Mermaid source
│   └── proposal/            project proposal PDF/DOCX (reference only)
├── everything-claude-code/  vendored ECC toolkit — gitignored, already installed into ~/.claude
├── .github/workflows/ci.yml backend (migrations + pytest) and frontend (lint + test + build)
├── docker-compose.yml       backend + frontend containers for staging/demo
└── .claude/launch.json      "backend" and "frontend" dev servers for the Claude desktop app
```

## Commands

All backend commands run from `backend/` using the project venv.

```bash
# Backend — install
cd backend && .venv/Scripts/python.exe -m pip install -r requirements.txt

# Backend — run API (http://localhost:8000, docs at /docs). Migrations run automatically at startup.
cd backend && .venv/Scripts/python.exe main.py

# Backend — migrations by hand
cd backend && .venv/Scripts/python.exe -m alembic upgrade head
cd backend && .venv/Scripts/python.exe -m alembic revision --autogenerate -m "describe change"

# Backend — tests
cd backend && .venv/Scripts/python.exe -m pytest -q
cd backend && .venv/Scripts/python.exe -m pytest tests/test_security_and_admin.py -q
cd backend && .venv/Scripts/python.exe -m pytest tests/test_reports.py::test_tc_004_valid_media_upload_sanitized -q

# Frontend — install / dev (http://localhost:5173) / lint / test / build
cd frontend && npm install
cd frontend && npm run dev
cd frontend && npm run lint          # oxlint, must be warning-free
cd frontend && npm test              # vitest run
cd frontend && npm run build         # tsc -b && vite build

# Full lifecycle demo against the local SQLite DB
cd backend && .venv/Scripts/python.exe ../scripts/run_demo.py

# All gates in one go (PowerShell) — run this before claiming a branch is done
.\scripts\check.ps1                 # -Quick skips the build; -Backend / -Frontend narrow it

# Feature work happens in worktrees, never directly on main
.\scripts\new-worktree.ps1 -Name feat/thing      # ..\salone-fix.wt\feat-thing, ports 8001/5174
.\scripts\remove-worktree.ps1 -Name feat/thing -DeleteBranch

# Staging/demo containers (needs JWT_SECRET / SESSION_SECRET in a root .env)
docker compose up --build
```

Environment: copy `.env.example` → `backend/.env`, and `frontend/.env.example` → `frontend/.env.local`. Defaults work for local dev. Never commit secrets.

Windows note: when scripting file edits with Python, pass `encoding="utf-8"` (or set `PYTHONUTF8=1`) — the default codepage is cp1252 and will corrupt non-ASCII text.

## Architecture rules

- **Layering:** `endpoints/` → `services/` → `models/`. Endpoints only parse input, resolve the current user, call a service, and return a schema. All business rules, state transitions, and audit writes live in `services/`.
- **Authorization is server-side only.** Use `require_roles([...])` from `app/core/dependencies.py` on every non-public endpoint, and re-check ownership/assignment inside the service: an officer only sees/acts on incidents assigned to their institution; a citizen only sees incidents linked to their own reports, and `get_incident_detail` redacts other reporters' reports and disputes and rounds coordinates for them. Frontend role gating is UX only, never a control.
- **Roles are provisioned, never self-assigned.** `POST /auth/register` always creates a `CITIZEN`. Moderator/officer/auditor/admin accounts are created by an admin via `POST /admin/users`; admins cannot deactivate or demote themselves.
- **Errors:** raise the typed exceptions in `app/core/exceptions.py` (`ValidationError`, `UnauthorizedError`, `ForbiddenError`, `NotFoundError`, `StateConflictError`, `MediaInvalidError`, `MediaTooLargeError`, `RateLimitedError`, `DependencyUnavailableError`). They serialize to `{error_code, message, details, request_id}`; unhandled exceptions become `INTERNAL_ERROR` (details stay in the log). Do not raise bare `HTTPException`.
- **State machine:** the only valid transitions are those in `04-workflows/workflow-specification.md` §2–§4, encoded in `incident_service.transition_incident_status` and the resolution/assignment services. Raise `StateConflictError` on invalid moves. Enums are in `app/models/enums.py`.
- **Audit:** every material action (moderation decision, assignment, status change, evidence submission/media/review, dispute, reopen, user/institution provisioning, audit reads) must write an `AuditEvent` via `audit_service` recording actor, timestamp, reason, previous state, new state.
- **Evidence is immutable.** Never overwrite or delete report media or resolution evidence. Merging a report links it to an incident and marks it `MERGED`; it does not discard it. Media can only be attached to `PENDING` evidence.
- **Resolution evidence:** `POST /incidents/{id}/resolution-evidence` creates the text record; photos go to `POST /incidents/{id}/resolution-evidence/{evidence_id}/media` (same sanitizer as report media, `Idempotency-Key` honoured). Approval for a category with `requires_resolution_evidence=True` is refused with `STATE_CONFLICT` if no photo is attached.
- **Media is private.** All uploads pass through `media_processor.validate_and_sanitize_image` (10 MB cap, magic-byte MIME check, EXIF stripped) and are stored via `storage.py`. `GET /media/{id}` requires an authenticated staff/owner session **or** the signed, expiring token embedded in every `MediaAssetOut.url` (built by `media_links.media_asset_out`). Never add an anonymous fallback and never serve `media_storage/` statically. The frontend uses `mediaUrl(asset)` for `<img src>`.
- **Location privacy:** public/citizen-facing responses return approximate location and `LocationPrecision`, never exact coordinates by default. The citizen UI derives `EXACT`/`APPROXIMATE` from GPS accuracy (≤100 m) and falls back to `USER_ENTERED` landmarks.
- **Pagination:** list endpoints take `limit` (≤100) and `offset` via `core/pagination.page_params` and return the total in `X-Total-Count`; the body stays a plain array. The frontend reads this through `requestPage` → `Page<T>`.
- **Idempotency:** `POST /reports`, `POST /reports/{id}/media`, and evidence media honour `Idempotency-Key`; the client generates one per submission (`newIdempotencyKey()`).
- **Rate limiting:** `rate_limiter(max_requests, window_seconds)` is applied to login, register, report and media creation and returns `429 RATE_LIMITED`. It is in-process/per-IP — fine for the prototype, not multi-worker safe.
- **Integrations behind flags:** anything AI- or WhatsApp-related goes behind an adapter and a feature flag, must be a no-op when disabled, may only *write recommendations*, and must raise `DependencyUnavailableError` (never crash the human workflow) if its provider is down.
- **Notifications** are in-app only (`notification_service`, channel `IN_APP`). Failures are logged via the structured logger and never roll back the triggering action.
- **Logging:** JSON lines to stdout (`app/core/logging.py`), every record carries the `request_id`. Log with `logger.info("event_name", extra={"data": {...}})`. No `print()`.
- **Schema changes:** edit `entities.py`, then `alembic revision --autogenerate`, review the file, and commit it under `backend/alembic/versions/`. `init_db.run_migrations()` upgrades on startup and stamps legacy `create_all` databases at `0001` first. Tests still use `create_all` on an in-memory DB. Keep seed data idempotent.

## Branching and worktrees

- `main` is always green and runnable. Do feature/fix work in a worktree created by `scripts/new-worktree.ps1`; it gets its own SQLite file, `media_storage/` and ports, so experiments cannot corrupt the main checkout's data.
- `backend/.venv` and `frontend/node_modules` inside a worktree are **junctions** to the main checkout. Never `rm -rf` a worktree folder — use `scripts/remove-worktree.ps1`, which unlinks them first. If a branch changes `requirements.txt` or `package.json`, create its worktree with `-FreshDeps`.
- Parallel Alembic revisions produce two heads on merge: resolve with `alembic merge -m "merge heads" <a> <b>`, never by renumbering files.
- `scripts/check.ps1` must pass in the worktree before a branch is pushed or merged; CI runs the same gates.

## Testing conventions

- Backend tests live in `backend/tests/` and use the `client` fixture (FastAPI `TestClient` over an in-memory SQLite `StaticPool` DB, freshly seeded per test). An autouse fixture resets the rate limiter between tests.
- Role fixtures: `citizen_token`, `moderator_token`, `officer_token` (FCC), `slra_officer_token`, `admin_token`, `auditor_token`. Pass as `Authorization: Bearer <token>`.
- Acceptance tests are named after spec cases: `test_tc_00X_...`. When implementing a TC from `07-testing/testing-and-acceptance.md`, add or extend the matching test. Security/admin behaviour lives in `test_security_and_admin.py`.
- Every new endpoint needs at least: a happy-path test, a forbidden-role test, and an invalid-state test where a state machine is involved.
- Frontend tests: Vitest + Testing Library, files `src/**/*.test.ts(x)`. Mock the network by spying on `globalThis.fetch` or the `client` module — never hit a live API from tests.
- Write tests before or alongside implementation. Do not claim completion while tests fail. CI (`.github/workflows/ci.yml`) runs migrations, pytest, oxlint, vitest and the build.

## Seeded personas (dev/test only)

| Role | Contact | Password |
|---|---|---|
| Admin | `admin@salonefix.gov.sl` | `AdminPass123!` |
| Moderator | `moderator@salonefix.gov.sl` | `ModPass123!` |
| Officer (FCC) | `officer.fcc@salonefix.gov.sl` | `OfficerPass123!` |
| Officer (SLRA) | `officer.slra@salonefix.gov.sl` | `OfficerPass123!` |
| Citizen | `citizen@freetown.sl` | `CitizenPass123!` |
| Auditor | `auditor@salonefix.gov.sl` | `AuditorPass123!` |

Seeded categories: `ROAD_POTHOLE`, `DRAINAGE_FLOODING`, `WASTE_MANAGEMENT`, `PUBLIC_FACILITIES` (all `requires_resolution_evidence=True`). Institutions: FCC, SLRA, Guma Valley Water Company. The login page offers these as one-click personas only while `VITE_DEMO_PERSONAS=true`; the seed hashes use cheap bcrypt rounds only when `APP_ENV` is `development`/`test`.

## Frontend conventions

- Plain React function components (`React.FC` is the existing convention in this codebase — match it), `useState`/`useEffect`/`useCallback`, no router — `App.tsx` swaps the page by the signed-in user's role.
- Data loading pattern: `const load = useCallback(async () => {...}, [])` + `useEffect(() => { void load(); }, [load])`, with `loading` initialised to `true`. The `react/set-state-in-effect` lint rule is disabled for this reason (see `.oxlintrc.json`).
- All API calls go through `src/api/client.ts`; add a typed function there rather than calling `fetch` in a component. Keep `src/types/index.ts` in sync with backend schemas/enums. Surface failures with `describeError(err)` into an inline `role="alert"` — no `alert()`/`console.error`.
- Style with the CSS variables in `src/styles/tokens.css` and follow `02-design/design-guide.md`. Target WCAG 2.2 AA: real `<button type="button">`s, labelled inputs (`htmlFor`), `aria-pressed`/`role="tab"` for toggles, decorative icons `aria-hidden`, status conveyed by text not colour alone (`StatusBadge`).
- API base URL comes from `VITE_API_BASE_URL` (`frontend/.env.example`), default `/api/v1`, which the Vite dev server (`vite.config.ts` → `server.proxy`) and the nginx container proxy to the backend. Keep it relative unless the API is hosted separately: it is what lets phones on the LAN use the app with no CORS and keeps the backend bound to localhost. Only `VITE_*` variables reach the bundle — never put secrets there.

## Prohibited shortcuts (from `10-ai-developer-instructions.md`)

- No bypassing authorization for convenience; no frontend-only permission checks; no client-chosen roles.
- No silently discarding reports; no merging without a recorded human decision.
- No marking resolved without required evidence (categories have `requires_resolution_evidence`).
- No calling AI from core lifecycle transitions.
- No exposing exact locations or private media by default (no anonymous media access, no static media serving).
- No "fraud" labels on reports or users.
- No secrets in source; no hard dependency on an unavailable AI/WhatsApp service.

## Working protocol for coding tasks

Before editing: state the requirement, list files inspected, state assumptions, state acceptance criteria.
After editing: summarize changes, list tests run with results, list unresolved risks.

## Known gaps / notes

- Rate limiter and notification delivery are in-process; a multi-worker deployment needs a shared store (Redis) for both.
- Officers have no free-text "progress note" endpoint — progress is expressed via status transitions (`IN_PROGRESS`, `ESCALATED`) and evidence records.
- `due_at` is set at assignment and surfaced as `is_overdue`; nothing yet notifies on overdue.
- Playwright E2E tests are not set up; `scripts/run_demo.py` plus the pytest lifecycle test are the end-to-end checks.
