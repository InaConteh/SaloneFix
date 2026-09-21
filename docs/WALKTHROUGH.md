# SaloneFix — How the Current Version Works

A guided walkthrough of the Human-First Foundation build: what runs where, how a request travels through the system, and how one civic report moves from a citizen's phone to a closed, audited case.

> Companion documents: [`specs/`](specs/) is the requirements pack (source of truth), [`../CLAUDE.md`](../CLAUDE.md) holds engineering conventions, [`../README.md`](../README.md) has the quick start.

---

## 1. The idea in one paragraph

A citizen in Freetown reports a public-service defect — a pothole, a blocked drain, an overflowing bin, a broken street light. A **human moderator** checks it, groups duplicates into one **incident**, and assigns it to the responsible **institution** (FCC, SLRA, Guma Valley). An **officer** at that institution accepts the work, fixes it, and uploads **photo evidence**. A moderator approves the evidence; the citizen can **dispute** if the fix did not hold; an **auditor** can read the complete, append-only history of every decision. No AI or messaging integration participates — by design, in this phase.

```
Citizen ──report──▶ Moderator ──verify/merge──▶ Incident ──assign──▶ Officer
   ▲                                                                  │
   │ dispute                                                 evidence + photo
   │                                                                  ▼
   └──────────────── Moderator approves ◀────── RESOLUTION_UNDER_REVIEW
                            │
                        RESOLVED ──▶ CLOSED          Auditor reads everything
```

---

## 2. What runs where

| Piece | Tech | Port | Role |
|---|---|---|---|
| `backend/` | FastAPI · SQLAlchemy 2 · SQLite · Alembic | 8000 | REST API, all business rules, all authorization, audit trail, private media |
| `frontend/` | React 19 · TypeScript · Vite | 5173 | Role-based single-page client; talks only to the API |
| `scripts/run_demo.py` | Python | — | Drives the full lifecycle through the service layer, prints the audit trail |
| `docker-compose.yml` | Docker | 8000 / 8080 | Staging/demo stack (API + nginx-served frontend) |

Both dev servers can be launched from the Claude desktop app via `.claude/launch.json`, or by hand:

```bash
cd backend  && .venv/Scripts/python.exe main.py     # migrations run, seed data applied, API up
cd frontend && npm run dev                          # Vite dev server
```

Open <http://localhost:5173> — or, from a phone on the same Wi-Fi, `http://<laptop-ip>:5173`; the dev server proxies `/api` to the backend so only one address is needed. The API's interactive docs are at <http://localhost:8000/docs>; `/health` reports the phase and confirms `ai_enabled: false`, `whatsapp_enabled: false`.

---

## 3. Startup: what happens before the first request

1. `main.py` imports `app.core.logging.setup_logging` → all logs become JSON lines on stdout, each stamped with the request ID.
2. The FastAPI `lifespan` calls `init_db()`:
   - `run_migrations()` reads `alembic.ini`, points it at `DATABASE_URL`, and runs `alembic upgrade head`. A database created before Alembic existed (tables but no `alembic_version`) is stamped at revision `0001` first, then upgraded — so old dev databases keep working.
   - Reference data is seeded idempotently: 4 service categories, 3 institutions, 6 demo users (see §10).
3. Middleware is registered: CORS (for the Vite origin), and a request-ID/timing middleware that binds the ID into the log context and echoes it back as `X-Request-ID`.
4. Exception handlers turn every error into one envelope:

```json
{ "error_code": "STATE_CONFLICT", "message": "…actionable text…", "details": {}, "request_id": "…" }
```

Stable codes: `VALIDATION_ERROR`, `UNAUTHORIZED`, `FORBIDDEN`, `NOT_FOUND`, `STATE_CONFLICT`, `MEDIA_INVALID`, `MEDIA_TOO_LARGE`, `RATE_LIMITED`, `DEPENDENCY_UNAVAILABLE`, `INTERNAL_ERROR`.

---

## 4. Anatomy of a request

Every API call follows the same path:

