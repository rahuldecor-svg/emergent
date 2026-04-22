import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { useEffect, useState } from "react";
import { http } from "@/lib/api";
import { toast } from "sonner";
import {
  Flame, LayoutDashboard, Package, Clipboard, Wrench, Siren, Wallet,
  FileText, MapPin, Bell, Users, Building2, ShieldCheck, LogOut, Gauge,
  LifeBuoy, RotateCcw,
} from "lucide-react";

const ROLE_LABEL = {
  super_admin: "SSPL Super Admin",
  client_admin: "Client Admin",
  fire_officer: "Fire Officer",
  technician: "Technician",
  auditor: "Auditor",
  partner: "Partner",
};

export default function AppShell() {
  const { user, logout } = useAuth();
  const nav = useNavigate();
  const [unread, setUnread] = useState(0);

  useEffect(() => {
    let on = true;
    const load = async () => {
      try {
        const { data } = await http.get("/notifications");
        if (on) setUnread(data.unread);
      } catch { /* ignore */ }
    };
    load();
    const t = setInterval(load, 20000);
    return () => { on = false; clearInterval(t); };
  }, []);

  if (!user) return null;
  const isSuper = user.role === "super_admin";
  const isDemo = user.email === "demo@fire-os.in";

  const items = isSuper ? [
    { to: "/app/sspl", icon: LayoutDashboard, label: "Command" },
    { to: "/app/clients", icon: Building2, label: "Clients" },
    { to: "/app/notifications", icon: Bell, label: "Alerts", badge: unread },
  ] : [
    { to: "/app/dashboard", icon: Gauge, label: "Dashboard" },
    { to: "/app/assets", icon: Package, label: "Assets" },
    { to: "/app/inspections", icon: Clipboard, label: "Inspections" },
    { to: "/app/maintenance", icon: Wrench, label: "Maintenance" },
    { to: "/app/compliance", icon: ShieldCheck, label: "Compliance" },
    { to: "/app/risk-map", icon: MapPin, label: "Risk Map" },
    { to: "/app/incidents", icon: Siren, label: "Emergency" },
    { to: "/app/wallet", icon: Wallet, label: "Wallet" },
    { to: "/app/documents", icon: FileText, label: "Vault" },
    { to: "/app/sites", icon: Building2, label: "Sites" },
    { to: "/app/users", icon: Users, label: "Users" },
    { to: "/app/support", icon: LifeBuoy, label: "Support" },
    { to: "/app/notifications", icon: Bell, label: "Alerts", badge: unread },
  ];

  return (
    <div className="min-h-screen grid grid-cols-[240px_1fr] bg-background">
      {/* Sidebar */}
      <aside className="border-r border-border bg-card flex flex-col">
        <div className="p-4 border-b border-border">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 bg-primary grid place-items-center"><Flame size={14} className="text-primary-foreground" /></div>
            <div>
              <div className="font-heading font-black tracking-tight leading-none text-sm">FIRE OS</div>
              <div className="overline text-muted-foreground leading-none mt-1">by SSPL</div>
            </div>
          </div>
        </div>
        <nav className="flex-1 p-2 overflow-y-auto">
          {items.map(({ to, icon: Icon, label, badge }) => (
            <NavLink
              key={to} to={to}
              data-testid={`nav-${label.toLowerCase()}`}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 text-sm font-medium transition-colors ${
                  isActive ? "bg-primary text-primary-foreground" : "hover:bg-secondary"
                }`
              }
            >
              <Icon size={16} />
              <span className="flex-1">{label}</span>
              {badge ? <span className="min-w-5 h-5 px-1 grid place-items-center text-[10px] font-bold bg-destructive text-destructive-foreground">{badge}</span> : null}
            </NavLink>
          ))}
        </nav>
        <div className="p-3 border-t border-border">
          <div className="text-xs mb-2">
            <div className="font-semibold truncate">{user.name}</div>
            <div className="overline text-muted-foreground mt-0.5">{ROLE_LABEL[user.role]}</div>
            {isDemo && <div className="overline text-destructive mt-1">DEMO MODE</div>}
          </div>
          {isDemo && (
            <button
              data-testid="demo-reset-btn"
              onClick={async () => {
                if (!window.confirm("Reset demo data? This wipes and re-seeds the demo tenant.")) return;
                try {
                  await http.post("/demo/reset");
                  toast.success("Demo tenant reset");
                  window.location.reload();
                } catch { toast.error("Reset failed"); }
              }}
              className="w-full border border-border px-3 py-2 text-xs font-semibold inline-flex items-center justify-center gap-2 hover:bg-primary hover:text-primary-foreground transition-colors mb-2"
            >
              <RotateCcw size={12} /> Reset Demo
            </button>
          )}
          <button
            data-testid="logout-btn"
            onClick={async () => { await logout(); nav("/login"); }}
            className="w-full border border-border px-3 py-2 text-xs font-semibold inline-flex items-center justify-center gap-2 hover:bg-primary hover:text-primary-foreground transition-colors"
          >
            <LogOut size={12} /> Sign out
          </button>
        </div>
      </aside>
      <main className="min-w-0 overflow-x-hidden">
        <div className="p-6 md:p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
