import { Link } from "react-router-dom";
import { Flame, ShieldCheck, QrCode, Gauge, Siren, Wallet, ArrowRight, CheckCircle2 } from "lucide-react";

export default function Landing() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* NAV */}
      <header className="border-b border-border bg-background/80 backdrop-blur sticky top-0 z-30">
        <div className="max-w-7xl mx-auto flex items-center justify-between px-6 py-4">
          <Link to="/" className="flex items-center gap-2" data-testid="brand-link">
            <div className="w-8 h-8 bg-primary grid place-items-center">
              <Flame size={18} className="text-primary-foreground" />
            </div>
            <div>
              <div className="font-heading font-black tracking-tight leading-none">FIRE COMPLIANCE OS</div>
              <div className="overline text-muted-foreground leading-none mt-1">by SSPL</div>
            </div>
          </Link>
          <nav className="hidden md:flex items-center gap-8 text-sm">
            <a href="#modules" className="hover:text-primary">Modules</a>
            <a href="#score" className="hover:text-primary">Scoring</a>
            <a href="#pricing" className="hover:text-primary">Pricing</a>
          </nav>
          <Link
            to="/login"
            data-testid="nav-login-btn"
            className="px-4 py-2 bg-primary text-primary-foreground text-sm font-semibold hover:bg-slate-900 transition-transform active:scale-95"
          >
            Sign in →
          </Link>
        </div>
      </header>

      {/* HERO */}
      <section className="relative overflow-hidden border-b border-border">
        <div
          className="absolute inset-0 bg-cover bg-center opacity-90"
          style={{ backgroundImage: "url(https://images.pexels.com/photos/33706868/pexels-photo-33706868.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940)" }}
        />
        <div className="absolute inset-0 hero-overlay" />
        <div className="relative max-w-7xl mx-auto px-6 py-24 lg:py-32 grid md:grid-cols-12 gap-8">
          <div className="md:col-span-8">
            <div className="flex items-center gap-3 mb-6">
              <span className="pill border-primary text-primary bg-background">
                <span className="w-1.5 h-1.5 bg-status-success animate-pulse-dot" />
                OPERATIONAL
              </span>
              <span className="overline text-muted-foreground">v1.0 · Enterprise</span>
            </div>
            <h1 className="font-heading font-black tracking-tighter text-5xl sm:text-6xl lg:text-7xl leading-[0.95]">
              THE OPERATING<br/>SYSTEM FOR<br/>
              <span className="text-destructive">FIRE SAFETY</span><br/>
              COMPLIANCE.
            </h1>
            <p className="mt-8 text-base md:text-lg max-w-2xl text-foreground/80">
              One platform to manage every extinguisher, hydrant, inspection, audit and
              NOC across every site. Built for EHS heads, government auditors and plant
              managers — so nothing ever slips.
            </p>
            <div className="mt-10 flex flex-wrap gap-4">
              <Link
                to="/login"
                data-testid="hero-signin-btn"
                className="px-6 py-3 bg-primary text-primary-foreground font-semibold inline-flex items-center gap-2 hover:bg-slate-900 transition-transform active:scale-95"
              >
                Access Platform <ArrowRight size={16} />
              </Link>
              <a
                href="#modules"
                data-testid="hero-explore-btn"
                className="px-6 py-3 border border-primary font-semibold hover:bg-primary hover:text-primary-foreground transition-colors"
              >
                Explore Modules
              </a>
            </div>
          </div>
          <div className="md:col-span-4 hidden md:block">
            <div className="panel p-6 bg-background/90">
              <div className="overline text-muted-foreground">Live Metric</div>
              <div className="num text-7xl leading-none mt-2">92</div>
              <div className="text-sm mt-1">Fire Safety Score · Plant A</div>
              <div className="h-px bg-border my-4" />
              <div className="grid grid-cols-3 text-center gap-2 text-xs">
                <div><div className="num text-2xl text-status-success">18</div>SAFE</div>
                <div><div className="num text-2xl text-status-warning">4</div>WARN</div>
                <div><div className="num text-2xl text-status-critical">2</div>CRIT</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* MODULES */}
      <section id="modules" className="max-w-7xl mx-auto px-6 py-20">
        <div className="grid md:grid-cols-12 gap-8 mb-12">
          <div className="md:col-span-4">
            <div className="overline text-muted-foreground">01 / Platform</div>
            <h2 className="font-heading font-black tracking-tight text-4xl lg:text-5xl mt-2">
              Every asset.<br/>Every site.<br/>One system.
            </h2>
          </div>
          <p className="md:col-span-8 text-lg text-foreground/80 self-end">
            Fire Compliance OS unifies asset tracking, inspection, maintenance, audit,
            NOC readiness, wallet and emergency response — with SSPL retaining absolute
            ownership of the data, licenses and kill-switch.
          </p>
        </div>
        <div className="grid md:grid-cols-3 gap-px bg-border">
          {[
            { icon: QrCode, title: "QR Asset Intelligence", desc: "Every extinguisher, hydrant, sprinkler. Scan → full history, voice notes, photos." },
            { icon: Gauge, title: "Fire Safety Score", desc: "Real-time 0–100 score per site. Overdue, expired and failed events weigh the score." },
            { icon: ShieldCheck, title: "NOC Readiness", desc: "Checklist vs government norms. Know if you’re audit-ready in one glance." },
            { icon: Siren, title: "Emergency Mode", desc: "Log incidents, capture timeline, generate insurance-ready report." },
            { icon: Wallet, title: "Wallet & Billing", desc: "Prepaid wallet, GST invoices, subscription plans — all controlled by SSPL." },
            { icon: Flame, title: "AMC Conversion", desc: "System auto-detects expired gear and suggests service with price." },
          ].map(({ icon: Icon, title, desc }) => (
            <div key={title} className="bg-card p-6 hover:bg-secondary transition-colors">
              <Icon size={22} className="text-destructive" />
              <div className="font-heading font-bold text-lg mt-3">{title}</div>
              <div className="text-sm text-muted-foreground mt-2">{desc}</div>
            </div>
          ))}
        </div>
      </section>

      {/* SCORE */}
      <section id="score" className="border-y border-border bg-secondary">
        <div className="max-w-7xl mx-auto px-6 py-20 grid md:grid-cols-2 gap-12 items-center">
          <div>
            <div className="overline text-muted-foreground">02 / Scoring Engine</div>
            <h2 className="font-heading font-black tracking-tight text-4xl lg:text-5xl mt-2">
              If you can’t<br/>measure it,<br/>you can’t save it.
            </h2>
            <p className="mt-6 text-foreground/80 text-lg">
              A single number, updated every minute, that tells your plant, your board and your auditor
              exactly where you stand.
            </p>
            <ul className="mt-8 space-y-3">
              {["Weighted by expired gear, missed maintenance & failed inspections",
                "Historical trend across 12 months",
                "Site-level drilldown to the asset"].map(t => (
                <li key={t} className="flex items-start gap-3 text-sm">
                  <CheckCircle2 size={18} className="text-status-success mt-0.5 shrink-0" />{t}
                </li>
              ))}
            </ul>
          </div>
          <div className="panel p-8 bg-card">
            <div className="overline text-muted-foreground">Plant A · Pune</div>
            <div className="num text-9xl leading-none mt-4">92</div>
            <div className="mt-3 h-2 bg-accent relative">
              <div className="absolute left-0 top-0 bottom-0 bg-status-success" style={{ width: "92%" }} />
            </div>
            <div className="grid grid-cols-4 text-center mt-6 text-xs divide-x divide-border">
              <div className="px-2"><div className="num text-2xl">128</div>Assets</div>
              <div className="px-2"><div className="num text-2xl text-status-critical">3</div>Expired</div>
              <div className="px-2"><div className="num text-2xl text-status-warning">5</div>Missed</div>
              <div className="px-2"><div className="num text-2xl text-status-success">42</div>Inspections</div>
            </div>
          </div>
        </div>
      </section>

      {/* PRICING */}
      <section id="pricing" className="max-w-7xl mx-auto px-6 py-20">
        <div className="overline text-muted-foreground">03 / Plans</div>
        <h2 className="font-heading font-black tracking-tight text-4xl lg:text-5xl mt-2 mb-12">
          Plans built for every scale.
        </h2>
        <div className="grid md:grid-cols-3 gap-px bg-border">
          {[
            { name: "Basic", price: "₹4,999", per: "/site/mo", feats: ["Up to 100 assets", "QR + inspections", "Wallet + GST", "Email support"] },
            { name: "Pro", price: "₹12,999", per: "/site/mo", feats: ["Unlimited assets", "NOC + Risk Map", "AMC engine", "Priority support"], highlight: true },
            { name: "Enterprise", price: "Custom", per: "", feats: ["Multi-site rollout", "White-label", "API access", "Dedicated success"] },
          ].map(p => (
            <div key={p.name} className={`p-8 bg-card ${p.highlight ? "border-t-4 border-t-destructive" : ""}`}>
              <div className="overline">{p.name}</div>
              <div className="num text-5xl mt-2">{p.price}<span className="text-base text-muted-foreground mono"> {p.per}</span></div>
              <ul className="mt-6 space-y-2 text-sm">
                {p.feats.map(f => <li key={f} className="flex gap-2"><CheckCircle2 size={14} className="text-status-success mt-1 shrink-0" />{f}</li>)}
              </ul>
            </div>
          ))}
        </div>
      </section>

      {/* FOOTER */}
      <footer className="border-t border-border bg-primary text-primary-foreground">
        <div className="max-w-7xl mx-auto px-6 py-8 flex flex-wrap gap-4 items-center justify-between">
          <div className="flex items-center gap-2">
            <Flame size={16} /> <span className="font-heading font-bold tracking-tight">FIRE COMPLIANCE OS</span>
          </div>
          <div className="mono text-xs opacity-70">© SECURRISE SOLUTION PVT LTD · ALL RIGHTS RESERVED</div>
        </div>
      </footer>
    </div>
  );
}
