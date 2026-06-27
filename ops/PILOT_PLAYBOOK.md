# 🚀 Pilot Customer Onboarding Playbook

**Target**: First 3–5 pilot tenants on Fire Compliance OS v1.4
**Owner**: SSPL Founder + CSM
**Duration per pilot**: 14 days from kickoff → activation

---

## Pilot Selection Criteria

Choose pilots that meet **ALL** of these:

| Criterion | Why |
|---|---|
| Active fire-safety operations (≥20 assets) | Real usage data to validate workflows |
| Willing to give weekly feedback | Iteration partner, not just user |
| Tolerant of minor friction | First-mile bugs are inevitable |
| Founder-level relationship | Direct escalation channel |
| Not a flagship customer | Lower risk if things break |
| Pays at least ₹5,000/month wallet | Validates payment flow with real money |

**Recommend mix**:
- 2 × Tier 1 (Fire Safety Agencies — they understand the domain)
- 2 × Tier 2 (Industrial / commercial — validates compliance score value)
- 1 × Tier 4 (Government PSU pilot — unlocks tender references)

---

## Pre-Kickoff (T-7 days)

| Item | Owner | Status |
|---|---|---|
| Pilot agreement signed (pilot-specific T&C with 90-day commitment) | Sales | ☐ |
| GST + PAN collected | Sales | ☐ |
| Pilot tier confirmed (Strategic / Growth) | Sales + CSM | ☐ |
| Site list received (Excel template) | CSM | ☐ |
| Asset inventory received (Excel template) | CSM | ☐ |
| Team roster received (admins, technicians, inspectors) | CSM | ☐ |
| Initial wallet recharge wired (₹X based on tier — min ₹5,000) | Sales + Finance | ☐ |
| Tenant provisioned in production (via `POST /api/admin/clients`) | CSM | ☐ |
| Client admin password set + shared via secure channel (1Password) | CSM | ☐ |
| Kickoff call scheduled (45 min, both teams) | CSM | ☐ |

---

## Day 1 — Kickoff Call (45 min)

**Agenda**:
1. **0–5 min** — Welcome, intros, agenda
2. **5–15 min** — Architecture walkthrough (multi-tenant, roles, wallet model)
3. **15–30 min** — Live demo: create 1 site + 1 asset (let customer drive)
4. **30–35 min** — Generate QR code, print sticker
5. **35–40 min** — PWA install on customer's phone (rear camera scan demo)
6. **40–45 min** — Recap + schedule Day 7 call

**Deliverables**:
- Help Center link sent
- Support WhatsApp added to customer phone
- Calendar invite for Day 7 + Day 30
- 1-page Quick Reference printed/PDF'd

---

## Day 2–6 — Self-Driven Exploration

Customer does (with light CSM support via WhatsApp):
- Bulk-add assets (manual via UI until P2 CSV import lands)
- Invite team members
- Do 5 trial inspections
- Try password reset flow
- Upload one document
- Check Compliance Score

CSM monitors:
- Daily check on `audit_logs` — is customer engaged?
- Watch wallet balance — alert if approaching ₹500
- Watch `email_log` + `messaging_log` — alerts firing correctly?

---

## Day 7 — Bulk Data Load + Training Call (60 min)

**Goal**: customer self-sufficient by end of call

**Agenda**:
1. Review Week 1 usage from dashboard
2. Bulk asset import (CSM does data entry if customer hasn't)
3. Schedule 3 maintenance tasks
4. Submit 1 real inspection together
5. Generate Compliance Report PDF
6. Walk through Help Center

**Decision point**: customer ready to operate solo? If not → schedule Day 10 follow-up.

---

## Day 14 — Activation Review (30 min)

**Health checklist**:
- ☐ ≥80% of planned inspections done
- ☐ Wallet balance healthy (≥1 month runway)
- ☐ At least 1 technician used PWA on mobile
- ☐ At least 1 alert (low wallet OR failed inspection) received correctly
- ☐ Compliance Score visible and accurate
- ☐ Customer can self-recharge via Razorpay (test with ₹100 if not yet done)

**If health green → graduate to monthly cadence + introduce AMC opportunities.**
**If health yellow → extend pilot 2 weeks, focused on weakest area.**

---

## Day 30 — QBR + AMC Pitch

- Review month 1 metrics: assets, inspections, score, AMC opportunities surfaced
- Discuss: which AMC opportunities to book this month?
- Plan: month 2 expansion (more sites? more team members?)
- Recharge planning for month 2

---

## Day 60 — Case Study Discussion

- Was the platform worth ₹X this month?
- 1–10 NPS score
- 3 things they loved
- 3 things to improve
- Permission to use as case study (with logo)
- Referral discussion: which fire-safety peer would benefit?

---

## Pilot Tracking Spreadsheet (CSM maintains)

| Pilot | Tier | Start | Day 7 Health | Day 14 Health | Day 30 Recharge | NPS | Case Study? | Referrals |
|---|---|---|---|---|---|---|---|---|
| Pilot 1 | T1 | YYYY-MM-DD | 🟢/🟡/🔴 | 🟢/🟡/🔴 | ₹X | N/10 | Y/N | count |
| Pilot 2 | T2 | ... | | | | | | |

---

## Pilot Failure Criteria (kill switch)

A pilot is paused/terminated if:
- Customer reports >3 P0/P1 bugs in week 1 → engineering pause-and-fix sprint
- Customer asks for refund within 14 days → process refund, exit interview
- Pilot's industry has regulatory blocker we missed → defer, learn

**Refund policy for pilots**: full wallet balance refunded within 30 days if customer requests, no questions asked. Builds trust, surfaces honest feedback.

---

## What CSM Documents (every pilot)

1. **Pain points the product solves** — quotes for marketing
2. **Friction encountered** — bug reports + UX requests for product
3. **Feature requests** — ranked by frequency for roadmap
4. **Surprising usage patterns** — that we didn't anticipate
5. **Renewal trigger** — what made them stay (or leave)

---

## Engineering's Role During Pilots

- **No new feature work** during pilot (per Phase 7 mandate)
- Daily check of `db.audit_logs` + `db.email_log` + `db.messaging_log` for anomalies
- **Bug fixes only**: P0/P1 fixed within SLA, P2 batched into weekly patch release
- **Performance**: monitor p95 latency on pilot tenant — investigate if >1s
- Weekly engineering update to founder: "what we saw, what we fixed, what's risky"

---

## Pilot → GA (General Availability) Exit Criteria

All of:
- ✅ 3 of 5 pilots reach Day 30 with health 🟢
- ✅ Zero P0 bugs across all pilots
- ✅ At least 1 pilot completes Razorpay live recharge end-to-end successfully
- ✅ At least 1 pilot triggers full WhatsApp + SMS alert chain (real numbers)
- ✅ Average NPS ≥ 7 across pilots
- ✅ At least 2 written case studies (with logos)
- ✅ All Phase 7.1 operational hardening complete (CI, staging, Sentry, monitoring)

When all 7 are ✅ → declare GA → open public sign-up → start Phase 7.2 (P1 features).

---

**Status**: Pre-pilot · Awaiting SSPL go-live decision.
