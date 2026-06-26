# 🏢 SCN BUSINESS OPERATING SYSTEM

**Document Type**: Operational Master Playbook  
**Owner**: Securrise Solution Pvt Ltd (SSPL)  
**Product**: Fire Compliance OS (v1.4)  
**Status**: ✅ MASTER REFERENCE — Phase 6.5  
**Effective Date**: April 2026  
**Companion to**: `/app/SCN_PRODUCT_BIBLE.md` (technical) · `/app/CLOSURE_REPORT_v1.4.md`

> **Purpose**: Translate technical capability into operational excellence. This document is the playbook for **anyone outside engineering** — Sales, CS, Partners, Ops, Finance, Leadership — to run SCN at scale.

---

## TABLE OF CONTENTS

1. [Sales Playbook](#1-sales-playbook)
2. [Customer Success Manual](#2-customer-success-manual)
3. [Government Sales Manual](#3-government-sales-manual)
4. [Partner Program Manual](#4-partner-program-manual)
5. [Renewal & Retention Playbook](#5-renewal--retention-playbook)
6. [Subscription Lifecycle](#6-subscription-lifecycle)
7. [Customer Journey Map](#7-customer-journey-map)
8. [Implementation SOP](#8-implementation-sop)
9. [Support & Escalation Matrix](#9-support--escalation-matrix)
10. [KPI Dashboard Definition](#10-kpi-dashboard-definition)
11. [Department-wise SOPs](#11-department-wise-sops)
12. [Risk Register](#12-risk-register)
13. [Business Continuity Plan](#13-business-continuity-plan)
14. [Data Governance Policy](#14-data-governance-policy)
15. [Annual Product Governance Calendar](#15-annual-product-governance-calendar)

---

## 1. Sales Playbook

### 1.1 Ideal Customer Profile (ICP)
| Tier | Profile | Wallet Size | Sales Motion |
|---|---|---|---|
| **Tier 1** | Fire Safety Agencies managing 10–50 client portfolios | ₹50k–₹2L/month | Direct, founder-led |
| **Tier 2** | Mid-size industrial parks, hospitals, malls (multi-site) | ₹10k–₹50k/month | Inside sales |
| **Tier 3** | SME factories, warehouses, single-site offices | ₹2k–₹10k/month | Self-serve + partner channel |
| **Tier 4 (Gov)** | Municipal corporations, PSU industrial estates | ₹2L+/quarter | Government sales (see §3) |

### 1.2 Buyer Personas
| Persona | Pain | Trigger | Pitch Angle |
|---|---|---|---|
| **Owner / MD of Fire Agency** | Manual logbooks, lost revenue, audit failures | Lost a client to competitor with software | "Convert AMC opportunities + take inspector load off you" |
| **Plant / Facility Manager** | Fire inspector visits, NOC anxiety, expiry tracking | Surprise inspection notice / NOC renewal | "Always audit-ready compliance score" |
| **CFO / Finance Head** | GST compliance, AMC budget visibility | Quarterly review meeting | "Per-asset transparent billing + auto-GST invoices" |
| **CTO / Head of IT** | Integration with ERP, data ownership | Internal IT review | "API-first, your data, your control" |

### 1.3 The 5-Call Sales Process
| Call | Goal | Duration | Outcome |
|---|---|---|---|
| **C1: Discovery** | Understand portfolio size + current process pain | 30 min | Qualify or disqualify |
| **C2: Demo** | One-click demo login → walk through their use case | 45 min | Specific use-case alignment |
| **C3: Pricing & Custom Proposal** | Wallet recharge sizing + AMC upsell projection | 30 min | Send proposal |
| **C4: Decision Maker / Procurement** | Address commercial + technical objections | 60 min | Verbal commit |
| **C5: Onboarding Kickoff** | Site list, user roles, recharge, training schedule | 45 min | Hand off to Implementation |

### 1.4 Objection-Handling Cheat Sheet
| Objection | Response |
|---|---|
| "We use Excel" | "Excel doesn't auto-detect expired extinguishers or send WhatsApp alerts to your client. SCN does — for ₹10/asset/month." |
| "Too expensive" | "Show your last 3 missed inspections. The fine per miss is ₹25k+ under Section 24 of the Fire Act. We cost less than 1 fine/year." |
| "We'll build our own" | "We've shipped 4 phases in 6 months with audit-grade compliance. Show me your timeline to GST-compliant invoicing + WhatsApp alerts." |
| "Internet down at site?" | "PWA installable on any phone — works offline for QR scan + inspection. Syncs when back online." |
| "Data security?" | "Multi-tenant with hard isolation, AES-encrypted at rest (R2/Atlas), httpOnly cookies, audit log of every action." |
| "What if you shut down?" | "100% data export available; you retain commercial copy of your DB. Source code escrow available for enterprise tier." |

### 1.5 Pricing Calculator (sales team uses)
```
Monthly wallet recharge =
  (assets × ₹10) + (inspections × ₹5) + (users × ₹20) + 20% buffer

Annual contract value (ACV) =
  Monthly × 12 + AMC upsell potential (₹X per booked service)

Discount ladder:
  ₹50k+ recharge   → 5% bonus credit
  ₹1L+ recharge    → 10% bonus credit
  ₹5L+ annual prepay → 15% bonus credit + dedicated CSM
```

### 1.6 Sales Stack
| Tool | Purpose |
|---|---|
| HubSpot Free / Zoho CRM | Lead tracking |
| Calendly | Demo booking |
| Loom | Custom demo videos for prospects |
| Razorpay Payment Links | Quote-to-cash (P2 feature in roadmap) |

### 1.7 Sales KPIs
- Demos booked / week (target: 15)
- Demo → paid conversion (target: 30%)
- Avg deal size (target: ₹25k/month)
- Sales cycle length (target: 21 days)

---

## 2. Customer Success Manual

### 2.1 CS Tier Definitions
| Tier | Recharge ≥ | Cadence | CSM Coverage |
|---|---|---|---|
| **Strategic** | ₹1L/month | Weekly check-in | Dedicated CSM |
| **Growth** | ₹25k/month | Bi-weekly | Shared CSM (1 per 20) |
| **Self-serve** | <₹25k/month | Quarterly + automated | Email + Help Center |

### 2.2 30-60-90 Day Plan
| Days | Goal | Owner Action | Customer Action |
|---|---|---|---|
| **0–7 (Onboarding)** | Asset master populated + 1st inspection done | CSM trains client_admin + 1 technician | Add 10 assets, do 1 trial inspection |
| **8–30 (Activation)** | All sites onboarded, 1st month inspections complete | Weekly call + Help Center walk-through | Hit 80% of planned inspections |
| **31–60 (Engagement)** | First AMC booking + NOC checklist 100% | Surface AMC opportunities | Book at least 1 service |
| **61–90 (Expansion)** | Add 2nd portfolio / additional sites | QBR (Quarterly Business Review) | Recharge for Q2 |

### 2.3 Health Score (per tenant)
Computed from real data; weights TBD by Product:
```
Health Score = 0.3 × wallet_balance_status     (safe/low/exhausted)
             + 0.2 × inspection_velocity       (inspections/week vs target)
             + 0.2 × compliance_score          (already in product)
             + 0.15 × user_activity            (DAU/MAU)
             + 0.15 × support_ticket_severity  (zero is best)
```
- **80–100**: Green — promote to case study candidate
- **60–79**: Yellow — proactive call within 48h
- **<60**: Red — escalation to CS Lead + Founder

### 2.4 Customer Lifecycle Touchpoints
| Stage | Touchpoint | Channel | Owner |
|---|---|---|---|
| Day 1 | Welcome email + Demo login link | Email | CSM |
| Day 3 | Onboarding call | Phone/Zoom | CSM |
| Day 7 | "How was Week 1?" check-in | WhatsApp | CSM |
| Day 30 | Activation review + AMC pitch | Phone | CSM |
| Day 60 | Compliance Report PDF shared | Email | Auto |
| Day 90 | QBR + renewal nudge | In-person/Zoom | CSM + Sales |
| Annually | Renewal celebration + bonus credit | Email + WhatsApp | Auto + CSM |

### 2.5 Save Plays (when customer signals churn)
| Signal | Save Play |
|---|---|
| Wallet not recharged for 14 days post-exhaustion | Founder call + bonus credit offer (5–10%) |
| Support tickets >5/month with low satisfaction | CSM + Product Manager 1:1 |
| No active users for 30 days | Re-onboarding session (free) |
| Negative NPS (≤6) | Founder call within 48h, root cause analysis |

---

## 3. Government Sales Manual

### 3.1 Why Government is Strategic
- 70% of India's fire compliance burden lies in PSU, municipal, and gov-industrial estates
- Multi-year contracts (3–5 years) with predictable revenue
- Reference customers unlock private-sector pipeline

### 3.2 Government Entity Map
| Entity | Decision Maker | Procurement Vehicle |
|---|---|---|
| **State Industrial Development Corp** (MIDC, GIDC, etc.) | CMD / Joint MD | Open tender + GeM |
| **Municipal Corporations** (BMC, GHMC, MCD) | Commissioner / Addl. Commissioner | Tender via state portal |
| **PSU Refineries / Power Plants** | GM (Safety) / GM (IT) | Limited tender + DGS&D rates |
| **Airports Authority of India (AAI)** | Head of Fire Safety | EOI → RFP → Reverse auction |
| **Defence / Cantonment Boards** | Cantonment Officer | Sealed tender |

### 3.3 Mandatory Compliance Documents
| Doc | Where to Get | Renewal Frequency |
|---|---|---|
| GeM (Government e-Marketplace) registration | gem.gov.in | Annually |
| Udyam / MSME certificate | udyamregistration.gov.in | Self-attested |
| GST registration (already have) | gst.gov.in | Quarterly returns |
| MAF (Manufacturer Authorisation Form) | SSPL letterhead | Per-tender |
| OEM certificate for SaaS | SSPL letterhead | Per-tender |
| ISO 27001 (recommended for ≥₹50L tenders) | Certifying body (BSI, TÜV) | 3-year cycle |
| CERT-In empanelment (recommended for cyber-sensitive) | cert-in.org.in | 3-year cycle |

### 3.4 Tender Response Workflow
```
Tender published → 1. Eligibility check (turnover, experience, certs)
                 → 2. Pre-bid meeting attendance (mandatory)
                 → 3. Technical bid prep (architecture diagram, security, compliance)
                 → 4. Commercial bid (per-asset pricing matrix)
                 → 5. Submit before deadline (online via portal)
                 → 6. Technical opening → Q&A
                 → 7. Reverse auction (if L1 tender)
                 → 8. Award notification → PO → kickoff
```

### 3.5 Government Pricing Logic
- Per-asset rate (₹10) **fixed for 3 years**
- Free training (8 hrs)
- Dedicated CSM for first 6 months
- SLA: 99.5% uptime, <4h critical-bug fix
- Payment terms: 30-day post-quarterly-invoice (Government Standard)

### 3.6 Key Differentiators in Tender Response
1. **India-owned SaaS** — data residency in Indian R2/Atlas region
2. **GST-compliant invoicing** — already audit-ready
3. **DLT-compliant SMS** — already integrated
4. **NOC Readiness module** — unique to fire compliance vertical
5. **Audit log immutability** — every action timestamped + user-attributed

---

## 4. Partner Program Manual

### 4.1 Partner Tiers
| Tier | Eligibility | Acquisition Commission | Recurring Commission | Bonus |
|---|---|---|---|---|
| **Referrer** | Anyone with a contact | 5% one-time | 0% | Cash bonus on first recharge |
| **Reseller** | Existing fire safety vendor | **24%** of first wallet recharge | **6%** of all future recharges | 5% bonus on annual prepay |
| **Implementation Partner** | Trained CSM + certified | 24% | 6% | Service revenue (₹500/site setup) |
| **Strategic Partner** | Industry association | Custom (revenue share) | Custom | Co-marketing budget |

### 4.2 Partner Onboarding
1. Apply via `partner@scn.in`
2. Sign partner agreement (template in `/legal/`)
3. SSPL provides partner dashboard access (P1 in roadmap — currently manual)
4. Training: 4-hour Zoom session on product + sales
5. Co-brand collateral kit (pitch deck, demo video, brochure)
6. First lead handed over → partner pitches → SSPL closes → commission tracked

### 4.3 Partner Commission Tracking (current — manual, P1 automated)
- Each tenant `client_id` tagged with `referred_by_partner_id`
- 24% of first `wallet_transaction.type=credit` → partner ledger
- 6% of every subsequent `credit` → partner ledger
- Monthly settlement on 7th of next month (via NEFT, TDS deducted)

### 4.4 Partner Code of Conduct
- No misrepresentation of features
- No undercutting SSPL's pricing
- Customer escalations must route to SSPL within 4 hours
- Confidentiality of customer data (NDA in agreement)
- Cannot resell to direct competitors of SSPL

### 4.5 Top Partner Recognition
- **Partner of Quarter**: highest new revenue
- **Partner of Year**: highest LTV book
- Awards: cash incentive (₹1L) + recognition at annual SCN Summit + co-marketing

---

## 5. Renewal & Retention Playbook

### 5.1 Renewal Definition
Since SCN uses prepaid wallet (not subscription), "renewal" = **wallet recharge before exhaustion**.

### 5.2 Renewal Cadence
| Trigger | Action | Owner |
|---|---|---|
| Balance < ₹500 (auto-detected) | In-app + email + WhatsApp alert | System (already coded) |
| Balance < ₹200 | CSM phone call within 24h | CSM |
| Balance = 0 (read-only mode) | Founder/Sales escalation within 48h | Sales |
| Wallet not recharged for 14 days post-exhaustion | "Win-back" campaign | CSM + Marketing |

### 5.3 Renewal Bonus Slabs (P1 feature)
| Recharge Amount | Bonus Credit | Effective Rate |
|---|---|---|
| ₹10k | 0% | ₹10k |
| ₹50k | +₹2,500 | ₹52,500 (5%) |
| ₹1L | +₹10,000 | ₹1,10,000 (10%) |
| ₹5L (annual) | +₹75,000 | ₹5,75,000 (15%) |

### 5.4 Churn Prevention Signals
| Signal | Days Before Churn | Action |
|---|---|---|
| DAU dropped >50% | 30 | CSM call |
| No new asset added in 30 days | 21 | Re-engagement email |
| Inspection velocity dropped | 14 | "Are you facing issues?" outreach |
| Support tickets unanswered by customer | 7 | Manual reopen |
| Negative NPS | 0 | Founder call |

### 5.5 Retention Metrics
| Metric | Target |
|---|---|
| NRR (Net Revenue Retention) | ≥110% |
| GRR (Gross Revenue Retention) | ≥90% |
| Logo retention (annual) | ≥85% |
| Time to first AMC booking | <60 days |

---

## 6. Subscription Lifecycle

### 6.1 Lifecycle Stages
```
[Lead] → [Qualified] → [Demo'd] → [Negotiating] → [Closed-Won] →
[Onboarding] → [Activated] → [Engaged] → [Expanding] → [Renewing]
                                              ↓
                                          [At Risk] → [Won-Back] / [Churned]
```

### 6.2 Definitions
| Stage | Entry Criteria | Exit Criteria |
|---|---|---|
| **Lead** | Form fill / inbound / referral | Sales contact made |
| **Qualified** | ICP fit + budget confirmed | Demo scheduled |
| **Demo'd** | Demo completed | Proposal sent |
| **Negotiating** | Proposal sent | PO/commit received |
| **Closed-Won** | Contract signed | First recharge done |
| **Onboarding** | Day 0–7 | First inspection submitted |
| **Activated** | Day 8–30 | 80% inspection target met |
| **Engaged** | Day 31–90 | 1+ AMC booking |
| **Expanding** | Additional sites/users | 2× original wallet |
| **Renewing** | Wallet recharge | Continued use |
| **At Risk** | Health <60 | Save play activated |
| **Won-Back** | Re-engaged after At Risk | Health ≥70 |
| **Churned** | No recharge × 60 days | (terminal state) |

### 6.3 Lifecycle Automation
| Stage Transition | Automation |
|---|---|
| Qualified → Demo'd | CRM auto-sends demo invite |
| Closed-Won → Onboarding | Welcome email + checklist email |
| Onboarding → Activated | "Congrats" email + AMC opportunity surfaced |
| Engaged → Expanding | Dashboard recommends new sites |
| Renewing | Bonus slab email |
| At Risk | Slack alert to CSM Lead |
| Churned | Exit survey + win-back drip |

---

## 7. Customer Journey Map

### 7.1 Pre-Sale (Awareness → Decision)
| Phase | Customer Action | Emotion | Touchpoint | Owner |
|---|---|---|---|---|
| Awareness | Hears about SCN via partner / Google | Curious | Landing page, demo | Marketing |
| Consideration | Books a demo | Hopeful | Demo call | Sales |
| Decision | Compares with Excel/competitor | Anxious | Proposal, ROI calc | Sales |
| Purchase | Signs contract + first recharge | Excited | Razorpay checkout, GST invoice | Sales + System |

### 7.2 Post-Sale (Onboarding → Advocacy)
| Phase | Customer Action | Emotion | Touchpoint | Owner |
|---|---|---|---|---|
| Onboarding (Day 0–7) | Adds sites, assets, team | Overwhelmed | CSM call, Help Center | CSM |
| First Win (Day 8–30) | First inspection report, compliance score visible | Relieved | Dashboard, PDF report | CSM + System |
| Adoption (Day 31–90) | Uses scheduler, books AMC | Confident | Reports, AMC notifications | System + CSM |
| Expansion (Day 90+) | Adds new sites / portfolios | Trusting | QBR, expansion offer | CSM + Sales |
| Advocacy (Day 180+) | Case study, referral | Loyal | NPS survey, partner enrolment | CSM + Founder |

### 7.3 Critical Moments of Truth
| Moment | Risk | What MUST happen |
|---|---|---|
| Demo Day | Bad demo = lost deal | Use real-data demo, not slides |
| Day 1 Login | Confusion = early churn | CSM-guided session, no self-discovery |
| First Wallet Exhaustion | Read-only mode = anger | Pro-active recharge nudge 5 days before |
| First Failed Inspection | Surprise = trust loss | Alert chain (in-app + email + WhatsApp) fires immediately |
| First NOC Audit | Audit failure = brand damage | Auto-generate PDF Compliance Report |
| First Annual Renewal | Skip renewal = churn | QBR + bonus slab offer |

### 7.4 Frustration Hotspots (proactive mitigation)
| Hotspot | Mitigation |
|---|---|
| "I don't know what to do next" | Onboarding progress tracker (already in product) |
| "My wallet exhausted unexpectedly" | Low-balance alerts (already in product) + visible usage forecast (P1) |
| "Lost a paper inspection sheet" | PWA QR scan + offline inspection (already in product) |
| "Inspector forgot to update" | Quick-Pass button + technician phone alerts (already in product) |
| "Auditor asked for evidence" | Audit log + PDF reports (already in product) |

---

## 8. Implementation SOP

### 8.1 Pre-Kickoff Checklist
- [ ] Contract signed + GST details collected
- [ ] First wallet recharge done (₹X based on tier)
- [ ] Client_admin email + password set
- [ ] Site list collected (Excel template provided)
- [ ] Asset list collected (template provided)
- [ ] Team roster (technicians, fire officers) collected
- [ ] Kickoff call scheduled (45 min, both teams present)

### 8.2 Day 1 — Kickoff
- 5 min: Welcome + agenda
- 10 min: Walk through SCN architecture + roles
- 15 min: Live create sites + 1 asset (let customer drive)
- 5 min: QR code generation + print
- 5 min: PWA install on customer's phone
- 5 min: Schedule next call (Day 7)

### 8.3 Day 7 — Bulk Data Load
- Bulk asset import (manual until P2 CSV import lands)
- User invitations sent
- 1st inspection done together (training)
- 1st maintenance task scheduled

### 8.4 Day 14 — Self-Sufficient Check
- Customer demonstrates: scan QR → submit inspection → view dashboard
- Help Center tour
- Support channel info shared

### 8.5 Day 30 — Activation Review
- Health score baseline
- Compliance Report PDF reviewed together
- AMC opportunities discussion
- Recharge planning for month 2

### 8.6 Implementation Time SLAs
| Tier | Onboarding Duration |
|---|---|
| Strategic | 14 days, dedicated PM |
| Growth | 7 days |
| Self-serve | <2 days (mostly automated) |
| Government | 30–60 days (procurement-dependent) |

---

## 9. Support & Escalation Matrix

### 9.1 Severity Definitions
| Severity | Definition | Example | SLA Response | SLA Resolution |
|---|---|---|---|---|
| **P0 — Critical** | Production down, data loss risk | Backend crash, all logins failing | 15 min | 2 hours |
| **P1 — High** | Major feature broken, multi-user impact | Razorpay verification failing | 1 hour | 8 hours |
| **P2 — Medium** | Single-user feature issue | One user can't login | 4 hours | 2 business days |
| **P3 — Low** | Cosmetic, enhancement | Typo, button alignment | 1 business day | Next sprint |

### 9.2 Escalation Ladder
```
Customer reports → /api/support-requests (Tier 0: self-serve)
                 ↓
                 Help Center / Demo Mode (Tier 1: documentation)
                 ↓
                 CSM (Tier 2: 4-hour response)
                 ↓
                 CS Lead (Tier 3: 1-hour response, P1+)
                 ↓
                 Engineering on-call (Tier 4: 15-min response, P0)
                 ↓
                 Founder / CTO (Tier 5: legal/PR/compliance)
```

### 9.3 Support Channels
| Channel | Use Case | Owner |
|---|---|---|
| In-app support ticket | All product issues | CSM |
| Email (`support@scn.in`) | Follow-ups, attachments | CSM |
| WhatsApp business number | Quick questions, status checks | CSM |
| Phone (Strategic only) | Urgent P0/P1 | CS Lead |
| Slack Connect (Strategic only) | Real-time co-working | CSM |

### 9.4 Communication Rules
- **Acknowledge within SLA, always** (even if resolution will take longer)
- Status updates every 2 hours for P0, every 8 hours for P1
- Post-mortem RCA published within 48 hours of P0 resolution
- All P0/P1 logged in `audit_logs` for compliance

### 9.5 Knowledge Base Maintenance
- Help Center (`/app/help`) — owned by CSM, updated weekly
- Every recurring ticket type triggers a Help Center article within 7 days
- Internal runbook for ops — `/ops/runbooks/`

---

## 10. KPI Dashboard Definition

### 10.1 North Star Metric
**Monthly Recurring Wallet Recharge (MRWR)** = sum of all wallet credits in a calendar month

### 10.2 Executive Dashboard (Founder + Leadership)
| KPI | Source | Target | Frequency |
|---|---|---|---|
| MRWR | `db.wallet_transactions` type=credit | Growth Y/Y | Real-time |
| Total Active Tenants | `db.clients` license_active=true | +20% Q/Q | Daily |
| Net Revenue Retention | (Expansion − Churn) / Starting MRR | ≥110% | Monthly |
| Logo Churn % | (Tenants lost / Tenants at start) | ≤5%/qtr | Monthly |
| CAC (Customer Acquisition Cost) | Sales + Marketing spend / new logos | ≤3× monthly ARPU | Quarterly |
| LTV (Lifetime Value) | Avg monthly recharge × avg lifespan months | ≥10× CAC | Quarterly |
| NPS (Net Promoter Score) | In-app survey | ≥40 | Quarterly |

### 10.3 Sales Dashboard
| KPI | Source | Target |
|---|---|---|
| MQLs / week | Marketing CRM | 30 |
| SQLs / week | Sales CRM | 15 |
| Demos / week | Calendly | 10 |
| Win rate (demo → paid) | CRM | ≥30% |
| Avg deal size | `db.payment_orders` first recharge | ≥₹25k |
| Sales cycle (days) | CRM stage timestamps | ≤21 |
| Pipeline coverage | Open opportunities / quarterly quota | ≥3× |

### 10.4 Product Dashboard
| KPI | Source | Target |
|---|---|---|
| DAU / MAU | `db.audit_logs` distinct user_id | ≥40% |
| Avg inspections / tenant / week | `db.inspections` | ≥10 |
| AMC conversion rate | (AMC booked / opportunities) | ≥20% |
| Feature adoption: PWA installed | (P2 — needs analytics) | ≥60% of tech users |
| Avg compliance score | `db.compliance/score` aggregate | ≥80 |

### 10.5 Operations Dashboard
| KPI | Source | Target |
|---|---|---|
| Uptime % | External monitoring | ≥99.9% |
| P0 incidents / quarter | `audit_logs` action=incident | 0 |
| Avg API response (p95) | nginx logs | <500ms |
| Daily MongoDB backup success | Backup cron | 100% |
| Support response time (p95) | Ticket system | within SLA |

### 10.6 Customer Success Dashboard
| KPI | Source | Target |
|---|---|---|
| Tenants with Health <60 | computed | ≤10% |
| Save-play success rate | (Won-Back / At Risk) | ≥40% |
| Time to first AMC booking | `db.amc_bookings` | <60 days |
| QBRs completed / quarter | CRM | 100% of Strategic |

### 10.7 Implementation
- Phase 7 P1 feature: Financial Dashboard already roadmapped
- Phase 8 P2: Connect Metabase/Superset to MongoDB read replica for these dashboards
- Until then: Quarterly manual export via aggregation queries (provided in `/ops/sql/`)

---

## 11. Department-wise SOPs

### 11.1 Founder / CEO Office
| SOP | Frequency | Output |
|---|---|---|
| Strategic roadmap review | Quarterly | Updated PRD.md + Bible |
| Board / investor update | Monthly | KPI snapshot + commentary |
| Hiring approval | Per-role | Sign-off in HR system |
| Customer escalations (P0) | As-needed | Direct call + resolution log |

### 11.2 Sales
| SOP | Frequency | Output |
|---|---|---|
| Pipeline review | Weekly | CRM forecast |
| Win/loss analysis | Monthly | Document patterns |
| Pricing committee | Quarterly | Pricing adjustments |
| Customer references library | Continuous | 5 case studies live |

### 11.3 Customer Success
| SOP | Frequency | Output |
|---|---|---|
| Health score review | Daily | Action list |
| QBR with Strategic accounts | Quarterly | QBR deck + action items |
| Onboarding handoff from Sales | Per-customer | Onboarding checklist |
| Save-play execution | As-needed | Documented in ticket |

### 11.4 Engineering
| SOP | Frequency | Output |
|---|---|---|
| Sprint planning | Bi-weekly | Backlog grooming |
| Code review | Per-PR | Approved merge |
| Test coverage check | Per-release | iteration_N.json report |
| Security review | Quarterly | Updated Risk Register |
| Performance review | Monthly | p95 + uptime |

### 11.5 Operations / DevOps
| SOP | Frequency | Output |
|---|---|---|
| Daily backup verification | Daily | Backup log + alert if failed |
| Uptime dashboard review | Daily | Incident report if <99.9% |
| Cert renewal | 30 days before expiry | Auto via certbot |
| Quarterly DR drill | Quarterly | Drill report + lessons |

### 11.6 Finance
| SOP | Frequency | Output |
|---|---|---|
| GST return filing | Monthly (GSTR-1, GSTR-3B) | Filed via gst.gov.in |
| Revenue reconciliation | Monthly | Match `wallet_transactions` × Razorpay |
| Partner commission settlement | Monthly (7th) | NEFT transfers + TDS certificates |
| Annual audit | Annually | Audited financial statements |

### 11.7 Compliance / Legal
| SOP | Frequency | Output |
|---|---|---|
| Privacy policy review | Annually | Updated /terms |
| Customer NDA / DPA | Per-contract | Signed agreement |
| Data subject request (GDPR-style) | Within 30 days of request | Export/deletion completed |
| Regulatory updates monitoring (Fire Act, GST, DLT) | Continuous | Internal memo if action needed |

### 11.8 Marketing
| SOP | Frequency | Output |
|---|---|---|
| Content calendar | Quarterly | 4 blog posts, 2 case studies, 1 webinar |
| Demo video refresh | Per-release | Updated landing page |
| Email nurture sequence | Continuous | Active drip campaigns |
| Conference / event presence | Quarterly | Fire safety + SaaS India events |

---

## 12. Risk Register

### 12.1 Risk Categorisation
- **Strategic**: existential business risks
- **Operational**: day-to-day execution risks
- **Financial**: cashflow, revenue, cost risks
- **Compliance**: legal, regulatory, certification
- **Technical**: code, infra, security
- **Reputation**: brand, PR

### 12.2 Risk Matrix
| # | Risk | Category | Likelihood | Impact | Score | Owner | Mitigation |
|---|---|---|:-:|:-:|:-:|---|---|
| R-1 | Razorpay deactivates account (fraud accusation) | Operational | LOW | CRITICAL | 9 | Founder | PayU/Stripe India as backup |
| R-2 | Meta WhatsApp template rejection / suspension | Operational | MED | MED | 6 | Product | MSG91 SMS fallback already coded |
| R-3 | MongoDB Atlas outage | Technical | LOW | CRITICAL | 9 | DevOps | Daily backups + DR plan |
| R-4 | Key engineer leaves | Strategic | MED | HIGH | 8 | Founder | Documentation (this Bible), code reviews mandatory |
| R-5 | Major security breach (data leak) | Technical | LOW | CRITICAL | 9 | CTO | Quarterly pentest, CERT-In empanelment |
| R-6 | GST regulation changes (rate, invoicing) | Compliance | MED | MED | 6 | Finance | Quarterly regulatory review |
| R-7 | Customer files lawsuit (e.g., missed inspection blame) | Reputation | LOW | HIGH | 7 | Legal | Liability cap in T&C, audit log evidence |
| R-8 | Cashflow crunch (high CAC, slow recharges) | Financial | MED | HIGH | 8 | CFO | Maintain 12 months runway |
| R-9 | Competitor launches free tier | Strategic | MED | MED | 6 | Founder | Differentiate on India compliance + audit-grade |
| R-10 | Government contract delayed payment | Financial | HIGH | MED | 7 | Sales | Invoice factoring, 30/60/90 day terms standard |
| R-11 | Customer data sovereignty (foreign request) | Compliance | LOW | HIGH | 7 | Legal | India-only data residency (R2/Atlas Mumbai) |
| R-12 | DDoS attack on production | Technical | LOW | HIGH | 7 | DevOps | Cloudflare proxy (already used for R2) |
| R-13 | Razorpay test→live key swap error in production | Operational | MED | HIGH | 8 | DevOps | Runbook + staging environment |
| R-14 | Partner mis-sells (overcommits features) | Reputation | MED | MED | 6 | Partner Manager | Partner training + audit calls |
| R-15 | Founder/key person hospitalisation | Strategic | LOW | CRITICAL | 9 | Founder | Key-person insurance + delegation matrix |

### 12.3 Risk Review Cadence
- **Monthly**: CTO + Founder review top 5 risks
- **Quarterly**: Full register review with all department heads
- **Annually**: Re-score all risks + add new ones

---

## 13. Business Continuity Plan

### 13.1 Scope
Beyond technical disaster recovery (covered in Product Bible §14), this plan covers **business continuity** — keeping SCN operational across people, processes, suppliers, and external shocks.

### 13.2 Continuity Scenarios
| Scenario | Likelihood | Continuity Plan |
|---|:-:|---|
| **Office shutdown** (pandemic, natural disaster) | MED | All ops remote-capable; Slack + Zoom + Drive ensure zero downtime |
| **Founder hospitalisation** | LOW | Delegation matrix: CTO acts as interim CEO for 30 days; Board notified within 24h |
| **Mass resignation** (>50% engineering) | LOW | Bible + Closure Report enable 2-engineer reboot; emergency hiring partner on retainer |
| **Razorpay account block** | LOW | Switch to PayU/Stripe India within 48h (alt-integration playbook in `/ops/`) |
| **R2 region outage (Mumbai)** | LOW | Local-disk fallback (already coded) + R2 fail-over to alt-region within 4h |
| **MongoDB Atlas global outage** | LOW | Restore to self-hosted MongoDB on backup VM within 4h |
| **Internet outage at ops centre** | MED | Remote ops continues; founder + CSM team can WFH |
| **Bank account frozen** | LOW | Backup current account at second bank (operational use only) |
| **GST registration suspended** | LOW | Immediate compliance review + reactivation; pause invoice issuance |
| **WhatsApp suspends business number** | MED | MSG91 SMS continues automatically; reapply via Meta Support |

### 13.3 Communication Plan (during continuity event)
| Audience | Channel | Within |
|---|---|---|
| Customers (Strategic) | Direct call from Founder/CSM | 4 hours |
| Customers (all) | Email + in-app banner | 24 hours |
| Partners | WhatsApp + email | 4 hours |
| Investors | Personal email | 24 hours |
| Employees | All-hands Zoom | 2 hours |
| Press (if needed) | Statement via PR firm | 48 hours |

### 13.4 Insurance Coverage
| Type | Coverage | Renewal |
|---|---|---|
| Professional Indemnity | ₹2 Cr | Annually |
| Cyber liability | ₹2 Cr | Annually |
| Key person insurance (Founder) | ₹5 Cr | Annually |
| Office contents | as per asset register | Annually |
| Public liability | ₹1 Cr | Annually |

### 13.5 BCP Drill Schedule
- **Monthly**: backup restore drill (staging)
- **Quarterly**: full DR drill (1 hour) — restore from latest backup
- **Annually**: tabletop simulation of 3 scenarios with leadership team

---

## 14. Data Governance Policy

### 14.1 Data Classification
| Class | Examples | Storage | Retention | Access |
|---|---|---|---|---|
| **Public** | Marketing pages, demo data | Anywhere | Indefinite | All |
| **Internal** | Audit logs, SOPs | Internal systems | 7 years | Employees |
| **Confidential** | Customer assets, inspections, financial data | MongoDB encrypted | Per contract (min 5 years) | Tenant-scoped + super_admin |
| **Restricted** | Auth tokens, passwords, payment IDs | hashed/encrypted | Until revoked | Code-only access |

### 14.2 Data Residency
- **Primary**: MongoDB Atlas — **Mumbai (ap-south-1) region**
- **Object storage**: Cloudflare R2 — Mumbai or Singapore (configurable)
- **Backups**: Encrypted backups stored in same-region (R2 archive)
- **No cross-border transfer** without explicit customer consent (gov / regulated industries)

### 14.3 Tenant Data Isolation
- **Logical**: enforced via `client_id` in every query (Bible §15)
- **Physical**: same database, separate collections per tenant feasible for ≥₹10L ACV customers
- **No tenant can query another tenant's data** (verified by 122 tests)

### 14.4 PII Handling
| PII Field | Storage | Encryption | Retention |
|---|---|---|---|
| Email | plain (lowercase) | At-rest (Atlas) | Until account deletion |
| Password | bcrypt hash (12 rounds) | Inherent | Forever (one-way) |
| Phone | E.164 plain | At-rest | Until account deletion |
| Name | plain | At-rest | Until account deletion |
| GSTIN | plain | At-rest | 7 years (legal retention) |
| Razorpay payment ID | plain (low-risk) | At-rest | 7 years (audit) |

### 14.5 Customer Data Rights
| Right | How to Exercise | SLA |
|---|---|---|
| **Access** (export own data) | Email `support@scn.in` or self-serve (P2) | 30 days |
| **Rectification** | Self-serve via UI | Immediate |
| **Deletion** (Right to be Forgotten) | Email + signed authorisation | 30 days (subject to legal retention exceptions) |
| **Portability** | Export to CSV/JSON | 30 days |
| **Object to processing** | Email + cancel contract | 30 days |

### 14.6 Audit & Compliance
- **All data access by super_admin** logged in `audit_logs` (Bible §16)
- **Quarterly access review**: who has DB credentials, R2 keys, .env access
- **Annual external audit** (ISO 27001 candidacy by Year 2)

### 14.7 Data Breach Protocol
1. Detect (alert from monitoring or report)
2. Contain within 1 hour (revoke keys, block IPs)
3. Assess scope within 4 hours (query audit logs)
4. Notify affected customers within 72 hours (regulatory requirement)
5. Notify CERT-In within 6 hours (Indian law)
6. Post-mortem RCA + remediation within 7 days

### 14.8 Third-Party Data Sharing
| Vendor | Data Shared | Purpose | DPA Signed |
|---|---|---|:-:|
| Razorpay | Customer email, amount | Payment processing | ✅ (standard) |
| Resend | Recipient email, content | Email delivery | ✅ |
| Meta WhatsApp | Phone, template content | Notification delivery | ✅ |
| MSG91 | Phone, SMS content | SMS delivery | ✅ |
| Cloudflare R2 | Document files | Storage | ✅ |
| MongoDB Atlas | All data | Database hosting | ✅ |

---

## 15. Annual Product Governance Calendar

### 15.1 Quarterly Anchors
| Quarter | Focus | Deliverables |
|---|---|---|
| **Q1 (Apr–Jun)** | Annual planning + strategic roadmap | Updated Bible, OKRs published, Board review |
| **Q2 (Jul–Sep)** | Mid-year review + customer expansion | NPS survey, QBRs with top 20, partner summit |
| **Q3 (Oct–Dec)** | Reliability + scale | Pentest, DR drill, capacity planning, ISO audit prep |
| **Q4 (Jan–Mar)** | Annual close + planning | Financial audit, GST returns, next-year budget |

### 15.2 Month-by-Month Calendar
| Month | Activity | Owner |
|---|---|---|
| **January** | Annual board meeting; budget approval; team appraisals | Founder + CFO |
| **February** | Year-on-year retrospective; partner summit | All-hands |
| **March** | GST annual return prep; financial audit kickoff | Finance |
| **April** | New financial year kickoff; new roadmap published | Founder + Product |
| **May** | Q1 KPI review; CSM playbook refresh | CS Lead |
| **June** | Mid-year hiring review; security pentest | HR + CTO |
| **July** | Half-year board update; OKR mid-year check | Founder |
| **August** | NPS survey + customer reviews | CS Lead |
| **September** | Partner program review; commission audit | Partner Manager |
| **October** | DR drill + BCP simulation | DevOps |
| **November** | Year-end planning workshop; pricing review | Sales + Founder |
| **December** | Annual customer summit; case studies finalised | Marketing |

### 15.3 Compliance Calendar (India-specific)
| Period | Activity | Owner |
|---|---|---|
| 10th of each month | GSTR-1 (outward supplies) filing | Finance |
| 20th of each month | GSTR-3B summary return + payment | Finance |
| 7th of each month | TDS on partner commissions | Finance |
| 30 April | GSTR-9 annual return | Finance |
| 31 July / 30 September | Income tax return (individual / company) | Finance |
| Within 30 days of FY end | Filing of financials with ROC (MCA) | Legal |
| Continuous | DLT template renewals (MSG91) | Product |
| Annually | Meta WhatsApp template review | Product |
| Annually | Razorpay KYC re-verification | Finance |
| Annually | Cloudflare R2 invoice + tax certificates | Finance |

### 15.4 Governance Meetings
| Meeting | Cadence | Attendees | Output |
|---|---|---|---|
| **All-hands** | Weekly (30 min) | All employees | Status, blockers |
| **Founder ↔ CTO 1:1** | Weekly (45 min) | Founder + CTO | Tech & product alignment |
| **Sales pipeline** | Weekly (45 min) | Sales team | Forecast |
| **CS health review** | Daily standup (15 min) | CS team | Account actions |
| **Product roadmap review** | Bi-weekly | Founder + Product + Engineering | Backlog priorities |
| **Risk review** | Monthly (60 min) | Leadership | Updated Risk Register |
| **Board meeting** | Quarterly (3 hours) | Board + Founder + CFO | Minutes + decisions |
| **Strategic offsite** | Annually (2 days) | Leadership | Vision for next year |

### 15.5 Release Cadence
- **Patch releases (v1.4.X)**: as needed, hotfix < 24 hours
- **Minor releases (v1.X.0)**: every 6–8 weeks (Phase-aligned)
- **Major releases (vX.0.0)**: annually, with breaking-change migration guide

### 15.6 Documentation Maintenance
| Document | Refresh Cadence | Owner |
|---|---|---|
| Product Bible | Per-release | Engineering |
| Business OS (this doc) | Quarterly | Founder + Ops |
| Closure Report | Per-major-release | Engineering |
| Changelog | Per-release | Engineering |
| Help Center | Weekly | CSM |
| Sales pitch deck | Quarterly | Sales |
| Partner kit | Quarterly | Partner Manager |
| Customer case studies | Continuous (1/month target) | Marketing |

---

## 📎 APPENDIX — Master Document Index

| Document | Path | Audience | Status |
|---|---|---|:-:|
| **SCN Product Bible** | `/app/SCN_PRODUCT_BIBLE.md` | Engineering | ✅ v1.4 |
| **SCN Business OS** | `/app/SCN_BUSINESS_OS.md` | Operations / Leadership | ✅ This file |
| **v1.4 Closure Report** | `/app/CLOSURE_REPORT_v1.4.md` | Leadership / Audit | ✅ |
| **Changelog** | `/app/CHANGELOG.md` | Engineering | ✅ |
| **PRD** | `/app/memory/PRD.md` | Product | ✅ |
| **Test Credentials** | `/app/memory/test_credentials.md` | QA / Engineering | ✅ |
| **Help Center content** | `/app/frontend/src/lib/helpContent.js` | End users | ✅ |
| Sales pitch deck | (to create) | Sales | 🔲 |
| Partner pitch deck | (to create) | Partner Manager | 🔲 |
| Customer onboarding checklist | (this doc §8) | CSM | ✅ Embedded |
| Tender response template | (to create from §3.4) | Government Sales | 🔲 |
| Privacy Policy | (in /terms route) | Legal | ⚠️ Refresh annually |
| Terms of Service | (in /terms route) | Legal | ⚠️ Refresh annually |

---

**END OF SCN BUSINESS OS**

*This document is the operational counterpart to the technical Product Bible. Both together = complete SCN runbook. Update quarterly.*

*© 2026 Securrise Solution Pvt Ltd. All rights reserved.*