```
HTTP ──▶ endpoints/*.py ──▶ services/*.py ──▶ models/entities.py ──▶ SQLite
           │                    │
           │                    ├─ state-machine checks (StateConflictError)
           │                    ├─ record_audit_event(...)
           │                    └─ notify_*(...)  (in-app notifications)
           └─ Depends(get_current_user / require_roles / rate_limiter / page_params)
```

- **Endpoints** are thin: parse input, resolve the user, call one service function, return a Pydantic schema.
- **Dependencies** (`app/core/dependencies.py`):
  - `get_current_user` decodes the JWT bearer token and loads the active user.
  - `require_roles([...])` is the role gate on every non-public route.
  - `rate_limiter(max, window)` protects login, register, report and media creation (429 `RATE_LIMITED`).
  - `page_params` gives `limit` (≤100) / `offset`; `paginate()` sets `X-Total-Count`.
- **Services** hold every business rule. Object-level checks live here too — an officer is re-checked against the incident's assignment (`require_officer_assigned_to_incident`), a citizen against report ownership.
- **Audit** — `audit_service.record_audit_event` writes actor, action, previous/new value, reason and request ID for every material change. Reading the audit log is itself an audited action.

---

## 5. Authentication and roles

| Role | How the account exists | What they can do |
|---|---|---|
| `CITIZEN` | Self-registers at `POST /auth/register` (role is **always** forced to CITIZEN) | Submit reports, upload photos, track by reference, list own reports, dispute a resolution of an incident linked to their report. `GET /incidents` shows only incidents linked to their own reports, with other citizens' reports/disputes removed and coordinates rounded |
| `MODERATOR` | Provisioned by an admin | Review queue, verify/clarify/reject/escalate/merge, create incidents, link reports, assign institutions, review evidence, reopen, close |
| `OFFICER` | Provisioned by an admin, bound to one institution | See only incidents assigned to their institution; accept/decline; submit evidence + photos; escalate |
| `AUDITOR` | Provisioned by an admin | Read the global and per-incident audit trail |
| `ADMIN` | Seeded / provisioned | Everything a moderator can, plus `/admin/users` and `/admin/institutions` |

Login (`POST /auth/login`) returns a 2-hour JWT. The frontend stores it in `localStorage`, restores the session on reload by calling `GET /auth/me`, and drops to the login page if that fails.

---

## 6. The lifecycle, step by step

This is the exact path exercised by `scripts/run_demo.py` and `tests/test_lifecycle_and_disputes.py`.

### Step 1 — Citizen submits a report
`POST /reports` with category, description, optional coordinates and a `LocationPrecision`.

- The UI asks the device for GPS (`navigator.geolocation`). Accuracy ≤ 100 m → `EXACT`, otherwise `APPROXIMATE`. If permission is refused or unavailable, the citizen describes a landmark → `USER_ENTERED`.
- An `Idempotency-Key` header makes retries safe; without one, an identical payload within 5 s is treated as a double-click.
- The report gets a tracking reference `SF-YYYY-NNNNNN`, status `SUBMITTED`, an audit event, and the citizen is told: *"A moderator will review the report."*

Optional photo: `POST /reports/{id}/media`. The image is size-capped (10 MB), MIME-checked by magic bytes, re-encoded with **all EXIF/GPS metadata stripped**, hashed, and saved to the private `media_storage/` directory. The response's `url` carries a signed, expiring token (see §8).

### Step 2 — Citizen tracks progress
`GET /reports/{reference}/status` is the *safe* public view: status, category, next expected action, responsible institution, `can_dispute`. It never returns exact coordinates or media. The UI's **Track Safe Status** and **My Reports** tabs use it.

### Step 3 — Moderator reviews the queue
`GET /moderation/queue` lists `SUBMITTED` / `UNDER_REVIEW` / `NEEDS_CLARIFICATION` reports (oldest first, paginated) with **nearby reports** (within ~2 km) to surface duplicates. The three-column workspace shows: original evidence · context & duplicates · decision controls.

`POST /moderation/reports/{id}/decision` requires a written **reason** and one of:

