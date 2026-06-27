# 🚀 SSPL Go-Live Action Plan

**Date**: April 2026
**Purpose**: Step-by-step actions SSPL must take to go from Phase 7.0 → first paid customer
**Estimated total elapsed time**: 5–10 business days (depending on KYC verification speeds)
**Estimated SSPL effort**: ~15–20 hours of actual work

> What this is: the **operator's checklist**, organized in sequence, with what to do, who can do it, where to do it, and what to send back to engineering.

---

## ⏱ Sequence Overview

```
Day 1 (today)  → Repo + GitHub setup       [1 hour]
Day 1–2        → Domain + DNS              [1 hour SSPL + 24h DNS propagation]
Day 2          → Cloudflare + R2           [1 hour]
Day 2–3        → MongoDB Atlas             [1 hour SSPL + setup wait]
Day 3–5        → Razorpay live account     [2–5 days incl. KYC verification]
Day 3          → Resend account            [30 min + DNS verify]
Day 3–7        → Meta WhatsApp Business    [3–5 days incl. template approval]
Day 4–6        → MSG91 + DLT registration  [2–3 days incl. DLT approval]
Day 5          → Production VM provisioned [2 hours]
Day 6          → Monitoring (UptimeRobot + Sentry) [1 hour]
Day 7          → Final deploy + smoke test [2 hours]
Day 8          → Pilot 1 onboarded         [Day 1 of pilot kick-off]
```

---

## STEP 1 — GitHub Repository (Day 1, 1 hour)

**SSPL action**:
1. Create GitHub org: `github.com/sspl-firecompliance` (Pro plan ₹350/user/mo or Free for ≤3 collaborators)
2. Create private repo: `fire-compliance-os`
3. In Emergent chat, click **"Save to GitHub"** → choose this repo
4. **Verify push succeeded**: see `v1.4.0-phase6-p0` tag in GitHub UI

**Engineering then**:
- Configure branch protection on `main` (require PR + 1 reviewer)
- Add Dependabot (already in repo as `.github/dependabot.yml`)
- Enable GitHub Actions (CI workflow already in `.github/workflows/ci.yml`)

**Output**: Repo URL committed to all team members. SSPL is now code owner.

---

## STEP 2 — Domain + DNS (Day 1–2, 1 hour active)

