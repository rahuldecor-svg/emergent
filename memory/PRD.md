# Fire Compliance OS — PRD

## Original Problem Statement
Build a category-defining, enterprise-grade SaaS platform "Fire Compliance OS" fully owned, controlled, and operated by Securrise Solution Pvt Ltd (SSPL) — the central operating system for fire safety compliance, maintenance, audits and risk intelligence. Multi-tenant, API-first, must ensure clients never miss compliance, SSPL always controls the ecosystem, data is a long-term strategic asset.

## User Choices (2026-04-22)
- MVP: **1a** Core web platform (deep, not wide)
- Intelligence: **2b** No AI — rule-based scoring
- Payments: **3c** Manual wallet recharge only
- Auth: **4a** JWT email + password
- Notifications: **5a** In-app + Email (Resend infra, key deferred)

## Personas & Roles
| Role | Scope |
|---|---|
| super_admin (SSPL) | Global control, all clients, kill-switch, wallet recharge, audit log |
| client_admin | Own tenant: sites, users, assets, inspections, compliance, wallet |
| fire_officer | Inspections, maintenance scheduling, compliance view |
| technician | Own maintenance tasks + inspections |
| auditor | Read-only inspection & compliance view |
| partner | Reserved for franchise onboarding |

## Architecture
- **FastAPI** + Motor (async MongoDB) backend on :8001, all routes under `/api`
- **React 19** + Tailwind (Swiss/control-room aesthetic, Chivo/IBM Plex/Anton) + Recharts + Sonner
- Auth: JWT access (8h) + refresh (7d) as httpOnly cookies (secure, samesite=none)
- Multi-tenant isolation via `tenant_filter(user)` applied to every client-scoped query
- SSPL sovereignty: `clients.license_active` gate in login; kill-switch toggle per tenant
- Audit trail: `audit_logs` collection for every SSPL action (create, update, kill, recharge)

## Implemented (v1.0 — 2026-04-22)
### SSPL Control Plane
- Command center dashboard (clients, users, assets, wallet totals, risk ladder)
- Client onboarding (creates tenant + primary admin atomically)
- **Kill-switch** (license_active toggle → blocks login with 403)
- **Manual wallet recharge** (adds credit + GST invoice with auto-computed 18% GST)
- Audit log API

### Client Tenant
- **Fire Safety Score 0–100** rule-based: `100 − expired×8 − missed×4 − failed×3` with 6-month trend
- **NOC Readiness** — site checklists vs govt norms, ready/not-ready flag, progress %
- **AMC Conversion Engine** — expired/expiring/missed → suggested service price, total opportunity value
- Asset Management with **QR code** per asset (`qrcode.react`), geo-tagging, category taxonomy
- **Inspection system** — dynamic per-category checklist, pass/fail logic, auto-alerts on fail
- **Maintenance engine** — scheduling, technician assignment, completion → asset.last_maintained
- **Emergency Mode** — incident logging w/ severity, auto-notifies admins
- **Live Risk Map** — geo-dots colored by risk level
- **Prepaid Wallet** — balance, GST invoice history
- **Document Vault** — NOC/certificates/drawings metadata
- **Notification Center** (in-app) with unread badge
- Sites & Users CRUD

### Security & Integrity
- bcrypt password hashing (12 rounds)
- Brute-force lockout (5 fails → 15 min)
- CORS with explicit origin (credentials)
- MongoDB `_id` excluded from every response (verified)
- Unique index on `users.email`, TTL on reset tokens
- `datetime.now(timezone.utc)` throughout

## Test Status (Iteration 1)
- Backend pytest: **34/34 green** at `/app/backend/tests/backend_test.py`
- Frontend smoke: all 9 protected routes + auth flow + interactions ✓
- No critical or minor bugs.

## Known Limitations (v1.0)
1. Email delivery logs-only until `RESEND_API_KEY` is provided (infra wired, inactive)
2. No object-storage upload — Document Vault accepts URLs only
3. No Android/offline technician app (web-responsive only)
4. No WhatsApp/SMS channels
5. Risk-map uses coordinate-plot, not true map tiles (no Google/Mapbox integration)
6. Access token valid full 8h after logout (cookie cleared; no server-side revocation list)
7. Brute-force key uses ingress-proxy IP → NAT users could theoretically lock each other

## Backlog
### P0 (stability)
- [ ] Add refresh-token rotation + server-side revocation list
- [ ] Aggregate super_admin wallet total
### P1 (growth enablers)
- [ ] Wire Resend once key provided
- [ ] Object storage for Document Vault uploads
- [ ] Bulk asset import (CSV)
- [ ] Role-scoped audit-log view for client_admins
### P2 (deferred by user)
- [ ] Predictive AI risk engine
- [ ] Technician Android + offline sync
- [ ] WhatsApp/SMS (Twilio)
- [ ] Voice-note Hindi/English inspection
- [ ] White-label partner/franchise portal

## Next Actions
1. Provide Resend API key → emails go live
2. Provide object-storage preference (S3 / GCS / Emergent object store) → enable uploads
3. Decide on native-mobile vs PWA for technician offline mode