| Decision | Report becomes | Effect |
|---|---|---|
| `VERIFY` | `VERIFIED` | Eligible to seed or join an incident |
| `NEEDS_CLARIFICATION` | `NEEDS_CLARIFICATION` | Citizen sees the note in tracking / My Reports |
| `REJECT` | `REJECTED` | Kept, never deleted |
| `ESCALATE` | `ESCALATED` | Flagged for senior review |
| `MERGE` (+ target incident) | `MERGED` | Linked to the incident; original preserved |

The reporter gets an in-app notification for each decision.

### Step 4 — Moderator creates an incident and assigns it
`POST /incidents` (seeded from a verified report) creates a case in `VERIFIED` status. `POST /incidents/{id}/assignments` with an institution (optionally an officer and `due_at`) moves it to `ASSIGNED` and notifies that institution's officers. In the UI this is the **Create Incident & Assign** dialog; later reassignment (after a decline or escalation) happens on the **Incident cases** tab. Additional verified reports can be linked with `POST /incidents/{id}/reports`.

### Step 5 — Officer accepts and works the case
Officers only see incidents assigned to their institution (`GET /incidents` is filtered server-side).
`PATCH /assignments/{id}/status`:
- `ACCEPTED` → incident moves to `IN_PROGRESS`.
- `DECLINED` (reason required) → stays `ASSIGNED`, moderators are notified to reassign.

If blocked, the officer can `PATCH /incidents/{id}/status` → `ESCALATED` with a reason. Overdue assignments (`due_at` passed while `ASSIGNED`/`IN_PROGRESS`) are flagged `is_overdue`.

### Step 6 — Officer submits resolution evidence
1. `POST /incidents/{id}/resolution-evidence` with a work-completion description → evidence record `PENDING`, incident → `RESOLUTION_UNDER_REVIEW`, moderators notified, reporters told the resolution is under review.
2. `POST /incidents/{id}/resolution-evidence/{evidence_id}/media` for each after-repair photo (same sanitizer as report photos, `Idempotency-Key` honoured). Only the officer who submitted the evidence may attach, and only while it is `PENDING`.

The officer UI does both in one dialog and lets the officer **attach more photos** later if a reviewer asks.

### Step 7 — Moderator reviews the evidence
`POST /incidents/{id}/resolution-review` with `APPROVED` or `REJECTED` and a reason.

- **Guard:** if the category has `requires_resolution_evidence = true` (all four seeded categories do) and the pending evidence has **no photo**, approval is refused with `409 STATE_CONFLICT` and an actionable message. The UI disables the Approve button and says why.
- `APPROVED` → incident `RESOLVED`; reporters notified.
- `REJECTED` → back to `IN_PROGRESS`; the institution is told what to fix.

### Step 8 — Citizen disputes (optional)
Once `RESOLVED`, tracking shows `can_dispute: true`. `POST /incidents/{id}/disputes` with a reason — only by a citizen whose report is linked to that incident — moves it to `DISPUTED` and alerts moderators.

### Step 9 — Moderator reopens or closes
- `POST /incidents/{id}/reopen` (from `DISPUTED`, `RESOLVED` or `CLOSED`) → `RESOLUTION_UNDER_REVIEW`, the open dispute is marked `ACCEPTED`, reporters notified.
- `PATCH /incidents/{id}/status` → `CLOSED` from `RESOLVED` ends the case (`closed_at` set).

### Step 10 — Auditor inspects
`GET /incidents/{id}/audit` returns the chain for the incident **and** its linked reports and assignments. `GET /events` is the global log, filterable by `entity_type`/`action`, paginated. Both calls write an `AUDIT_ACCESSED` event of their own.

---

## 7. The state machines

**Report**

```
SUBMITTED ─▶ UNDER_REVIEW ─┬─▶ VERIFIED
                           ├─▶ NEEDS_CLARIFICATION
                           ├─▶ MERGED
                           ├─▶ REJECTED
                           └─▶ ESCALATED
```

**Incident** (only these transitions are accepted; anything else is `STATE_CONFLICT`)

