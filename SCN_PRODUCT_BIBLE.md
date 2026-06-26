# 🔥 SCN PRODUCT BIBLE — Fire Compliance OS

**Version**: 1.4 (Phase-6 P0 closure)  
**Owner**: Securrise Solution Pvt Ltd (SSPL)  
**Document Status**: ✅ MASTER REFERENCE — supersedes all prior docs  
**Last Updated**: April 2026  
**Audience**: Engineering, Product, Compliance, Sales, Support — any incoming team taking over.

---

## TABLE OF CONTENTS

1. [Vision & Product Positioning](#1-vision--product-positioning)
2. [Business Rules](#2-business-rules)
3. [Complete Module List](#3-complete-module-list)
4. [User Roles & Permissions Matrix](#4-user-roles--permissions-matrix)
5. [User Journey per Role](#5-user-journey-per-role)
6. [Database Dictionary](#6-database-dictionary)
7. [API Catalogue](#7-api-catalogue)
8. [System Architecture Diagram](#8-system-architecture-diagram)
9. [Folder Structure & Technology Stack](#9-folder-structure--technology-stack)
10. [Third-Party Integrations](#10-third-party-integrations)
11. [Environment Variables (.env Guide)](#11-environment-variables-env-guide)
12. [Deployment Guide](#12-deployment-guide)
13. [Backup & Restore Process](#13-backup--restore-process)
14. [Disaster Recovery Plan](#14-disaster-recovery-plan)
15. [Security Architecture](#15-security-architecture)
16. [Audit Log Structure](#16-audit-log-structure)
17. [Release History (v1.0 → v1.4)](#17-release-history)
18. [Known Limitations](#18-known-limitations)
19. [Future Roadmap](#19-future-roadmap)
20. [Change Request Process](#20-change-request-process)

---

## 1. Vision & Product Positioning

### Vision
> **"Every site, every asset, under control."**  
> Fire Compliance OS is the operating system for fire safety compliance in India — eliminating manual logbooks, missed inspections, and NOC chaos.

### Mission
Become the default platform every Fire Safety Compliance Agency in India uses to manage their multi-tenant client portfolios — with absolute owner control retained by **Securrise Solution Pvt Ltd (SSPL)**.

### Product Positioning
| Dimension | Position |
|---|---|
| **Category** | Enterprise SaaS · Vertical (Fire Safety Compliance) |
| **Customer** | Indian Fire Safety Agencies + Industrial/Commercial property owners |
| **Pricing** | Prepaid wallet usage-based (per asset / inspection / user) |
| **Differentiator** | (1) SSPL Super-Admin kill switch (2) Usage-based billing (no SaaS subscription lock-in) (3) NOC-readiness scoring (4) AMC conversion engine |
| **Moat** | Owned by SSPL; multi-tenant from day 1; audit-grade trail; full India compliance (GST, DLT, NOC) |
| **Stage** | v1.4 — Production-ready, awaiting live API keys |

### Strategic Pillars
1. **Owner Control** — SSPL has absolute kill-switch, audit visibility, revenue dashboard
2. **API-First** — Every screen built on top of public REST APIs (allows future mobile/partner integrations)
3. **Revenue Engine** — Wallet model converts to recurring revenue; usage hooks naturally upsell AMC
4. **Compliance-Grade** — Every action audit-logged; GST invoices auto-generated; DLT-compliant SMS

---

## 2. Business Rules

### 🔐 SSPL Ownership Rules
| # | Rule |
|---|---|
| B-1 | Only **one** `super_admin` (SSPL) account exists — auto-seeded from `ADMIN_EMAIL`/`ADMIN_PASSWORD` env. **Never deletable**. |
| B-2 | SSPL can **kill-switch** any tenant (`license_active=false`) — instantly blocks login regardless of cookies. |
| B-3 | SSPL can view all clients' data; clients see only their own (enforced via `tenant_filter` dependency). |
| B-4 | All clients are billed via **prepaid wallet**. No subscription billing. |

### 💰 Wallet & Pricing Rules
| # | Rule |
|---|---|
| B-5 | Every new asset creation deducts `COST_PER_ASSET` (default ₹10). |
| B-6 | Every inspection deducts `COST_PER_INSPECTION` (default ₹5). |
| B-7 | Every new user addition deducts `COST_PER_USER` (default ₹20). |
| B-8 | When wallet balance ≤ 0 → tenant enters **read-only mode**: blocks asset/inspection/user creation. Reads always allowed. |
| B-9 | When balance < `WALLET_LOW_THRESHOLD` (default ₹500) → low-balance email + in-app + WhatsApp/SMS alert sent to client admins. |
| B-10 | Wallet recharge generates a **unique GST invoice** (`INV-YYYYMMDDHHMMSS`). 18% GST split as 9% CGST + 9% SGST. |
| B-11 | Razorpay payment verification uses **constant-time HMAC-SHA256**. Duplicate calls return `already_processed=true` — never double-credit. |

### 🛠 Operational Rules
| # | Rule |
|---|---|
| B-12 | Every asset has an auto-generated UUID + QR code. Scanning the QR opens `/app/assets/{id}`. |
| B-13 | Inspections result in `pass` or `fail`. A `fail` immediately notifies all client admins via email + in-app + WhatsApp/SMS. |
| B-14 | Maintenance tasks auto-run daily at 03:00 UTC via APScheduler. Overdue tasks marked `missed`. |
| B-15 | NOC Readiness Score = `max(0, 100 − expired_assets×8 − missed_maintenance×4 − failed_inspections×3)`. |
| B-16 | Compliance Score ≥85 = SAFE · 60–84 = WARNING · <60 = CRITICAL. |

### 🔁 Auth & Session Rules
| # | Rule |
|---|---|
| B-17 | Login: 5 failed attempts → 15-min IP+email lockout. |
| B-18 | Access token = 8 hours. Refresh token = 7 days. Both `httpOnly`, `secure`, `samesite=none`. |
| B-19 | Logout revokes both tokens (JTI added to TTL-indexed `revoked_tokens`). |
| B-20 | Password reset token = 1 hour TTL, single-use, SHA-256 hashed at rest. |
| B-21 | Password reset request **never reveals** whether the email exists. |

---

## 3. Complete Module List

### Functional Modules (16 backend routers)
| Module | Router | Purpose |
|---|---|---|
| **Auth** | `auth.py` | Login, logout, refresh, password reset, profile |
| **Admin (SSPL)** | `admin.py` | Client CRUD, kill-switch, revenue dashboard, manual wallet recharge, audit logs |
| **Assets/Operations** | `assets.py` | Sites, assets, inspections, incidents, maintenance |
| **Asset Master Catalog** | `asset_master.py` | Pre-defined fire equipment templates |
| **Compliance Engine** | `compliance.py` | NOC checklist, compliance score, risk map, AMC opportunities |
| **AMC Engine** | `amc.py` | Book annual maintenance contract |
| **QR System** | `qr.py` | Asset QR code generation + PDF sheets |
| **Wallet** | `wallet.py` | Balance, transactions, pricing |
| **Payments** | `payments.py` | Razorpay order/verify/webhook + GST invoice |
| **Documents (Vault)** | `documents.py` | Upload/download via R2 with local fallback |
| **Reports** | `reports.py` | PDF compliance reports |
| **Notifications** | `notifications.py` | In-app notification center |
| **Onboarding** | `onboarding.py` | Progress tracker for new tenants |
| **Support** | `support.py` | Tenant ↔ SSPL ticketing |
| **Users** | `users.py` | User CRUD, phone update |
| **Demo Mode** | `demo.py` | One-click sample tenant + reset |

### Core Services (`/app/backend/core/`)
| Service | File | Purpose |
|---|---|---|
| **Config** | `config.py` | All env vars, no hardcoded defaults |
| **DB** | `db.py` | Motor client + index setup |
| **Security** | `security.py` | JWT, bcrypt, token revocation |
| **Deps** | `deps.py` | `get_current_user`, `require_role`, `tenant_filter` |
| **Wallet Service** | `wallet_service.py` | `charge()` / `credit()` with alerts |
| **Emailer** | `emailer.py` | Resend → SMTP → log cascade + templates |
| **Messaging** | `messaging.py` | WhatsApp → MSG91 SMS fallback |
| **Storage** | `storage.py` | R2 → local disk fallback |
| **Notify** | `notify.py` | In-app notifications + audit log |
| **Scheduler** | `scheduler.py` | APScheduler daily cron at 03:00 UTC |

### Frontend Pages (`/app/frontend/src/pages/`)
| Page | Route | Audience |
|---|---|---|
| Landing | `/` | Public |
| Login | `/login` | Public |
| Forgot Password | `/forgot-password` | Public |
| Reset Password | `/reset-password?token=` | Public |
| Terms | `/terms` | Public |
| SSPL Dashboard | `/app/sspl` | super_admin |
| Clients Admin | `/app/clients` | super_admin |
| Client Dashboard | `/app/dashboard` | tenant users |
| Assets list | `/app/assets` | tenant users |
| Asset Detail | `/app/assets/:id` | tenant users |
| QR Scan | `/app/scan` | technician/inspector |
| Inspections | `/app/inspections` | tenant users |
| Maintenance | `/app/maintenance` | tenant users |
| Incidents | `/app/incidents` | tenant users |
| Compliance Center | `/app/compliance` | client_admin/fire_officer |
| Risk Map | `/app/risk-map` | tenant users |
| Wallet | `/app/wallet` | client_admin |
| Documents | `/app/documents` | tenant users |
| Sites | `/app/sites` | client_admin |
| Users | `/app/users` | super_admin / client_admin |
| Support | `/app/support` | tenant users |
| Help Center | `/app/help` | all |
| Notifications | `/app/notifications` | all |

---

## 4. User Roles & Permissions Matrix

| Action | super_admin (SSPL) | client_admin | fire_officer | technician | inspector |
|---|:-:|:-:|:-:|:-:|:-:|
| **Cross-tenant view** | ✅ All clients | ❌ | ❌ | ❌ | ❌ |
| **Create/edit/suspend tenant** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Kill-switch tenant** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Manual wallet recharge (SSPL)** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Self-serve recharge (Razorpay)** | ❌ | ✅ | ❌ | ❌ | ❌ |
| **View own wallet + GST invoice** | ❌ (always 0) | ✅ | ✅ (read) | ❌ | ❌ |
| **Add sites** | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Add assets** | ❌ | ✅ | ✅ | ❌ | ❌ |
| **Submit inspection** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Create incident** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Schedule maintenance** | ❌ | ✅ | ✅ | ❌ | ❌ |
| **Mark maintenance done** | ❌ | ✅ | ✅ | ✅ | ❌ |
| **Add user (own tenant)** | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Add user (any tenant)** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Upload document** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Update NOC checklist** | ❌ | ✅ | ✅ | ❌ | ❌ |
| **Book AMC** | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Generate PDF report** | ❌ | ✅ | ✅ | ❌ | ❌ |
| **Audit log access** | ✅ Full | ❌ | ❌ | ❌ | ❌ |
| **Create support ticket** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Respond to support tickets** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Scan QR (camera)** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Password reset (self)** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Update own phone (for WhatsApp alerts)** | ✅ | ✅ | ✅ | ✅ | ✅ |

**Enforcement**: `require_role(*roles)` dependency in FastAPI + `tenant_filter()` for data scoping. Frontend uses `useAuth()` for UI-level gates (defense-in-depth).

---

## 5. User Journey per Role

### 👑 SSPL Super Admin
1. **Login** at `/login` → lands on `/app/sspl`
2. **Revenue Dashboard** — sees total clients, active/suspended, total wallet balance, total revenue (sum of all credits), total usage, recent transactions, **risk-ranked client list** by compliance score
3. **Manage Clients** → `/app/clients`
   - Create new tenant (name, industry, GSTIN, plan, admin email+password)
   - Toggle license (kill-switch)
   - Edit subscription plan & feature flags
4. **Manual Recharge** — recharge any client's wallet from admin panel (creates GST invoice)
5. **Audit Log** — `/api/admin/audit` — read-only view of every sensitive action
6. **Support Inbox** — respond to tenant tickets

### 🏢 Client Admin (e.g., Acme Industries)
1. **Login** → `/app/dashboard`
2. **Onboarding tracker** — shows pending setup (add site, add asset, invite team)
3. **Add sites** → `/app/sites` — each site = physical location
4. **Add assets** → `/app/assets` — extinguisher, hydrant, alarm, etc. (₹10 each from wallet)
5. **Invite team** → `/app/users` — fire_officer / technician / inspector (₹20 each)
6. **Recharge wallet** → `/app/wallet` → Razorpay Checkout → GST invoice auto-downloaded
7. **View Compliance Score** → `/app/compliance` — NOC readiness per site
8. **Book AMC** → `/app/compliance` — converts expiring assets into AMC bookings
9. **Generate PDF Report** → `/api/reports/compliance` — for client audits

### 🚒 Fire Officer
1. **Login** → `/app/dashboard`
2. Reviews **pending inspections** + **failed inspections** queue
3. **Approves NOC checklist items** → `/app/compliance`
4. Receives **WhatsApp alert** on inspection failures
5. Can **mark maintenance done** + **add assets** but cannot recharge wallet

### 🔧 Technician
1. **Login** on phone (PWA) → installs as home-screen app
2. Tap **"Scan QR"** → `/app/scan` → opens rear camera
3. Lands on asset page → taps **"Quick-Pass Inspection"** (1-tap pass) OR opens full checklist
4. Submits inspection → wallet auto-debits ₹5
5. Marks maintenance tasks complete

### 🔍 Inspector
- Same as technician but typically only does inspections (read-only on maintenance)

### 🎁 Demo User
1. On `/login` → clicks **"Try Demo (no signup)"**
2. Backend `POST /api/demo/login` auto-creates sample tenant "Demo Industries (Sample)" with seeded assets/inspections/wallet
3. User explores entire flow without registering
4. `POST /api/demo/reset` wipes & re-seeds demo data

---

## 6. Database Dictionary

**Engine**: MongoDB 6.x · Database: `fire_compliance_os` · Driver: Motor (async)

### Core Collections
| Collection | Key Fields | Indexes | Notes |
|---|---|---|---|
| **users** | `id`, `email` (unique), `password_hash` (bcrypt), `name`, `role`, `phone`, `client_id`, `site_ids[]`, `created_at`, `password_updated_at` | `email` unique | super_admin has `client_id=null` |
| **clients** | `id`, `name`, `industry`, `gstin`, `subscription_plan`, `license_active`, `wallet_balance`, `features{}`, `created_at` | — | One per tenant |
| **sites** | `id`, `client_id`, `name`, `address`, `city`, `state` | `client_id` | |
| **assets** | `id`, `client_id`, `site_id`, `name`, `category`, `serial_number`, `status`, `qr_code`, `expiry_date`, `last_inspected`, `created_at` | `client_id` | status: active/faulty/expired |
| **inspections** | `id`, `client_id`, `asset_id`, `inspector_id`, `inspector_name`, `overall_result` (pass/fail), `checklist[]`, `notes`, `created_at` | `(client_id, asset_id)` | |
| **maintenance_tasks** | `id`, `client_id`, `asset_id`, `scheduled_date`, `status` (scheduled/done/missed), `assignee_id` | `(client_id, scheduled_date)` | |
| **incidents** | `id`, `client_id`, `site_id`, `severity`, `summary`, `reported_by`, `created_at` | `client_id` | |
| **noc_checklist** | `id`, `client_id`, `site_id`, `item`, `completed`, `updated_at` | `client_id` | |
| **documents** | `id`, `client_id`, `title`, `doc_type`, `site_id`, `expires_on`, `storage_provider` (r2/local), `storage_key`, `storage_location`, `file_name`, `file_size`, `content_type`, `uploaded_by`, `created_at` | `client_id` | |
| **notifications** | `id`, `user_id`, `kind`, `severity`, `title`, `body`, `meta{}`, `read`, `created_at` | `(user_id, created_at)` | |
| **wallet_transactions** | `id`, `client_id`, `type` (credit/usage), `amount`, `balance_after`, `reason`, `reference`, `gst_invoice_no`, `gst_amount`, `created_at` | `(client_id, created_at)`, `gst_invoice_no` | |
| **payment_orders** | `id`, `order_id` (unique Razorpay), `client_id`, `user_id`, `receipt`, `amount_inr`, `amount_paise`, `status` (created/paid/signature_failed), `payment_id`, `invoice_no`, `finalized_via`, `paid_at`, `created_at` | `order_id` unique, `(client_id, created_at)` | |
| **support_tickets** | `id`, `client_id`, `subject`, `body`, `status`, `created_by`, `created_at` | — | Collection name in code: `support_requests` |
| **scheduler_runs** | `key` (e.g. `daily-2026-04-22`), `at` | — | APScheduler idempotency guard |
| **asset_master_catalog** | — (NOT a collection — static Python list in `routers/asset_master.py`) | — | Reference catalogue only |

### Auth & Audit Collections
| Collection | Key Fields | Indexes | Notes |
|---|---|---|---|
| **audit_logs** | `id`, `user_id`, `user_email`, `client_id`, `action`, `target`, `details{}`, `created_at` | — | Every sensitive action |
| **login_attempts** | `identifier` (ip:email), `count`, `locked_until`, `updated_at` | `identifier` | |
| **revoked_tokens** | `jti`, `expires_at` | `expires_at` TTL | Auto-purge expired |
| **password_reset_tokens** | `id`, `user_id`, `email`, `token_hash` (SHA-256), `expires_at`, `used`, `used_at`, `created_at` | `expires_at` TTL | Single-use |
| **email_log** | `id`, `to[]`, `subject`, `provider` (resend/smtp/log_only), `provider_id`, `success`, `created_at` | `created_at` | |
| **messaging_log** | `id`, `kind` (whatsapp/sms), `to`, `event`, `provider`, `success`, `detail`, `notification_id`, `created_at` | `created_at`, `(event, success)` | |

### Standard Fields (every doc)
- `id` — UUID string (we **never** expose `_id`)
- `created_at` — ISO 8601 UTC string
- `client_id` — tenant scope (except global collections)

### Field Conventions
| Pattern | Rule |
|---|---|
| `_id` | **Always excluded** in projections (`{"_id": 0}`) |
| ObjectId | **Never stored**; we use UUID strings |
| Timestamps | Stored as ISO strings (not BSON dates) for portability |
| Money | Stored as float INR; converted to paise only at Razorpay API boundary |
| Phone | Stored as E.164 `+91XXXXXXXXXX`; normalized at write time |

---

## 7. API Catalogue

All endpoints prefixed with `/api`. Authentication via `access_token` httpOnly cookie OR `Authorization: Bearer <token>`.

### 🔐 Auth (`/auth`)
| Method | Endpoint | Role | Purpose |
|---|---|---|---|
| POST | `/auth/login` | public | Email + password → cookies |
| POST | `/auth/logout` | any | Revoke tokens |
| GET | `/auth/me` | any | Current user profile |
| POST | `/auth/refresh` | any | Rotate access token |
| POST | `/auth/password-reset/request` | public | Send reset email (non-enumerating) |
| POST | `/auth/password-reset/confirm` | public | Set new password using token |

### 👑 Admin (`/admin` — super_admin only)
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/admin/clients` | List all tenants |
| POST | `/admin/clients` | Create tenant + admin user |
| PATCH | `/admin/clients/{cid}` | Update tenant |
| POST | `/admin/clients/{cid}/kill-switch` | Toggle license |
| GET | `/admin/overview` | Revenue dashboard data |
| POST | `/admin/wallet/recharge` | Manual recharge (GST invoice) |
| GET | `/admin/audit` | Audit log |

### 🏭 Operations
| Method | Endpoint | Purpose |
|---|---|---|
| GET/POST | `/sites` | List/create sites |
| GET/POST | `/assets` | List/create assets (₹10 charge) |
| GET | `/assets/{aid}` | Asset detail |
| DELETE | `/assets/{aid}` | Soft delete |
| GET/POST | `/inspections` | List/create (₹5 charge) |
| GET/POST/PATCH | `/maintenance[/{tid}]` | Task lifecycle |
| GET/POST | `/incidents` | Incident log |

### ✅ Compliance (`/compliance`)
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/compliance/score` | Real-time score + status |
| GET | `/compliance/noc` | NOC checklist by site |
| PATCH | `/compliance/noc/{item_id}` | Tick NOC item |
| GET | `/compliance/amc-opportunities` | Expiring assets eligible for AMC |
| GET | `/compliance/risk-map` | Geo-tagged risk data |

### 💼 AMC (`/amc`)
| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/amc/book-service` | Convert expiring asset to AMC booking |

### 📷 QR (`/qr`)
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/qr/asset/{aid}` | Single QR PNG |
| POST | `/qr/sheet` | Bulk PDF sheet |

### 💰 Wallet (`/wallet`)
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/wallet` | Balance + ledger + pricing |

### 💳 Payments (`/payments`)
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/payments/config` | Public Razorpay key |
| POST | `/payments/order` | Create Razorpay order |
| POST | `/payments/verify` | HMAC verify + credit wallet |
| POST | `/payments/webhook` | Async safety net |
| GET | `/payments/invoice/{invoice_no}` | GST invoice PDF |
| GET | `/payments/orders` | Tenant order history |
| GET | `/payments/admin/orders` | All orders (super_admin) |

### 📄 Documents (`/documents`)
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/documents` | List tenant docs |
| POST | `/documents/upload` | Multipart upload → R2/local |
| POST | `/documents` | Metadata-only entry |
| GET | `/documents/file/{doc_id}` | Download (R2 presigned redirect or stream) |

### 📊 Reports (`/reports`)
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/reports/compliance` | Multi-page PDF compliance report |

### 🔔 Notifications (`/notifications`)
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/notifications` | List my notifications |
| POST | `/notifications/{nid}/read` | Mark one read |
| POST | `/notifications/read-all` | Mark all read |

### 🎁 Demo (`/demo`)
| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/demo/login` | Auto-create + login |
| POST | `/demo/reset` | Wipe + re-seed |

### 👥 Users (`/users`)
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/users` | List (tenant-scoped) |
| POST | `/users` | Create (₹20 charge) |
| PATCH | `/users/{uid}` | Update name/phone/role |
| POST | `/users/me/phone` | Update own phone |

### 🎫 Support (`/support-requests`)
| Method | Endpoint | Purpose |
|---|---|---|
| GET/POST | `/support-requests` | List/create tickets |
| PATCH | `/support-requests/{rid}` | Respond / close |

### 🚦 Onboarding (`/onboarding`)
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/onboarding/progress` | Setup checklist progress |

### 📚 Asset Master (`/asset-master`)
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/asset-master` | Pre-defined equipment catalog |

**~60 endpoints total**.

---

## 8. System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          USERS                                          │
│  SSPL Admin · Client Admin · Fire Officer · Technician · Inspector      │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │ HTTPS (cookies)
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    KUBERNETES INGRESS / NGINX                           │
│  Routes:  /api/* → :8001          /* → :3000 (React build)              │
└────────────────┬─────────────────────────────┬──────────────────────────┘
                 │                             │
                 ▼                             ▼
┌──────────────────────────┐      ┌──────────────────────────────────────┐
│  REACT 19 PWA            │      │  FASTAPI BACKEND (uvicorn :8001)     │
│  · Tailwind + shadcn     │      │  ┌────────────────────────────────┐  │
│  · Service Worker        │      │  │ 16 Routers (/api/*)            │  │
│  · html5-qrcode          │      │  │ ┌──────┬─────────┬───────────┐ │  │
│  · axios + AuthContext   │      │  │ │ Auth │ Wallet  │ Payments  │ │  │
│  · sonner toasts         │      │  │ │ Admin│ Assets  │ Compliance│ │  │
│  · Razorpay Checkout JS  │      │  │ │ AMC  │ QR      │ Reports   │ │  │
│                          │      │  │ │ Docs │ Notif.  │ Onboard.  │ │  │
│  pages/ · components/ui  │      │  │ │ Users│ Support │ Demo / AM │ │  │
│                          │      │  │ └──────┴─────────┴───────────┘ │  │
│                          │      │  └────────────────────────────────┘  │
│                          │      │  ┌────────────────────────────────┐  │
│                          │      │  │ Core Services                  │  │
│                          │      │  │  · JWT + bcrypt + revocation   │  │
│                          │      │  │  · tenant_filter dependency    │  │
│                          │      │  │  · wallet_service (charge/credit)│ │
│                          │      │  │  · emailer (Resend→SMTP→log)   │  │
│                          │      │  │  · messaging (WA→MSG91→skip)   │  │
│                          │      │  │  · storage (R2→local)          │  │
│                          │      │  │  · scheduler (APScheduler 03:00 UTC)│
│                          │      │  └────────────────────────────────┘  │
└──────────────────────────┘      └─────────────┬────────────────────────┘
                                                │
            ┌───────────────────────────────────┼──────────────────────────────┐
            │                                   │                              │
            ▼                                   ▼                              ▼
┌────────────────────┐         ┌──────────────────────────┐    ┌─────────────────────┐
│  MONGODB           │         │   THIRD-PARTY APIs       │    │   OBJECT STORAGE    │
│  · 20 collections  │         │  · Razorpay (payments)   │    │  · Cloudflare R2    │
│  · TTL indexes     │         │  · Resend (email)        │    │  · S3 fallback ok   │
│  · Multi-tenant    │         │  · SMTP (fallback)       │    │  · Local disk f/b   │
│    via client_id   │         │  · Meta WhatsApp Cloud   │    │                     │
│                    │         │  · MSG91 SMS (DLT India) │    │                     │
└────────────────────┘         └──────────────────────────┘    └─────────────────────┘
```

### Request flow example: Wallet Recharge
```
[Client Admin] → Wallet page → "Recharge ₹5000"
   POST /api/payments/order
   → backend creates Razorpay order, stores intent in payment_orders
   → returns {order_id, key_id, amount}
[Frontend] → Razorpay Checkout opens
[User pays with test card]
[Razorpay] → callback handler(razorpay_payment_id, razorpay_signature)
   POST /api/payments/verify
   → backend HMAC-SHA256 verifies signature (constant-time)
   → idempotent wallet credit (payment_orders.status == "paid" check)
   → wallet_transactions row created with gst_invoice_no
[Backend] returns {ok, balance, invoice_no}
[Frontend] auto-opens /api/payments/invoice/{invoice_no} → GST PDF downloaded
[Async: Razorpay webhook → /payments/webhook] (idempotent safety net)
```

---

## 9. Folder Structure & Technology Stack

### Folder Structure
```
/app/
├── backend/
│   ├── server.py                 # FastAPI entry, mounts routers, CORS, startup
│   ├── seed.py                   # Auto-seeds SuperAdmin + demo tenant
│   ├── requirements.txt          # pip freeze output
│   ├── .env                      # ⚠️ ALL secrets (gitignored)
│   ├── core/
│   │   ├── config.py             # env vars (no hardcoded defaults)
│   │   ├── db.py                 # Motor client + indexes
│   │   ├── deps.py               # auth, RBAC, tenant scoping
│   │   ├── security.py           # JWT, bcrypt, revocation
│   │   ├── notify.py             # in-app notifications + audit
│   │   ├── emailer.py            # Resend → SMTP → log
│   │   ├── messaging.py          # WhatsApp → MSG91 SMS
│   │   ├── storage.py            # R2 → local disk
│   │   ├── wallet_service.py     # charge() / credit()
│   │   └── scheduler.py          # APScheduler daily cron
│   ├── routers/
│   │   ├── auth.py admin.py assets.py amc.py asset_master.py
│   │   ├── compliance.py demo.py documents.py notifications.py
│   │   ├── onboarding.py payments.py qr.py reports.py
│   │   ├── support.py users.py wallet.py
│   ├── tests/
│   │   ├── test_payments_flow.py # Razorpay e2e self-test
│   │   ├── test_phase3.py        # AMC + scheduler regression
│   │   ├── test_stabilization.py
│   │   └── backend_test.py
│   └── uploads/                  # local storage fallback (gitignored)
│
├── frontend/
│   ├── package.json              # yarn deps
│   ├── .env                      # REACT_APP_BACKEND_URL
│   ├── public/
│   │   ├── manifest.json         # PWA manifest
│   │   ├── service-worker.js     # offline cache
│   │   ├── icon.svg              # PWA icon
│   │   └── index.html
│   └── src/
│       ├── App.js                # router + AuthProvider
│       ├── index.js / index.css / App.css
│       ├── context/AuthContext.js
│       ├── lib/
│       │   ├── api.js            # axios http client
│       │   ├── i18n.js           # EN/HI translations
│       │   └── helpContent.js    # Help Center copy
│       ├── components/
│       │   ├── AppShell.jsx      # sidebar + drawer + topbar
│       │   ├── InstallPrompt.jsx
│       │   ├── NeedHelpFab.jsx
│       │   ├── ui-kit.jsx        # PageHeader, Panel, StatusPill, Empty
│       │   └── ui/               # shadcn primitives (60+)
│       └── pages/ (23 pages — see Module List)
│
├── memory/
│   ├── PRD.md                    # this file's parent
│   └── test_credentials.md       # test logins
│
├── test_reports/                 # iteration_1.json … iteration_7.json
├── test_result.md
└── SCN_PRODUCT_BIBLE.md          # ← this document
```

### Technology Stack
| Layer | Tech | Version | Notes |
|---|---|---|---|
| Frontend framework | React | 19 | Hooks + Context |
| Build | CRA + craco | — | yarn only |
| Styling | Tailwind CSS | 3.x | |
| UI primitives | shadcn/ui + Radix UI | latest | |
| Icons | lucide-react | latest | No emojis |
| HTTP | axios | latest | `withCredentials: true` |
| Toast | sonner | latest | |
| Charts | recharts | latest | |
| QR Scan | html5-qrcode | latest | |
| Payments SDK | Razorpay Checkout JS | v1 | CDN-loaded |
| Backend lang | Python | 3.11 | |
| Backend framework | FastAPI | 0.110 | async |
| ASGI | uvicorn | 0.25 | |
| Process mgr | supervisor | — | hot reload |
| DB driver | Motor | 3.3 | async MongoDB |
| Auth | PyJWT + bcrypt | 2.10 / 4.1 | |
| Validation | Pydantic | 2.6 | |
| Scheduler | APScheduler | latest | in-process |
| PDF | ReportLab | latest | invoices + reports |
| Image | Pillow | latest | QR rendering |
| QR gen | qrcode | latest | |
| Email | resend SDK + smtplib | 2.x / stdlib | |
| Payments | razorpay SDK | 1.4.2 | + `setuptools<81` pin |
| Object storage | boto3 | 1.34+ | R2 (S3-compat) |
| HTTP client | httpx | latest | WhatsApp + MSG91 |
| Database | MongoDB | 6.x+ | Atlas or self-hosted |

---

## 10. Third-Party Integrations

| # | Provider | Type | Status | Required Keys | Failure Mode |
|---|---|---|:-:|---|---|
| 1 | **Razorpay** | Payments | code complete | `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`, `RAZORPAY_WEBHOOK_SECRET` | `/payments/order` returns 503 if keys missing |
| 2 | **Resend** | Email (primary) | code complete | `RESEND_API_KEY`, `EMAIL_FROM` | Auto-falls back to SMTP |
| 3 | **SMTP** | Email (fallback) | code complete | `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_USE_TLS` | Falls back to log-only |
| 4 | **Meta WhatsApp Cloud API** | Messaging (primary) | code complete | `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_API_VERSION=v20.0`, 4 template names | Falls back to MSG91 SMS |
| 5 | **MSG91 Flow API v5** | SMS (fallback) | code complete | `MSG91_AUTHKEY`, `MSG91_SENDER_ID`, 4 DLT template IDs | Records in messaging_log as skipped |
| 6 | **Cloudflare R2** | Object Storage | code complete | `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET`, `R2_PUBLIC_BASE_URL`, `R2_REGION=auto` | Falls back to local disk |

### Integration verification
- **Razorpay**: Run `/root/.venv/bin/python /app/backend/tests/test_payments_flow.py` — full HMAC + idempotency + invoice cycle (must temporarily set dummy keys to .env, runs in <2s)
- **Resend**: After setting `RESEND_API_KEY`, trigger any email-generating action and inspect `db.email_log` for `provider="resend"` + `success=true`
- **WhatsApp**: After keys + 4 approved templates, run a low-balance scenario; check `db.messaging_log` for `provider="meta"` + `success=true`
- **MSG91**: Cut WhatsApp keys temporarily → same scenario → `provider="msg91"` should record
- **R2**: After keys, upload doc → `db.documents.storage_provider="r2"` + presigned URL works

### Template requirements (action before going live)
- 4 WhatsApp templates pre-approved in Meta Business Manager:
  - `inspection_failure_alert` (asset_name, inspector, notes)
  - `wallet_low_alert` (client_name, balance, threshold)
  - `wallet_exhausted_alert` (client_name, balance)
  - `maintenance_scheduled_alert` (asset_name, due_date)
- 4 MSG91 SMS templates DLT-registered (same names + India-compliance text)

---

## 11. Environment Variables (.env Guide)

### `/app/backend/.env` — MASTER
```bash
# ═══ CORE ═══════════════════════════════════════════════════
MONGO_URL="mongodb://localhost:27017"           # or Atlas SRV URL
DB_NAME="fire_compliance_os"
CORS_ORIGINS="*"                                # restrict in prod
JWT_SECRET="<64-char-hex from openssl rand -hex 32>"
ADMIN_EMAIL="superadmin@sspl.in"
ADMIN_PASSWORD="<strong password>"
FRONTEND_URL="https://yourdomain.com"           # exact prod URL (CORS depends)

# ═══ PRICING / BUSINESS ════════════════════════════════════
COST_PER_ASSET="10"
COST_PER_INSPECTION="5"
COST_PER_USER="20"
WALLET_LOW_THRESHOLD="500"
GST_RATE="18"

# ═══ EMAIL ═════════════════════════════════════════════════
RESEND_API_KEY=""                               # re_xxx
EMAIL_FROM="Fire Compliance OS <noreply@yourdomain.com>"
SMTP_HOST=""                                    # optional SMTP fallback
SMTP_PORT="587"
SMTP_USER=""
SMTP_PASSWORD=""
SMTP_USE_TLS="true"
PASSWORD_RESET_TTL_HOURS="1"

# ═══ RAZORPAY ══════════════════════════════════════════════
RAZORPAY_KEY_ID=""                              # rzp_test_xxx or rzp_live_xxx
RAZORPAY_KEY_SECRET=""
RAZORPAY_WEBHOOK_SECRET=""                      # any strong string ≥16 chars

# ═══ GST INVOICE METADATA (editable placeholders) ══════════
SSPL_GSTIN="27AAAPS1234Z1ZB"                    # replace with real
SSPL_COMPANY_NAME="Securrise Solution Pvt Ltd"
SSPL_ADDRESS="<registered address>"
SSPL_STATE_CODE="27"                            # Maharashtra=27
SSPL_PAN="AAAPS1234Z"
SSPL_HSN_CODE="9983"                            # SAC for support services

# ═══ WHATSAPP (Meta Cloud API) ═════════════════════════════
WHATSAPP_PHONE_NUMBER_ID=""
WHATSAPP_ACCESS_TOKEN=""
WHATSAPP_API_VERSION="v20.0"
WHATSAPP_TPL_LANG="en"
WHATSAPP_TPL_INSPECTION_FAIL="inspection_failure_alert"
WHATSAPP_TPL_LOW_WALLET="wallet_low_alert"
WHATSAPP_TPL_WALLET_EXHAUSTED="wallet_exhausted_alert"
WHATSAPP_TPL_MAINTENANCE="maintenance_scheduled_alert"

# ═══ MSG91 SMS (DLT India) ═════════════════════════════════
MSG91_AUTHKEY=""
MSG91_SENDER_ID=""                              # 6-char DLT header
MSG91_TPL_INSPECTION_FAIL=""                    # DLT template ID
MSG91_TPL_LOW_WALLET=""
MSG91_TPL_WALLET_EXHAUSTED=""
MSG91_TPL_MAINTENANCE=""

# ═══ CLOUDFLARE R2 ═════════════════════════════════════════
R2_ACCOUNT_ID=""
R2_ACCESS_KEY_ID=""
R2_SECRET_ACCESS_KEY=""
R2_BUCKET=""
R2_PUBLIC_BASE_URL=""                           # for public read URLs (optional)
R2_REGION="auto"
MAX_UPLOAD_MB="25"

# ═══ STORAGE FALLBACK ══════════════════════════════════════
UPLOAD_DIR="/app/backend/uploads"
```

### `/app/frontend/.env`
```bash
REACT_APP_BACKEND_URL="https://yourdomain.com"  # NO trailing slash, NO /api suffix
```

### ⚠️ Critical rules
1. **NO comments inside .env** in production (some parsers fail)
2. **NEVER commit .env** to git
3. **Never delete keys** — set to empty `""` if not used
4. After editing `.env`: `sudo supervisorctl restart backend`

---

## 12. Deployment Guide

### Option A — Emergent Platform (recommended)
1. Click **Deploy** in chat header
2. Configure custom domain in Emergent settings → CNAME points to the assigned subdomain
3. Add `.env` keys via Emergent's secrets manager UI
4. Click Deploy → live in <5 min

### Option B — Self-host (Ubuntu 22.04+)

#### Prerequisites
```bash
sudo apt update && sudo apt install -y python3.11 python3.11-venv nodejs npm nginx certbot mongodb-clients
sudo npm install -g yarn
```

#### Setup MongoDB
- **Recommended**: MongoDB Atlas (free M0 tier ok for pilot)
- **Self-host**: install MongoDB 6.x, enable auth, create user

#### App setup
```bash
sudo mkdir -p /opt/fireos && cd /opt/fireos
git clone <your-repo> .

# Backend
cd app/backend
python3.11 -m venv venv && source venv/bin/activate
pip install --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/ -r requirements.txt
cp .env.example .env && nano .env            # fill all secrets

# Frontend
cd ../frontend
cp .env.example .env && nano .env            # set REACT_APP_BACKEND_URL=https://yourdomain.com
yarn install
yarn build                                    # produces frontend/build
```

#### Supervisor config (`/etc/supervisor/conf.d/fireos.conf`)
```ini
[program:fireos-backend]
command=/opt/fireos/app/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001 --workers 2
directory=/opt/fireos/app/backend
autostart=true
autorestart=true
stderr_logfile=/var/log/fireos/backend.err.log
stdout_logfile=/var/log/fireos/backend.out.log
environment=PATH="/opt/fireos/app/backend/venv/bin"
```
```bash
sudo mkdir -p /var/log/fireos
sudo supervisorctl reread && sudo supervisorctl update
```

#### Nginx (`/etc/nginx/sites-available/fireos`)
```nginx
server {
    server_name yourdomain.com;
    client_max_body_size 30M;

    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }

    location / {
        root /opt/fireos/app/frontend/build;
        try_files $uri /index.html;
        add_header Cache-Control "public, max-age=3600";
    }
}
```
```bash
sudo ln -s /etc/nginx/sites-available/fireos /etc/nginx/sites-enabled/
sudo certbot --nginx -d yourdomain.com
sudo systemctl reload nginx
```

#### Razorpay webhook (after deploy)
- Razorpay Dashboard → Settings → Webhooks → Add
- URL: `https://yourdomain.com/api/payments/webhook`
- Secret: same as `RAZORPAY_WEBHOOK_SECRET`
- Events: ✅ `payment.captured` ✅ `order.paid`

#### Smoke test post-deploy
```bash
curl https://yourdomain.com/api/                                # → version
curl https://yourdomain.com/api/payments/config                 # → configured:true
curl -X POST https://yourdomain.com/api/auth/login -H "Content-Type: application/json" \
     -d '{"email":"superadmin@sspl.in","password":"<your password>"}'  # → access_token
```

---

## 13. Backup & Restore Process

### MongoDB Backup
```bash
# Daily automated backup (cron @ 02:30 IST)
0 21 * * * mongodump --uri="$MONGO_URL" --db=fire_compliance_os \
  --gzip --archive=/backups/fireos-$(date +\%Y\%m\%d).gz

# Retention: keep 30 daily + 12 monthly
find /backups/ -name "fireos-*.gz" -mtime +30 -delete
```

### MongoDB Restore
```bash
mongorestore --uri="$MONGO_URL" --db=fire_compliance_os \
  --gzip --archive=/backups/fireos-20260422.gz --drop
```

### R2 Backup
- R2 has built-in 99.999999999% durability
- Optional: enable **R2 → S3 replication** for cross-region redundancy
- For local-disk uploads (dev fallback): `rsync /app/backend/uploads /backups/uploads/` daily

### Config Backup
- `.env` files — store in 1Password / Vault (rotate quarterly)
- Repo (`/app/`) — push to private GitHub via Emergent's "Save to GitHub"

### Audit Log Backup
- `audit_logs` collection MUST be backed up minimum monthly (compliance requirement)
- Archive to cold storage (R2 Glacier-equivalent) after 1 year

---

## 14. Disaster Recovery Plan

### Recovery Targets
| Metric | Target |
|---|---|
| RTO (Recovery Time Objective) | < 4 hours |
| RPO (Recovery Point Objective) | < 24 hours (daily backup) |

### Scenarios

#### 1. Backend Server Down
- **Detect**: Uptime monitoring (UptimeRobot/PingDom) on `/api/`
- **Recover**: `sudo supervisorctl restart backend` (1 min)
- **Escalate**: If supervisor fails → spin up new VM, restore from infra-as-code

#### 2. MongoDB Failure
- **Atlas**: auto-failover (3-node replica set) — no manual action
- **Self-hosted**:
  ```bash
  # On standby node:
  mongorestore --uri="mongodb://..." --gzip --archive=/backups/latest.gz
  # Update MONGO_URL in .env, restart backend
  ```

#### 3. Razorpay Outage
- Recharge UI shows error; users redirected to "Contact SSPL for manual recharge"
- SSPL uses `/admin/wallet/recharge` to credit manually (full audit + GST invoice still generated)

#### 4. Email Provider (Resend) Down
- SMTP fallback auto-activates if `SMTP_HOST` set
- Else: log-only mode — review `db.email_log` for missed sends, resend manually

#### 5. WhatsApp API Outage
- MSG91 SMS auto-fires
- In-app notifications + email continue normally

#### 6. R2 Outage
- Falls back to local disk (auto)
- New uploads stored locally; existing R2 docs unreachable until R2 returns
- Recovery: when R2 returns, run migration script to push local docs

#### 7. Full Region Disaster
- Restore from offsite MongoDB backup → new region
- Restore R2 (already multi-region) or restore from replicated bucket
- Update DNS A/CNAME to point to new infrastructure
- ETA: 4 hours with prepared playbook

### Drill Schedule
- Quarterly: restore backup to staging + smoke test
- Annually: full failover drill (warm standby)

---

## 15. Security Architecture

### Authentication
- Passwords hashed with **bcrypt** (12 rounds default)
- JWT tokens signed with HS256 + 64-char random `JWT_SECRET`
- Access token = 8h; Refresh token = 7d
- All tokens stored in **httpOnly + secure + samesite=none** cookies (XSS-proof)
- Token revocation list with TTL (`revoked_tokens` collection)
- Login lockout: 5 fails → 15-min IP+email lock

### Authorization (RBAC)
- 5 roles enforced via FastAPI dependency `require_role(*roles)`
- Tenant scoping via `tenant_filter()` — automatic `{client_id: user.client_id}` filter
- Super admin bypasses tenant filter (sees all)
- License check on login (suspended tenants blocked at door)

### Data Protection
- All data in transit: **HTTPS only** (cookies refuse to set on HTTP)
- All data at rest: MongoDB Atlas encrypts; self-host requires LUKS/dm-crypt
- Tenant isolation: enforced in code AND verified by 100+ regression tests
- No PII in logs (passwords/tokens explicitly redacted)

### Payment Security
- Razorpay signature verified with **`hmac.compare_digest`** (constant-time)
- Idempotent crediting prevents replay attacks
- Webhook secret independent of API secret
- Order intent stored before payment → cross-tenant attempts return 403

### File Upload Security
- 25 MB hard cap (configurable)
- Filename sanitization (`Path(filename).name`) — prevents path traversal
- Tenant-scoped object keys: `tenants/{client_id}/{doc_id}-{filename}`
- R2 presigned URLs expire in 5 minutes
- Super admin **cannot** upload tenant documents (separation of duties)

### Email Security
- SHA-256 hashed reset tokens (raw token never stored)
- Reset endpoints **non-enumerating** (same response for known/unknown emails)
- Single-use tokens, auto-expire via TTL index

### API Security
- CORS restricted via `FRONTEND_URL` env (set exactly, not `*` in prod)
- Pydantic validates every request body
- No SQL injection vector (NoSQL + parameterized queries)
- Rate limiting recommended at nginx layer (`limit_req`)

### Audit
- Every sensitive action writes to `audit_logs` with user_id + email + IP + action + target + details
- `email_log` and `messaging_log` track every external communication
- All logs immutable (append-only writes)

### Compliance
- **GDPR-ready**: user export + deletion endpoints can be added (P2)
- **GST Act 2017** compliant (CGST + SGST split, HSN/SAC, invoice numbering)
- **DLT compliance**: MSG91 templates pre-registered for India SMS
- **Meta policy**: WhatsApp templates pre-approved before use

---

## 16. Audit Log Structure

### `audit_logs` collection
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "user_email": "admin@acme.in",
  "client_id": "uuid",
  "action": "payments.verify.success",
  "target": "<resource id, e.g. client_id, asset_id, order_id>",
  "details": { "any": "json blob" },
  "created_at": "2026-04-22T03:42:11+00:00"
}
```

### Actions Logged
| Action | When |
|---|---|
| `client.create` | New tenant created |
| `client.update` | Tenant info changed |
| `client.kill_switch` | License toggled |
| `wallet.recharge` | Manual recharge by SSPL |
| `payments.order.create` | Razorpay order created |
| `payments.verify.success` | Payment verified + wallet credited |
| `user.create` | User added |
| `user.update` | User edited |
| `user.phone_update` | Phone changed |
| `inspection.create` | Inspection submitted |
| `asset.create` / `asset.delete` | Asset CRUD |
| ... (every sensitive endpoint logs) |

### `email_log` collection
- Every send attempt — successful or failed — provider + provider_id + detail

### `messaging_log` collection
- Every WhatsApp/SMS attempt — kind, provider, success, detail, event type

### Query examples
```javascript
// All actions by user
db.audit_logs.find({user_email: "admin@acme.in"}).sort({created_at: -1})

// All wallet operations on a tenant in last 30 days
db.audit_logs.find({
  client_id: "<id>",
  action: {$regex: /^wallet\./},
  created_at: {$gte: ISODate("2026-03-22")}
})

// Find failed WhatsApp deliveries
db.messaging_log.find({kind: "whatsapp", success: false}).sort({created_at: -1}).limit(50)
```

---

## 17. Release History

### v1.0 — MVP (Q4 2025)
- Multi-tenant auth, RBAC, assets, inspections, sites, basic dashboard
- 34 tests pass

### v1.0.1 — Stabilisation
- Bug fixes, token revocation, login lockout
- 52 tests

### v1.1 — Phase 2 (Q1 2026)
- Wallet system, usage-based deduction
- Read-only grace mode at zero balance
- Mocked email alerts
- Modular router refactor
- 65 tests

### v1.2 — Phase 3
- AMC Conversion Engine
- APScheduler (daily 03:00 UTC)
- One-click Demo Mode
- PDF Compliance Reports (ReportLab)
- Severity scoring
- Support tickets
- 86 tests

### v1.2.1 — Phase 4
- Asset Master Catalog
- QR PDF sheets
- Bilingual Help Center (EN/HI)
- Terms & Conditions page
- Friendly errors
- 100 tests

### v1.3 — Phase 5
- PWA: manifest, service worker, install prompt
- Mobile responsive (hamburger drawer)
- QR camera scanning (html5-qrcode)
- Quick-Pass inspection
- 100 backend + 17 Phase-5 frontend assertions

### v1.4 — Phase 6 P0 (Current — April 2026)
- **Razorpay** wallet recharge + GST invoice
- **Real email** (Resend → SMTP → log cascade)
- **WhatsApp + SMS** (Meta Cloud API + MSG91 fallback)
- **Cloudflare R2** object storage
- **Password reset** self-service
- **Phone field** on user
- **122/122 tests pass** (22 Phase-6 + 100 regression)

---

## 18. Known Limitations

### Functional
1. **Razorpay/Resend/WhatsApp/R2 keys not yet provided** — system gracefully degrades but real comms not flowing yet
2. **WhatsApp + MSG91 templates** need pre-approval (Meta + DLT) before live use
3. **GST invoice metadata** uses placeholders (`SSPL_GSTIN`, address, PAN) — update via env before going live
4. **PWA icons are SVG only** — iOS prefers PNG 192/512 (works but not optimal)
5. **QR camera requires HTTPS** + user permission (standard browser constraint)
6. **No bulk CSV import** for assets/users yet
7. **No partner portal** (white-label is deferred)
8. **No predictive AI** for asset failure (deferred)
9. **No real map tiles** on Risk Map (uses placeholder rendering)

### Technical
10. **Scheduler is in-process** — single-node only; needs externalisation (Celery/RQ) for multi-instance deploys
11. **`setuptools<81` pin** required because Razorpay SDK 1.4.2 uses deprecated `pkg_resources`
12. **No pagination** on `/assets`, `/inspections`, `/wallet/transactions` — current limit 200/500 docs (P1 fix)
13. **No CSV/Excel export** yet (P1)
14. **No financial dashboards** with MRR trends (P1)
15. **No rectification system** for wallet adjustments (P1)
16. **No partner commission tracking** (P1)
17. **Email is sync within request** — for very high-volume tenants consider Celery
18. **GST invoice doesn't yet handle inter-state CGST/IGST split** (only intra-state CGST+SGST)

### Operational
19. **No automated MongoDB backup** — operator must configure cron
20. **No status page** for users (P2)
21. **No A/B testing** infrastructure
22. **No feature flags** beyond `clients.features{}`

---

## 19. Future Roadmap

### 🔴 P1 — Phase 7 (Next 2 weeks)
| # | Feature | Effort |
|---|---|---|
| 1 | **Client Financial Dashboard** — transaction history, filters, running balance, CSV export | 2h |
| 2 | **SSPL Financial Dashboard** — MRR trend, net revenue, client wallets ranked, alerts | 3h |
| 3 | **Rectification System** — append-only wallet adjustments with audit | 1.5h |
| 4 | **Partner Commission System** — 24% acq / 6% rec + bonus slabs | 3h |
| 5 | **DB Pagination** — cursor-based on assets/inspections/transactions | 2h |
| 6 | **CSV/Excel Export** — transactions, audit, payments, inspections | 1.5h |

### 🟠 P2 — Phase 8 (Month 2)
| # | Feature | Effort |
|---|---|---|
| 7 | **PNG PWA icons** (192/512) for iOS | 0.5h |
| 8 | **Service worker update prompt** | 1h |
| 9 | **White-label PDFs** (client logo) | 2h |
| 10 | **Bulk CSV import** (assets/users/sites) | 4h |
| 11 | **GDPR endpoints** (data export + deletion) | 2h |
| 12 | **Razorpay Payment Links** (shareable links via WhatsApp) | 1.5h |
| 13 | **Real map tiles** for Risk Map (MapLibre + OSM) | 3h |
| 14 | **Inter-state IGST** support on invoices | 1h |

### 🟡 P3 — Phase 9+ (Months 3–6)
| # | Feature | Effort |
|---|---|---|
| 15 | **Predictive AI** — failure forecasting (Gemini integration) | 8h |
| 16 | **Voice-note inspections** (audio attachments, ElevenLabs TTS for accessibility) | 6h |
| 17 | **Android native app** (React Native or Capacitor wrap) | 40h |
| 18 | **White-label partner portal** (sub-tenant SSPL view) | 30h |
| 19 | **Workflow engine** (custom inspection templates per industry) | 20h |
| 20 | **AI knowledge base** (Q&A on uploaded SOPs via Claude) | 15h |
| 21 | **Real-time WebSocket dashboard** (live updates) | 12h |
| 22 | **Status page** + uptime monitoring integration | 4h |

---

## 20. Change Request Process

### Categorisation
| Type | Examples | Approver |
|---|---|---|
| **Hotfix** | Critical bug, security patch | Tech Lead — direct merge |
| **Minor enhancement** | UI tweak, copy change, new endpoint param | Tech Lead |
| **Feature** | New module, integration, role | Product Owner + Tech Lead |
| **Architecture change** | DB schema migration, new integration | Founder + Tech Lead + DBA |

### Workflow
```
┌──────────────────┐
│ 1. Request CR    │ ← User/stakeholder fills CR template
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 2. Triage        │ ← Tech Lead categorises + estimates
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 3. Approve       │ ← Per category table above
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 4. Implement     │ ← Feature branch, tests written first
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 5. Test          │ ← `testing_agent_v3_fork` for ≥2 features OR critical bug
│                  │   curl/screenshot for small fixes
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 6. Document      │ ← Update PRD.md + this Bible + CHANGELOG
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 7. Deploy        │ ← Staging → Smoke test → Production
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 8. Verify        │ ← Stakeholder UAT, monitor for 24h
└──────────────────┘
```

### CR Template
```markdown
**Title**:
**Category**: hotfix / minor / feature / architecture
**Requested by**:
**Business value**:
**Current behaviour**:
**Desired behaviour**:
**Acceptance criteria** (list 3+ testable points):
**Affected modules**:
**Rollback plan**:
**Estimated effort**:
```

### Versioning
- Major (X.0): breaking changes, schema migrations
- Minor (1.X): new modules, features
- Patch (1.4.X): bug fixes, perf, copy

### Rollback Policy
- Every release tagged in git: `v1.4.0`, `v1.4.1`, ...
- DB migrations include up + down scripts
- Emergent users: use the **"Rollback"** option (free) to revert to any checkpoint
- Self-host: `git checkout v1.3.x && supervisorctl restart backend`

---

## 📌 APPENDIX — Quick Reference Card

### Test Credentials
| Role | Email | Password |
|---|---|---|
| SSPL Super Admin | `superadmin@sspl.in` | `Sspl@12345` |
| Client Admin (Acme) | `admin@acme.in` | `Acme@12345` |
| Fire Officer | `officer@acme.in` | `Officer@123` |
| Technician | `tech@acme.in` | `Tech@12345` |
| Demo | `demo@fire-os.in` | `Demo@12345` |

### Daily Operations Commands
```bash
# Restart backend (after env change)
sudo supervisorctl restart backend

# Tail logs
tail -f /var/log/supervisor/backend.err.log

# Verify backend up
curl https://yourdomain.com/api/

# Razorpay self-test
/root/.venv/bin/python /app/backend/tests/test_payments_flow.py

# DB shell
mongosh "$MONGO_URL/fire_compliance_os"
```

### Critical Files
- `/app/backend/.env` — all secrets
- `/app/frontend/.env` — backend URL
- `/app/memory/PRD.md` — product reference
- `/app/memory/test_credentials.md` — test logins
- `/app/SCN_PRODUCT_BIBLE.md` — **this document**

---

**END OF SCN PRODUCT BIBLE v1.4**

*This document is the single source of truth. When in conflict with anything else, this wins. Update on every release.*

*© 2026 Securrise Solution Pvt Ltd. All rights reserved.*
