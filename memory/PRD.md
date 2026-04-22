# Fire Compliance OS — PRD

## Original Problem Statement
Build a category-defining, enterprise-grade SaaS platform "Fire Compliance OS" fully owned, controlled, and operated by Securrise Solution Pvt Ltd (SSPL) — the central operating system for fire safety compliance, maintenance, audits and risk intelligence. Multi-tenant, API-first, clients never miss compliance, SSPL always controls the ecosystem.

## User Choices
- MVP: 1a · Core web platform (deep, not wide)
- Intelligence: 2b · No AI — rule-based scoring
- Payments: 3c · Manual wallet recharge only
- Auth: 4a · JWT email + password
- Notifications: 5a · In-app + Email (Resend infra; key deferred)

## Implemented (v1.0 — stabilised 2026-04-22)
- SSPL command center + clients mgmt + kill-switch + manual wallet recharge with GST invoice + audit log
- Client dashboards with Fire Safety Score (0–100, rule-based, 6-mo trend) + NOC Readiness + AMC Conversion
- Asset Management + QR tags + Inspection (dynamic checklist, fail auto-alerts) + Maintenance + Emergency/Incidents
- Risk Map + Wallet + Document Vault + Notifications + Sites + Users
- JWT httpOnly cookies, bcrypt(12) passwords, brute-force lockout, tenant_filter() on every client-scoped route

## Test Status
- **Iteration 1:** 34/34 backend + full frontend smoke — green
- **Iteration 2 (stabilization):** 51/51 backend + 12/12 routes frontend — green
- 2 real bugs found and fixed during iteration 2 (NOC cross-tenant leak · GST invoice collision)
- 1 correctness fix applied after iteration 2 (wallet recharge amount > 0 Pydantic validation)
- 1 UX guard applied after iteration 2 (SSPL dashboards wrap 403 with toast instead of error overlay)

## Known Limitations (v1.0)
1. Resend email = log-only until `RESEND_API_KEY` is set
2. No object storage — Document Vault accepts URLs only
3. No native/offline Android app (web-responsive only)
4. No WhatsApp/SMS channels
5. Risk map uses coord-plot, not real map tiles
6. Access token valid full 8h post-logout (cookie cleared; no server revocation list)
7. Brute-force key uses ingress-proxy IP
8. Usage-based wallet deduction (per asset / inspection / user) NOT implemented — manual credit only
9. `GET /api/wallet` for super_admin returns 0 (no aggregation)
10. `server.py` ~840 lines single-file; not yet split into routers

## Backlog
### P0 (stability)
- [ ] Refresh-token rotation + server-side revocation list
- [ ] Aggregate super_admin wallet total
- [ ] Split `server.py` into routers
### P1
- [ ] Usage-based wallet deduction + grace mode + auto-restriction at ₹0
- [ ] Wire Resend
- [ ] Object storage for Document Vault
- [ ] Bulk asset CSV import
- [ ] Role-scoped audit view for client_admins
### P2 (deferred by user)
- [ ] Predictive AI risk engine
- [ ] Android + offline sync
- [ ] WhatsApp/SMS (Twilio)
- [ ] Voice-note Hindi/English inspection
- [ ] White-label partner portal

## Next Actions
1. Implement usage-based wallet deduction (P1)
2. Provide RESEND_API_KEY → go live on emails
3. Pick object-storage provider → enable Vault uploads
4. Split server.py into routers for maintainability
