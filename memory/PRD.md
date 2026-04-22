# Fire Compliance OS — PRD

## Original Problem
"Fire Compliance OS" — enterprise SaaS owned by SSPL. Multi-tenant fire-safety compliance OS.

## Architecture (v1.4 — Phase 6 P0)
Backend: FastAPI + Motor + APScheduler · 16 routers · `core/` helpers (+ storage, messaging)
Frontend: React 19 + Tailwind + shadcn · responsive + PWA · html5-qrcode · recharts · reportlab
Integrations: Razorpay · Resend (+ SMTP fallback) · WhatsApp Cloud API (+ MSG91 SMS fallback) · Cloudflare R2

## Timeline
- **v1.0 MVP** → 34 tests
- **v1.0.1 stabilisation** → 52
- **v1.1 Phase-2** → 65
- **v1.2 Phase-3** → 86
- **v1.2.1 Phase-4** → 100
- **v1.3 Phase-5** (PWA) → 100 backend + 17 Phase-5 assertions
- **v1.4 Phase-6 P0** (production closure) → **122/122 (22 Phase-6 + 100 regression)**

## Phase-6 P0 Deliverables (all shipped, all tested 122/122)

### 1. Razorpay — Wallet Recharge (new router `/api/payments`)
- `POST /payments/order` → creates Razorpay order (tenant-scoped, stores intent in `payment_orders`)
- `POST /payments/verify` → HMAC-SHA256 signature verification; idempotent wallet credit (replay-safe)
- `POST /payments/webhook` → async safety net with webhook-secret HMAC verification
- `GET /payments/invoice/{invoice_no}` → GST invoice PDF (CGST+SGST split, placeholder SSPL metadata editable via env)
- `GET /payments/config` → public key_id + configured flag for frontend
- `GET /payments/orders` → tenant order history
- Frontend: `Wallet.jsx` Recharge button + Razorpay Checkout + auto invoice download + per-txn PDF link

### 2. Real Email — Layered cascade (no mocks)
- `core/emailer.py` rewritten: **Resend (primary) → SMTP (fallback) → log-only (last resort)**
- Every send records in `db.email_log` with provider + success + detail
- New template: `tpl_password_reset(name, reset_url, ttl_hours)`

### 3. WhatsApp + SMS (`core/messaging.py`)
- Meta WhatsApp Business Cloud API primary (template messages, v20.0)
- MSG91 Flow API v5 fallback (India DLT-compliant)
- Auto fallback: WhatsApp fail → SMS. Records every attempt in `db.messaging_log`.
- Phone normalization: accepts `+91…`, `91…`, `10-digit` → E.164
- Wired into: wallet_exhausted, low_wallet, inspection_failure
- `fire_and_forget` wrapper → never blocks API caller
- Phone field added to User model (`POST /users`, `PATCH /users/{id}`, `POST /users/me/phone`)

### 4. Object Storage — Cloudflare R2 (`core/storage.py`)
- S3-compatible via boto3 (already in requirements)
- Object key layout: `tenants/{client_id}/{doc_id}-{filename}` (strict tenant isolation)
- `put_bytes` / `get_stream` / `get_presigned_url` / `delete`
- `routers/documents.py` refactored to use storage layer
- Downloads use **presigned URL redirect (302)** for R2 (zero egress through app)
- Automatic fallback to local disk when R2 env not set — same API surface
- MAX_UPLOAD_MB env-driven (default 25)

### 5. Password Reset (self-service)
- `POST /auth/password-reset/request` → always 200 (no user enumeration), SHA-256 hashed token in `password_reset_tokens` with TTL auto-expiry
- `POST /auth/password-reset/confirm` → single-use, expiry validation, resets `login_attempts` lockouts
- Frontend: `/forgot-password` + `/reset-password?token=…` pages
- Link on Login: `data-testid="forgot-password-link"`
- TTL env: `PASSWORD_RESET_TTL_HOURS=1`

## Environment Variables (all read-only from env, no code hardcoding)
```
# Razorpay
RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET, RAZORPAY_WEBHOOK_SECRET

# GST invoice metadata (editable placeholders)
SSPL_GSTIN, SSPL_COMPANY_NAME, SSPL_ADDRESS, SSPL_STATE_CODE, SSPL_PAN, SSPL_HSN_CODE, GST_RATE

# Email
RESEND_API_KEY, EMAIL_FROM, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_USE_TLS
PASSWORD_RESET_TTL_HOURS

# WhatsApp (Meta Cloud API)
WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_ACCESS_TOKEN, WHATSAPP_API_VERSION, WHATSAPP_TPL_LANG
WHATSAPP_TPL_INSPECTION_FAIL, WHATSAPP_TPL_LOW_WALLET, WHATSAPP_TPL_WALLET_EXHAUSTED, WHATSAPP_TPL_MAINTENANCE

# MSG91 SMS (DLT)
MSG91_AUTHKEY, MSG91_SENDER_ID
MSG91_TPL_INSPECTION_FAIL, MSG91_TPL_LOW_WALLET, MSG91_TPL_WALLET_EXHAUSTED, MSG91_TPL_MAINTENANCE

# Cloudflare R2
R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET, R2_PUBLIC_BASE_URL, R2_REGION
MAX_UPLOAD_MB
```

## Known Limitations (v1.4)
1. All Phase-6 API keys currently blank in `.env` — user to populate
2. WhatsApp templates must be pre-approved by Meta before keys go live
3. MSG91 SMS templates require DLT registration in India
4. `setuptools<81` pinned because Razorpay 1.4.2 uses deprecated `pkg_resources`
5. PWA PNG icons still SVG-only (P2)

## Backlog
### P1 — Financial & Admin Systems (next up)
- Client Financial Dashboard (full txn history with filters + CSV export)
- SSPL Admin Financial Dashboard (MRR, client-wise wallets, trends)
- Rectification System (append-only wallet adjustments with audit)
- Partner Commission System (24% acq / 6% recurring + bonus slabs)
- DB indexing + pagination (scale prep)
- Export to CSV/Excel
### P2
- PNG PWA icons (192/512) for iOS
- Service worker update prompt
### Deferred
- Predictive AI · Android native · Voice-note · White-label partner portal

See `/app/memory/test_credentials.md`.
