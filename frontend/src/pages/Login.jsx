import { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { Link, useNavigate } from "react-router-dom";
import { Flame, ArrowRight } from "lucide-react";
import { formatApiError } from "@/lib/api";

export default function Login() {
  const { login } = useAuth();
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e) => {
    e.preventDefault();
    setErr(""); setLoading(true);
    try {
      const u = await login(email.trim().toLowerCase(), password);
      nav(u.role === "super_admin" ? "/app/sspl" : "/app/dashboard");
    } catch (e) {
      setErr(formatApiError(e.response?.data?.detail) || e.message);
    } finally { setLoading(false); }
  };

  const quick = (e, p) => { setEmail(e); setPassword(p); };

  return (
    <div className="min-h-screen grid md:grid-cols-2">
      <div className="hidden md:flex relative bg-primary text-primary-foreground p-12 flex-col justify-between overflow-hidden">
        <div className="absolute inset-0 bg-grid opacity-[0.08]" />
        <Link to="/" className="relative flex items-center gap-2" data-testid="login-brand">
          <Flame size={20} /><span className="font-heading font-black tracking-tight">FIRE COMPLIANCE OS</span>
        </Link>
        <div className="relative">
          <div className="overline opacity-70">System Access</div>
          <div className="font-heading font-black tracking-tighter text-5xl leading-tight mt-4">
            Every site.<br/>Every asset.<br/>Under control.
          </div>
          <p className="mt-6 opacity-80 max-w-md text-sm">
            The enterprise OS for fire compliance — owned and operated by Securrise Solution Pvt Ltd.
          </p>
        </div>
        <div className="relative mono text-xs opacity-70">v1.0 · SECURRISE SOLUTION PVT LTD</div>
      </div>

      <div className="flex items-center justify-center p-8 bg-background">
        <form onSubmit={onSubmit} className="w-full max-w-md" data-testid="login-form">
          <div className="overline text-muted-foreground">SECURE SIGN IN</div>
          <h1 className="font-heading font-black tracking-tighter text-4xl mt-2">Access Platform</h1>
          <p className="text-sm text-muted-foreground mt-2">Authorised personnel only.</p>

          <div className="mt-8 space-y-4">
            <div>
              <label className="overline block mb-2">Email</label>
              <input
                data-testid="login-email-input"
                className="w-full bg-card border border-input px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                type="email" value={email} onChange={e => setEmail(e.target.value)} required autoFocus
              />
            </div>
            <div>
              <label className="overline block mb-2">Password</label>
              <input
                data-testid="login-password-input"
                className="w-full bg-card border border-input px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                type="password" value={password} onChange={e => setPassword(e.target.value)} required
              />
            </div>
            {err && <div className="text-sm text-destructive border border-destructive/30 p-2" data-testid="login-error">{err}</div>}
            <button
              disabled={loading}
              type="submit"
              data-testid="login-submit-btn"
              className="w-full bg-primary text-primary-foreground font-semibold py-3 inline-flex items-center justify-center gap-2 hover:bg-slate-900 transition-transform active:scale-95 disabled:opacity-50"
            >
              {loading ? "Authenticating…" : <>Sign In <ArrowRight size={16} /></>}
            </button>
          </div>

          <div className="mt-10 border-t border-border pt-6">
            <div className="overline text-muted-foreground mb-3">Demo Accounts</div>
            <div className="grid grid-cols-1 gap-2 text-xs">
              {[
                ["SSPL Super Admin", "superadmin@sspl.in", "Sspl@12345"],
                ["Client Admin", "admin@acme.in", "Acme@12345"],
                ["Fire Officer", "officer@acme.in", "Officer@123"],
                ["Technician", "tech@acme.in", "Tech@12345"],
              ].map(([label, e, p]) => (
                <button type="button" key={e}
                  onClick={() => quick(e, p)}
                  data-testid={`demo-${e.split("@")[0]}-btn`}
                  className="flex justify-between items-center border border-border px-3 py-2 hover:bg-secondary text-left">
                  <span className="font-semibold">{label}</span>
                  <span className="mono text-muted-foreground">{e}</span>
                </button>
              ))}
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