```
VERIFIED ─▶ ASSIGNED ─▶ IN_PROGRESS ─▶ RESOLUTION_UNDER_REVIEW ─▶ RESOLVED ─▶ CLOSED
              │  ▲          │  ▲               │                    │           │
              │  │          │  └── (evidence rejected) ◀────────────┘           │
              │  │          └─▶ ESCALATED ─▶ ASSIGNED (reassign)     DISPUTED ◀─┘
              │  └────────────────────────────────┘                    │
              └─ officer DECLINED (stays ASSIGNED)      reopen ──▶ RESOLUTION_UNDER_REVIEW
```

Who may trigger what is enforced by `require_roles` at the endpoint and re-checked in the service (`docs/specs/04-workflows/workflow-specification.md` §4 is the authoritative table).

---

## 8. Privacy and security controls you will run into

| Control | Where | Behaviour |
|---|---|---|
| Server-side RBAC + object checks | `dependencies.require_roles`, services | UI gating is cosmetic; the API decides |
| No self-assigned roles | `auth.register` | Always `CITIZEN`; staff via `/admin/users` |
| Private media | `endpoints/media.py`, `services/media_links.py` | `GET /media/{id}` needs a staff/owner session **or** the signed, 1-hour token embedded in every `MediaAssetOut.url`. Anonymous → 403. Nothing is served as static files. |
| Metadata stripping | `services/media_processor.py` | Pixels are copied into a fresh image; EXIF/GPS/ICC never reach disk |
| Location minimisation | `reports/{ref}/status`, `incidents/public/map`, citizen view of `incidents/*` | Public and citizen views expose only precision class or coordinates rounded to 2 dp (~1 km); citizens never see another citizen's report or dispute |
| Rate limiting | `dependencies.rate_limiter` | Login 20/min, register 10/min, report & media 30/min per IP → 429 |
| Idempotency | reports, report media, evidence media | Same `Idempotency-Key` returns the original record |
| Audit everything | `services/audit_service.py` | Material actions, provisioning, and audit reads |
| Human-first guarantee | `config.py`, `/health` | `AI_ENABLED`/`WHATSAPP_ENABLED` default off; the app must start and complete every workflow without them (tested: TC-012/013) |

---

## 9. The frontend, screen by screen

`App.tsx` restores the session and renders one page per role:

| Screen | File | What you can do |
|---|---|---|
| **Login** | `pages/LoginView.tsx` | Sign in · create a citizen account (consent checkbox) · one-click demo personas when `VITE_DEMO_PERSONAS=true` |
| **Citizen** | `pages/CitizenView.tsx` | *Submit Public Report* (category cards, description, GPS or landmark, photo) · *Track Safe Status* (by reference, dispute when allowed) · *My Reports* |
| **Moderator** | `pages/ModeratorView.tsx` + `components/IncidentCasesPanel.tsx` | *Report queue* tab: three-column review with the five decisions and Create Incident & Assign · *Incident cases* tab: filters (Needs my decision, Evidence review, Disputed…), evidence photos, approve/reject, reopen, close, link report, assign/reassign with due date |
| **Officer** | `pages/OfficerView.tsx` | Assigned cases for your institution · accept/decline · submit evidence + photos · attach more photos · escalate · overdue flag |
| **Auditor** | `pages/AuditorView.tsx` | Global log with entity filter and pagination, or one incident's full chain |
| **Admin** | `pages/AdminView.tsx` | Provision staff (moderator/officer/auditor/admin), deactivate/reactivate with reason · register/deactivate institutions · embedded moderator workspace |

All network access goes through `src/api/client.ts`: bearer token, `Idempotency-Key` generation, `Page<T>` from `X-Total-Count`, typed `ApiError`, and `mediaUrl()` that turns the API's signed relative URLs into absolute `<img src>` values. Errors surface inline as `role="alert"` banners; status is always shown as text (`StatusBadge`), never colour alone.

---

## 10. Demo data

Seeded on first start (development only):

