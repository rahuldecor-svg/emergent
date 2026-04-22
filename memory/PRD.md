# Fire Compliance OS — PRD

## Original Problem
"Fire Compliance OS" — enterprise SaaS owned by SSPL. Multi-tenant fire-safety compliance OS.

## Architecture (v1.3 — Phase 5)
Backend: FastAPI + Motor + APScheduler · 15 routers · `core/` helpers
Frontend: React 19 + Tailwind + shadcn · responsive + PWA · html5-qrcode · recharts · reportlab

## Timeline
- **v1.0 MVP** → 34 tests
- **v1.0.1 stabilisation** → 52
- **v1.1 Phase-2** (wallet deduction, email, upload, revocation, revenue, refactor) → 65
- **v1.2 Phase-3** (AMC Book Service, scheduler, onboarding, PDF, demo, severity, support) → 86
- **v1.2.1 Phase-4** (asset master, QR PDF, Help Center EN/HI, Terms, friendly errors) → 100
- **v1.3 Phase-5** (PWA, mobile responsive, QR scan, install prompt, quick-pass inspection) → **100 backend + 17 Phase-5 frontend assertions**

## Phase-5 Deliverables (all shipped, all tested)
1. **PWA** — `manifest.json`, `icon.svg`, `service-worker.js`, Apple web-app meta tags, SW registered on load, network-first shell cache, `/api/` skipped.
2. **Install prompt** — `InstallPrompt.jsx` listens to `beforeinstallprompt`, banner with Install/Not-now, 7-day dismissal memory.
3. **Mobile responsive** — `AppShell.jsx` now has hamburger top bar, slide-in drawer, desktop sidebar preserved at ≥768px, all interactive elements ≥44px touch target, viewport-fit=cover.
4. **QR scan via camera** — `/app/scan` page using `html5-qrcode`; prefers rear camera; manual URL/ID paste fallback; regex-extracts UUID from full asset URL.
5. **Field usability** — Quick-Pass inspection button on AssetDetail (1-tap pass inspection). Mark Done on maintenance (from Phase-1).
6. **Performance** — All PWA static assets <1.5 KB each; no >1 MB blocking JS chunk; SW caches shell for repeat loads.

## Known Limitations (v1.3)
1. Resend email still log-only until `RESEND_API_KEY` is set
2. Uploads on local disk (single-node)
3. No WhatsApp/SMS · No real map tiles
4. Wallet recharge SSPL-manual only (no self-serve)
5. Scheduler in-process
6. PWA icons are SVG only — iOS prefers PNG fallbacks (works but not optimal)
7. QR camera requires HTTPS + user permission (standard browser constraint)
8. NeedHelpFab + Emergent badge are near each other in corner (cosmetic; no functional impact)

## Backlog
### P0
- Provide RESEND_API_KEY
- Generate PNG PWA icons (192/512) for iOS
### P1
- Self-serve recharge (Stripe/Razorpay)
- Object-storage for Document Vault
- White-label PDF + client logo
- CSV bulk import
- Server-side password reset flow
### P2 (deferred by user)
- Predictive AI · Android native · WhatsApp/SMS · Voice-note · White-label partner portal

See `/app/memory/test_credentials.md`.
