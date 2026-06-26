# Fire Compliance OS — Changelog

All notable changes to this project are documented here.
Format adheres to [Keep a Changelog](https://keepachangelog.com/) · [Semantic Versioning](https://semver.org/).

---

## [v1.4.0-phase6-p0] — 2026-04-22 — **Phase 6 P0 Closure**

### Added
- **Razorpay wallet recharge** — full self-serve payment flow
  - `POST /api/payments/order` — Razorpay order creation (tenant-scoped, intent stored)
  - `POST /api/payments/verify` — HMAC-SHA256 signature verification (constant-time)
  - `POST /api/payments/webhook` — async safety net with webhook signature verify
  - `GET /api/payments/invoice/{invoice_no}` — GST invoice PDF (CGST + SGST split, HSN/SAC, SSPL metadata)
  - `GET /api/payments/config` — public Razorpay key for frontend
  - `GET /api/payments/orders` — tenant order history
  - `GET /api/payments/admin/orders` — SSPL view of all orders
  - Frontend Wallet page: Razorpay Checkout integration + auto invoice download
- **Real email** — `core/emailer.py` cascade: Resend → SMTP → log-only
  - Tracks every send in new `db.email_log` collection
  - New template: `tpl_password_reset()`
- **WhatsApp + SMS** — `core/messaging.py`
  - Meta WhatsApp Business Cloud API (v20.0) primary
  - MSG91 Flow API v5 SMS fallback (DLT-compliant India)
  - Auto-fallback on failure; records in new `db.messaging_log`
  - Phone normalization: `+91…`, `91…`, 10-digit → E.164
  - `fire_and_forget()` wrapper — never blocks API caller
  - Wired into: `wallet_exhausted`, `low_wallet`, `inspection_failure`
- **Cloudflare R2 storage** — `core/storage.py`
  - S3-compatible via boto3
  - Tenant-scoped object keys: `tenants/{client_id}/{doc_id}-{filename}`
  - Presigned URL downloads (302 redirect, zero egress through app)
  - Local disk fallback when R2 unconfigured
- **Self-service password reset**
  - `POST /api/auth/password-reset/request` — non-enumerating, SHA-256 hashed tokens, TTL auto-expiry
  - `POST /api/auth/password-reset/confirm` — single-use, validates expiry, clears login lockouts
  - Frontend: `/forgot-password` + `/reset-password?token=` pages
  - "Forgot password?" link on Login page
- **User phone field** + endpoints
  - `phone` field added to user model (E.164 format)
  - `POST /api/users/me/phone` — self-service phone update
  - `PATCH /api/users/{uid}` — admin user updates (name, phone, role)
- **DB collections** (new in v1.4):
  - `payment_orders` — Razorpay order intents + status tracking
  - `email_log` — every email send attempt
  - `messaging_log` — every WhatsApp/SMS attempt
  - `password_reset_tokens` — hashed tokens with TTL index
- **New env vars** (~30):
  - Razorpay: `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`, `RAZORPAY_WEBHOOK_SECRET`
  - GST: `SSPL_GSTIN`, `SSPL_COMPANY_NAME`, `SSPL_ADDRESS`, `SSPL_STATE_CODE`, `SSPL_PAN`, `SSPL_HSN_CODE`, `GST_RATE`
  - Email: SMTP fallback + `PASSWORD_RESET_TTL_HOURS`
  - WhatsApp: `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_API_VERSION`, 4 template names
  - MSG91: `MSG91_AUTHKEY`, `MSG91_SENDER_ID`, 4 DLT template IDs
  - R2: `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET`, `R2_PUBLIC_BASE_URL`, `R2_REGION`
  - `MAX_UPLOAD_MB`
- **Documentation**:
  - `/app/SCN_PRODUCT_BIBLE.md` — 1,252-line master reference (20 sections)
  - `/app/CLOSURE_REPORT_v1.4.md` — formal audit report
  - `/app/CHANGELOG.md` — this file
  - Razorpay self-test: `/app/backend/tests/test_payments_flow.py`

### Changed
- `core/wallet_service.py` — `charge()` and `credit()` now trigger WhatsApp/SMS alerts on critical events
- `routers/documents.py` — refactored to use `core/storage.py` abstraction
- `routers/auth.py` — added password reset endpoints
- `routers/users.py` — added `PATCH /users/{uid}` and `POST /users/me/phone`
- `server.py` — mounted new `payments` router (16th)
- `requirements.txt` — pinned `setuptools<81` (Razorpay SDK uses deprecated `pkg_resources`)

### Fixed
- `routers/payments.py` — removed unused `h1` style variable, removed unnecessary f-string prefix
- `core/db.py` — added unique index on `payment_orders.order_id`
- `core/db.py` — added indexes on `messaging_log` and `email_log` for fast querying

### Security
- All Phase-6 keys read **strictly from env** (no hardcoded defaults)
- Razorpay signature verification uses `hmac.compare_digest` (constant-time, replay-safe)
- Password reset tokens stored as SHA-256 hashes (raw token never persists)
- Reset endpoint non-enumerating (same response for known/unknown emails)
- R2 presigned URLs expire in 5 minutes
- All file uploads tenant-scoped via object key prefix

### Tests
- **122/122 pass** (22 Phase-6 + 100 Phase 1–5 regression)
- Test report: `/app/test_reports/iteration_7.json`

### Migration / Operator Notes
- Run `sudo supervisorctl restart backend` after editing `.env`
- All Phase-6 integrations gracefully degrade when keys empty (no crashes)
- Use Razorpay test mode first (`rzp_test_…`) — switch to live after validation
- Razorpay webhook URL: `https://yourdomain.com/api/payments/webhook`
- WhatsApp templates must be pre-approved by Meta before going live
- MSG91 SMS templates require DLT registration in India

### Documentation Fixes (post-audit)
- Database Dictionary: clarified `support_tickets` → actual code uses `support_requests`
- Database Dictionary: added missing `scheduler_runs` collection
- Database Dictionary: corrected `asset_master_catalog` (not a collection — static Python constant)

---

## [v1.3.0] — Q1 2026 — Phase 5 — Mobile + PWA

### Added
- Progressive Web App: `manifest.json`, `service-worker.js`, install prompt (`InstallPrompt.jsx`)
- 7-day dismiss memory on install banner
- Mobile responsive: hamburger drawer at <768px, all touch targets ≥44px
- Camera-based QR scanning at `/app/scan` using `html5-qrcode`
- Rear camera preference + manual URL/ID paste fallback
- Quick-Pass Inspection (1-tap pass) on AssetDetail
- Apple web-app meta tags for iOS

### Tests
- 100 backend + 17 Phase-5 frontend assertions pass

---

## [v1.2.1] — Phase 4 — Asset Master + Polish

### Added
- Asset Master Catalog (static reference for extinguishers, hydrants, sprinklers, etc.)
- Bulk QR PDF sheet generation
- Bilingual Help Center (EN/HI)
- Terms & Conditions page
- Friendly error messages across the app

### Tests
- 100 tests pass

---

## [v1.2.0] — Phase 3 — AMC + Compliance

### Added
- AMC Conversion Engine — detects expired/expiring assets, surfaces booking opportunities
- `POST /api/amc/book-service` — service booking flow
- Daily Scheduler (APScheduler) — runs `scan_and_alert` at 03:00 UTC
- One-click Demo Mode (`POST /api/demo/login`) with sample tenant + reset
- NOC Readiness Checklist per site
- Support Ticket system (client ↔ SSPL)
- PDF Compliance Reports (ReportLab) with score, summary, NOC, expired assets, failed inspections
- Severity scoring on incidents

### Tests
- 86 tests pass

---

## [v1.1.0] — Phase 2 — Revenue Engine + Stabilisation

### Added
- Prepaid wallet system with per-asset/inspection/user deduction
- Read-only grace mode at zero balance (blocks new resource creation)
- Wallet transactions ledger with running balance
- GST invoice numbering: `INV-YYYYMMDDHHMMSS` unique sequence
- Email alerts (initially mocked): low balance, wallet exhausted, inspection fail
- Manual wallet recharge by SSPL (`POST /api/admin/wallet/recharge`)
- Configurable pricing: `COST_PER_ASSET`, `COST_PER_INSPECTION`, `COST_PER_USER`, `WALLET_LOW_THRESHOLD`

### Changed
- Major code refactor: monolithic `server.py` → modular `core/` + `routers/`

### Tests
- 65 tests pass

---

## [v1.0.1] — Stabilisation

### Fixed
- Token revocation persisting beyond logout
- Login lockout edge cases
- Cookie attribute consistency (samesite=none)

### Tests
- 52 tests pass

---

## [v1.0.0] — MVP — Q4 2025

### Added — Initial Release
- Multi-tenant SaaS architecture with strict `client_id` isolation
- JWT authentication in httpOnly cookies (access 8h, refresh 7d)
- 5-role RBAC: super_admin, client_admin, fire_officer, technician, inspector
- SSPL Super Admin with kill-switch over any tenant
- Asset Management: sites, assets, categories, expiry tracking
- QR code generation per asset
- Inspections + Incidents with checklists and severity scoring
- Daily Maintenance task tracking
- Login lockout: 5 failed → 15-min lock
- Audit logs (`audit_logs` collection) for all sensitive actions
- React 19 + Tailwind + shadcn frontend
- Landing + Login + 18 internal pages

### Tests
- 34 tests pass

---

## Version Numbering

- **Major (X.0.0)**: Breaking schema changes, removed endpoints, major architecture shifts
- **Minor (1.X.0)**: New modules, new integrations, additive endpoints (current — Phase 1 → 6)
- **Patch (1.4.X)**: Bug fixes, perf, copy changes, dependency bumps

## Release Tag Format
- Production-ready: `vMAJOR.MINOR.PATCH` (e.g., `v1.4.0`)
- Phase milestones: `vMAJOR.MINOR.PATCH-phaseN-pN` (e.g., `v1.4.0-phase6-p0`)
- Pre-release: `vMAJOR.MINOR.PATCH-rcN` (e.g., `v1.4.1-rc1`)

## Links
- Repository: (set after pushing to GitHub)
- Issue tracker: (TBD)
- Product Bible: `/app/SCN_PRODUCT_BIBLE.md`
- Closure Report: `/app/CLOSURE_REPORT_v1.4.md`
