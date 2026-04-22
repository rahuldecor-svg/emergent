import { useEffect, useState } from "react";
import { http } from "@/lib/api";
import { PageHeader, Panel, Btn, Empty } from "@/components/ui-kit";

const SEV = {
  critical: { bar: "border-l-status-critical", dot: "bg-status-critical", label: "CRITICAL" },
  warning:  { bar: "border-l-status-warning",  dot: "bg-status-warning",  label: "WARNING"  },
  info:     { bar: "border-l-primary",         dot: "bg-primary",         label: "INFO"     },
};

export default function NotificationsPage() {
  const [data, setData] = useState({ items: [], unread: 0 });
  const [filter, setFilter] = useState("all");

  const load = async () => { const { data } = await http.get("/notifications"); setData(data); };
  useEffect(() => { load(); }, []);

  const markAll = async () => { await http.post("/notifications/read-all"); load(); };
  const markOne = async (id) => { await http.post(`/notifications/${id}/read`); load(); };

  const filtered = data.items.filter(n => {
    const sev = n.severity || "info";
    return filter === "all" ? true : sev === filter;
  });

  const counts = { critical: 0, warning: 0, info: 0 };
  data.items.forEach(n => { counts[n.severity || "info"] = (counts[n.severity || "info"] || 0) + 1; });

  return (
    <div>
      <PageHeader
        eyebrow="Alerts" title="Notifications"
        subtitle="Compliance-critical updates, incidents and wallet events — prioritised by severity."
        actions={data.unread ? <Btn onClick={markAll} data-testid="mark-all-read">Mark all read</Btn> : null}
      />
      <div className="flex gap-2 mb-4" data-testid="severity-filters">
        {["all", "critical", "warning", "info"].map(f => (
          <button key={f} onClick={() => setFilter(f)}
            data-testid={`filter-${f}`}
            className={`px-3 py-1.5 text-xs uppercase font-semibold border ${
              filter === f ? "bg-primary text-primary-foreground border-primary" : "border-border hover:bg-secondary"
            }`}>
            {f} {f !== "all" && <span className="ml-1 mono">{counts[f] || 0}</span>}
          </button>
        ))}
      </div>
      <div className="panel">
        {filtered.length === 0 ? <Empty>All clear. No alerts.</Empty> :
          filtered.map(n => {
            const sev = SEV[n.severity || "info"];
            return (
              <div key={n.id}
                className={`p-4 border-b border-border last:border-0 border-l-4 ${sev.bar} flex justify-between items-start gap-3 ${!n.read ? "bg-secondary" : ""}`}
                data-testid={`notif-${n.id}`}>
                <div>
                  <div className="flex items-center gap-2">
                    <span className={`w-1.5 h-1.5 ${sev.dot} ${!n.read ? "animate-pulse-dot" : ""}`} />
                    <span className="overline text-muted-foreground">{sev.label} · {n.kind}</span>
                  </div>
                  <div className="font-semibold text-sm mt-1">{n.title}</div>
                  <div className="text-xs text-muted-foreground mt-1">{n.body}</div>
                  <div className="mono text-[10px] text-muted-foreground mt-1">{n.created_at.slice(0,16).replace("T"," ")}</div>
                </div>
                {!n.read && <Btn variant="outline" onClick={() => markOne(n.id)}>Mark read</Btn>}
              </div>
            );
          })}
      </div>
    </div>
  );
}
