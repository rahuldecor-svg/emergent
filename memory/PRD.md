# Fire Compliance OS — PRD

## Original Problem
Build "Fire Compliance OS" — enterprise SaaS owned by SSPL (Securrise Solution Pvt Ltd). Multi-tenant fire-safety compliance OS with asset mgmt, inspection, audits, risk, revenue & client lock-in.

## User Choices
- MVP Core web platform (deep, not wide)
- Rule-based scoring (no AI)
- Manual wallet recharge + usage deduction (Phase-2)
- JWT email/password
- In-app + email (Resend, log-only until key provided)

## Architecture (v1.1)
```
backend/
├── server.py            # thin entrypoint
├── seed.py              # idempotent seed
├── core/                # config, db, security (JWT + revocation), deps, emailer, wallet_service, notify
└── routers/             # auth, admin, assets, compliance, wallet, documents, users, notifications
frontend/src/
├── pages/               # Landing, Login, 9 app pages (Dashboard, Assets, Inspections, Maintenance,
│                        #   Incidents, Compliance, Risk Map, Wallet, Documents, Sites, Users, Alerts)
├── components/          # AppShell, ui-kit
└── context/AuthContext
```

## Implemented Timeline
**v1.0 (MVP)** — 2026-04-22
- Landing, auth, SSPL command center, kill-switch, manual wallet recharge+GST
- Client dashboard (Fire Score + NOC + AMC), Assets+QR, Inspections, Maintenance, Incidents, Risk Map
- Wallet, Documents (URL), Notifications, Sites, Users
- Iteration 1 testing: 34/34 green

**v1.0.1 (stabilization)** — 2026-04-22
- Fixed NOC cross-tenant 404 + GST invoice collision + wallet amount validation
- Iteration 2 testing: 52/52 green

**v1.1 (Phase-2)** — 2026-04-22
1. **Usage-based wallet deduction** — ₹10/asset, ₹5/inspection, ₹20/user; grace mode at ≤₹0
2. **Email integration (Resend)** — log-only fallback when `RESEND_API_KEY` empty; templates for inspection fail, maintenance due, low balance, exhausted
3. **Document upload** — multipart → local tenant-scoped storage + streaming download
4. **Logout token revocation** — JWT `jti` + `revoked_tokens` TTL collection
5. **Revenue dashboard** — total_revenue, total_usage, wallets_by_client, recent_transactions on `/api/admin/overview`
6. **Router refactor** — `server.py` now 60 lines, 8 routers + 7 core helpers
- Iteration 3 testing: 65/65 green (13 new Phase-2 + 52 regression)

## Env Variables
`MONGO_URL`, `DB_NAME`, `JWT_SECRET`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `FRONTEND_URL`,
`RESEND_API_KEY` (optional), `EMAIL_FROM`,
`COST_PER_ASSET=10`, `COST_PER_INSPECTION=5`, `COST_PER_USER=20`, `WALLET_LOW_THRESHOLD=500`,
`UPLOAD_DIR=/app/backend/uploads`

## Known Limitations (v1.1)
1. Resend sends live only if `RESEND_API_KEY` is set (fallback logs each email body)
2. File uploads stored on local disk under `UPLOAD_DIR` — single-node; not S3/GCS
3. No mobile/offline technician app
4. No WhatsApp/SMS channels
5. Risk map uses coord-plot, not real map tiles
6. Brute-force key uses ingress proxy IP (NAT users share bucket on same email)
7. No scheduled job runner — maintenance "due soon" emails only fire at task creation (not daily)
8. Wallet does not auto-recharge; SSPL manual credit only

## Backlog
### P0
- [ ] Wire Resend (just drop key into .env)
- [ ] Scheduled daily job: "maintenance due tomorrow" email pass
### P1
- [ ] Object-storage upload (S3/GCS) replacing local disk
- [ ] Stripe/Razorpay self-serve recharge for clients
- [ ] Bulk asset CSV import
- [ ] Role-scoped audit view for client_admins
### P2 (deferred by user)
- [ ] Predictive AI risk engine
- [ ] Android + offline sync
- [ ] WhatsApp/SMS (Twilio)
- [ ] Voice-note Hindi/English inspection
- [ ] White-label partner portal

## Demo Credentials (`/app/memory/test_credentials.md`)
- `superadmin@sspl.in / Sspl@12345` — SSPL root
- `admin@acme.in / Acme@12345` — client admin
- `officer@acme.in / Officer@123` — fire officer
- `tech@acme.in / Tech@12345` — technician