| Persona | Contact | Password |
|---|---|---|
| Citizen — Fatu Kamara | `citizen@freetown.sl` | `CitizenPass123!` |
| Civic Moderator | `moderator@salonefix.gov.sl` | `ModPass123!` |
| FCC Works Officer | `officer.fcc@salonefix.gov.sl` | `OfficerPass123!` |
| SLRA Roads Officer | `officer.slra@salonefix.gov.sl` | `OfficerPass123!` |
| Independent Auditor | `auditor@salonefix.gov.sl` | `AuditorPass123!` |
| System Administrator | `admin@salonefix.gov.sl` | `AdminPass123!` |

Categories: Roads & Potholes, Drainage & Flooding, Waste Management, Public Facilities (all require photo evidence for resolution). Institutions: Freetown City Council, Sierra Leone Roads Authority, Guma Valley Water Company.

### Try the whole walk in ten minutes
1. Sign in as **Citizen** → submit a Roads & Potholes report with a photo → note the `SF-…` reference.
2. Sign out → **Civic Moderator** → *Report queue* → Verify it → **Create Incident & Assign** to FCC.
3. Sign out → **FCC Works Officer** → Accept → **Submit completion evidence** with an after-repair photo.
4. Sign out → **Civic Moderator** → *Incident cases* → *Evidence review* → Approve (try approving first without a photo to see the guard).
5. Sign out → **Citizen** → *Track Safe Status* with your reference → **Dispute**.
6. Sign out → **Civic Moderator** → *Disputed* → Reopen.
7. Sign out → **Independent Auditor** → pick the incident → read the full decision chain.

Or run it non-interactively: `cd backend && .venv/Scripts/python.exe ../scripts/run_demo.py`.

---

## 11. Data model at a glance

```
User ──(reporter)──▶ Report ──▶ MediaAsset (report photos)
                       │
                       └── ReportIncidentLink ──▶ Incident ──▶ Assignment ──▶ Institution / User(officer)
                                                     │
                                                     ├──▶ ResolutionEvidence ──▶ MediaAsset (after-repair photos)
                                                     ├──▶ Dispute
                                                     └──▶ AuditEvent (by entity_type/entity_id)
ModerationDecision ──▶ Report          Notification ──▶ User          ServiceCategory ◀── Report / Incident
```

Schema changes go through Alembic (`backend/alembic/versions/`): `0001` is the baseline, `0002` added `media_assets.idempotency_key`.

---

## 12. How it is tested

| Layer | Command | What it covers |
|---|---|---|
| Backend (30 tests) | `cd backend && .venv/Scripts/python.exe -m pytest -q` | All 15 acceptance cases TC-001…TC-015 from the testing spec; the complete lifecycle with dispute and reopen; media privacy; registration lockdown; admin provisioning; pagination; rate limiting |
| Frontend (14 tests) | `cd frontend && npm test` | API client (token, pagination header, idempotency key, typed errors), `StatusBadge`, `LoginView` (sign in, error display, citizen-only registration) |
| Static | `npm run lint` · `npm run build` | oxlint (warning-free) and the TypeScript/Vite production build |
| End-to-end | `scripts/run_demo.py` | Full lifecycle through the service layer with printed audit chain |
| All of the above | `.\scripts\check.ps1` | Runs every gate locally with a PASS/FAIL scoreboard; use it inside a feature worktree before pushing |
| CI | `.github/workflows/ci.yml` | Same gates plus dependency audits, on every push and PR |

Feature work is done in isolated worktrees (`scripts/new-worktree.ps1`), each with its own database, media folder and ports — see the README section *Working on features safely*.

---

## 13. What is deliberately *not* in this version

- No AI recommendations, auto-routing, auto-merge or auto-resolve — Phase 3 work, to be added behind an adapter and feature flag that only ever *writes recommendations*.
- No WhatsApp/SMS/email delivery — notifications are in-app; the channel abstraction and failure logging are in place.
- No free-text officer progress notes (progress is expressed through status transitions and evidence records).
- No overdue notifications (the flag exists; nothing fires on it yet).
- In-process rate limiter and notification queue — fine for a single-worker prototype, needs a shared store for scale.