**SSPL action**:
1. Register domain (recommended: `firecompliance.in` or `securrise.in` — pick one for the brand)
2. Sign up for Cloudflare (free tier, https://cloudflare.com)
3. In Cloudflare dashboard → "Add a site" → enter your domain
4. Cloudflare gives you 2 nameservers (e.g., `kahn.ns.cloudflare.com`)
5. Update nameservers at your domain registrar to point to Cloudflare's
6. Wait 4–24 hours for propagation
7. Verify: `dig NS firecompliance.in` shows Cloudflare's NS

**Output**: Domain active under SSPL control, ready for DNS records.

---

## STEP 3 — Cloudflare R2 (Day 2, 1 hour)

**SSPL action**:
1. In Cloudflare dashboard → R2 → "Create bucket"
2. Bucket name: `fireos-prod-documents` (one per environment)
3. Location: `Asia-Pacific (APAC)` for low latency to India
4. Manage R2 API Tokens → Create API Token:
   - Permissions: "Object Read & Write"
   - Specify bucket: `fireos-prod-documents`
   - TTL: 1 year, then rotate
5. Copy `Access Key ID` + `Secret Access Key` + `Account ID` (from R2 sidebar)
6. Repeat for second bucket: `fireos-backups`

**Send to engineering** (encrypted channel — 1Password sharable link):
```
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET=fireos-prod-documents
R2_PUBLIC_BASE_URL=  (optional — only if you make it public)
```

---

## STEP 4 — MongoDB Atlas (Day 2–3, 1 hour + propagation)

**SSPL action**:
1. Sign up at https://cloud.mongodb.com (use SSPL email)
2. Create Organisation: "Securrise Solution Pvt Ltd"
3. Create Project: "Fire Compliance OS"
4. Create cluster:
   - Type: **M10 dedicated** ($57/mo)
   - Provider: AWS
   - Region: **Mumbai (ap-south-1)** ← IMPORTANT for data residency
   - Cluster name: `fireos-prod`
5. Database Access → Add user:
   - Username: `fireos_app`
   - Password: strong random (store in 1Password)
   - Role: `readWrite` on database `fire_compliance_os`
6. Network Access → Add IP whitelist (will add prod VM IP later; for now `0.0.0.0/0` temporarily and tighten in Step 9)
7. Database → "Connect" → "Drivers" → copy the connection string
8. Backup → Enable Continuous Cloud Backup (included in M10) + daily snapshot retention 30 days

**Send to engineering**:
```
MONGO_URL=mongodb+srv://fireos_app:PASSWORD@fireos-prod.xxxxx.mongodb.net/?retryWrites=true&w=majority
DB_NAME=fire_compliance_os
```

---

## STEP 5 — Razorpay (Day 3–8, 2–5 days incl. KYC)

**SSPL action**:
1. Sign up at https://razorpay.com — Business account under SSPL GSTIN
2. Submit KYC: PAN, GST cert, Cancelled cheque, Director PAN, Address proof
3. Wait 1–3 business days for activation
4. **Once activated**: Dashboard → Settings → API Keys → Generate **TEST** keys first
5. Webhooks → Add new:
   - URL: `https://app.<yourdomain>/api/payments/webhook`
   - Secret: generate a 32-char random string (1Password)
   - Events: ✅ `payment.captured` ✅ `order.paid`
6. After successful test transaction → switch to **LIVE** keys (regenerate)

**Send to engineering** (test first, then live):
```
RAZORPAY_KEY_ID=rzp_test_XXX   # then rzp_live_XXX
RAZORPAY_KEY_SECRET=XXX
RAZORPAY_WEBHOOK_SECRET=XXX
```

**SSPL GST invoice metadata** (one-time):
```
SSPL_GSTIN=<your real GSTIN>
SSPL_PAN=<your real PAN>
SSPL_ADDRESS=<registered address>
SSPL_STATE_CODE=<your state, e.g. 27 for Maharashtra>
```

---

## STEP 6 — Resend Email (Day 3, 30 min + DNS propagation)

**SSPL action**:
1. Sign up at https://resend.com (under SSPL email)
2. Add domain (e.g., `firecompliance.in`)
3. Resend gives you 3 DNS records (SPF, DKIM, MX) — add to Cloudflare DNS
4. Wait 5–60 minutes for verification
5. Once "verified" → API Keys → Create → copy

**Send to engineering**:
```
RESEND_API_KEY=re_XXX
EMAIL_FROM="Fire Compliance OS <noreply@firecompliance.in>"
```

**Optional SMTP fallback** (use SendGrid free 100/day or Brevo free 300/day):
```
SMTP_HOST=smtp-relay.brevo.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_USE_TLS=true
```

---

## STEP 7 — Meta WhatsApp Business (Day 3–7, 3–5 days approval)

**SSPL action**:
1. Sign up at https://business.facebook.com (under SSPL business name)
2. Verify business (Meta requires documents — GST cert + utility bill)
3. Add WhatsApp Business platform → Cloud API
4. Create system user with WhatsApp permissions, generate **permanent access token**
5. Get a phone number provisioned (free test number OK initially; later port your own)
6. Note the **Phone Number ID** (different from the actual phone number)
7. **Create 4 message templates** — Meta will review (24–48h typical):

   Template 1: `inspection_failure_alert` (Category: Utility)
   ```
   🚨 Inspection Failed
   Asset: {{1}}
   Inspector: {{2}}
   Notes: {{3}}
   Please review in Fire Compliance OS.
   ```

   Template 2: `wallet_low_alert` (Category: Utility)
   ```
   ⚠ Wallet Low — {{1}}
   Balance: ₹{{2}} (threshold ₹{{3}})
   Recharge soon to avoid service interruption.
   ```

   Template 3: `wallet_exhausted_alert` (Category: Utility)
   ```
   🛑 Wallet Exhausted — {{1}}
   Balance: ₹{{2}}
   Platform is in read-only mode. Recharge to resume.
   ```

   Template 4: `maintenance_scheduled_alert` (Category: Utility)
   ```
   🔧 Maintenance Due
   Asset: {{1}}
   Due Date: {{2}}
   ```

**Send to engineering**:
```
WHATSAPP_PHONE_NUMBER_ID=<numeric ID>
WHATSAPP_ACCESS_TOKEN=<permanent token>
WHATSAPP_API_VERSION=v20.0
WHATSAPP_TPL_LANG=en
WHATSAPP_TPL_INSPECTION_FAIL=inspection_failure_alert
WHATSAPP_TPL_LOW_WALLET=wallet_low_alert
WHATSAPP_TPL_WALLET_EXHAUSTED=wallet_exhausted_alert
WHATSAPP_TPL_MAINTENANCE=maintenance_scheduled_alert
```

---

## STEP 8 — MSG91 + DLT (Day 4–6, 2–3 days approval)

**SSPL action**:
1. Sign up at https://msg91.com
2. KYC + DLT registration (https://www.trai.gov.in) — required for India
3. Pick a Sender ID (6 chars, e.g., `SCNFOS`)
4. Submit 4 SMS templates for DLT approval — wait 24–72h

**Send to engineering** (post-approval, with DLT template IDs):
```
MSG91_AUTHKEY=<authkey>
MSG91_SENDER_ID=SCNFOS
MSG91_TPL_INSPECTION_FAIL=<DLT template ID>
MSG91_TPL_LOW_WALLET=<DLT template ID>
MSG91_TPL_WALLET_EXHAUSTED=<DLT template ID>
MSG91_TPL_MAINTENANCE=<DLT template ID>
```

---

## STEP 9 — Production VM (Day 5, 2 hours)

**SSPL action**:
- **Recommended**: Click "Deploy" in Emergent chat header (zero infra work, includes auto-scaling)
- **OR Self-host**: Provision Hetzner CX21 (€5.83/mo) or DigitalOcean 2vCPU droplet ($12/mo)

**If self-hosting**:
1. SSH into VM as root
2. Run our `/app/ops/nginx/fireos.conf` (after editing `app.yourdomain.com`)
3. Run our `/app/ops/supervisor/fireos.conf`
4. Issue SSL: `certbot --nginx -d app.yourdomain.com`
5. Set Cron: `30 21 * * * /opt/fireos/ops/backup.sh >> /var/log/fireos/backup.log 2>&1`
6. Atlas → Network Access → replace `0.0.0.0/0` with VM's exact IP
7. Open ports: 22 (SSH key-only), 80, 443; close all others (`ufw enable`)

**DNS**:
- Cloudflare → DNS → Add A record: `app` → VM's IP → proxied (orange cloud)

---

## STEP 10 — Monitoring (Day 6, 1 hour)

**SSPL action**:
1. **UptimeRobot** (https://uptimerobot.com — free tier):
   - Monitor 1: GET `https://app.yourdomain.com/api/health` every 1 min
   - Monitor 2: GET `https://app.yourdomain.com/` every 5 min
   - Alert contacts: SSPL ops email + WhatsApp (paid feature, $7/mo)

2. **Sentry** (https://sentry.io — free 5k events/month):
   - Create project: Python (FastAPI) + JavaScript (React)
   - Copy DSN
   - Send to engineering: `SENTRY_DSN=https://xxx@sentry.io/xxx`

3. **Atlas Alerts**:
   - Connections > 80% of limit → email
   - Disk > 80% → email
   - Replication lag > 10s → email

---

## STEP 11 — Final Deploy + Smoke Test (Day 7, 2 hours)

**Engineering action** (we'll execute):
1. Receive all 30+ env vars from SSPL via 1Password
2. Write to `/opt/fireos/app/backend/.env` (chmod 600)
3. Restart backend: `supervisorctl restart fireos-backend`
4. Run smoke test:
   ```bash
   curl https://app.yourdomain.com/api/health
   curl https://app.yourdomain.com/api/payments/config   # → configured:true
   ```
5. Manual UI test:
   - Login as superadmin
   - Create test tenant + admin
   - Log in as test admin
   - Recharge ₹100 via Razorpay (real money!)
   - Verify wallet credit + GST invoice PDF downloads
   - Trigger inspection fail → verify WhatsApp + SMS + Email received
   - Upload doc → verify R2 storage (check Cloudflare R2 dashboard)
   - Test password reset → verify email received

**Output**: 🟢 Production live. Ready for first pilot.

---

## STEP 12 — Pilot Onboarding (Day 8+)

Follow `/app/ops/PILOT_PLAYBOOK.md` — that's the customer-facing playbook.

---

## 🔐 Secret Handling Protocol

**SSPL responsibilities**:
- Use 1Password (or equivalent vault) for ALL credentials
- Share with engineering only via 1Password sharable links (auto-expire 48h)
- Never paste secrets in Slack/WhatsApp/Email/chat

**Engineering responsibilities**:
- Read keys, write to `.env`, never log them, never echo to console
- `/app/backend/.env` permissions `chmod 600` + owner `fireos`
- After all keys set, ask SSPL to confirm we delete the 1Password share

---

## 📋 Credential Collection Checklist

When you're ready to deliver to engineering, send this filled-in template via 1Password:

```
# === MANDATORY for go-live ===
MONGO_URL=
DB_NAME=fire_compliance_os
JWT_SECRET=          (generate: openssl rand -hex 32)
ADMIN_EMAIL=
ADMIN_PASSWORD=      (strong, ≥16 chars)
FRONTEND_URL=        (e.g., https://app.firecompliance.in)
ENVIRONMENT=production

# === Razorpay ===
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
RAZORPAY_WEBHOOK_SECRET=

# === Resend ===
RESEND_API_KEY=
EMAIL_FROM=

# === WhatsApp ===
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_ACCESS_TOKEN=
(plus 4 template names — already templated above)

# === MSG91 ===
MSG91_AUTHKEY=
MSG91_SENDER_ID=
(plus 4 DLT template IDs)

# === R2 ===
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET=fireos-prod-documents

# === Monitoring (optional) ===
SENTRY_DSN=

# === SSPL GST (one-time) ===
SSPL_GSTIN=
SSPL_PAN=
SSPL_ADDRESS=
SSPL_STATE_CODE=
```

---

## ⏯ Engineering's Standby Posture

While SSPL works through Steps 1–10, engineering will:
- Stand by for credential drops
- Monitor pilot tenant `audit_logs` once live
- Be on-call for any deployment issues
- **NOT begin Phase 7.2 (new features)** until pilots prove stable

If anything blocks during Step 1–11, SSPL pings engineering channel → we respond <2 hours during business hours, <8 hours after-hours.

---

**Document version**: 1.0 · **Effective**: April 2026
**Companion**: `/app/PHASE_7_GOVERNANCE.md`
