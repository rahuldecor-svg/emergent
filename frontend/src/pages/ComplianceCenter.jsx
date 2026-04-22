import { useEffect, useState } from "react";
import { http } from "@/lib/api";
import { PageHeader, Panel, StatusPill, Empty } from "@/components/ui-kit";

export default function ComplianceCenter() {
  const [noc, setNoc] = useState([]);
  const [amc, setAmc] = useState(null);

  const load = async () => {
    const [a, b] = await Promise.all([http.get("/compliance/noc"), http.get("/compliance/amc-opportunities")]);
    setNoc(a.data); setAmc(b.data);
  };
  useEffect(() => { load(); }, []);

  const toggle = async (itemId, next) => {
    await http.patch(`/compliance/noc/${itemId}`, { completed: next });
    load();
  };

  return (
    <div>
      <PageHeader
        eyebrow="Compliance / Audit"
        title="Compliance Center"
        subtitle="NOC readiness and AMC conversion — the commercial face of compliance."
      />
      <div className="grid lg:grid-cols-5 gap-6 mb-6">
        <div className="lg:col-span-3 space-y-6">
          {noc.map(s => (
            <Panel key={s.site.id} title={`NOC · ${s.site.name}`} action={<StatusPill value={s.ready ? "safe" : "warning"}>{s.ready ? "Ready" : "Not Ready"}</StatusPill>}>
              <div className="h-2 bg-accent relative mb-3">
                <div className={`absolute left-0 top-0 bottom-0 ${s.ready ? "bg-status-success" : "bg-status-warning"}`} style={{ width: `${s.progress}%` }} />
              </div>
              <div className="divide-y divide-border">
                {s.checklist.map(it => (
                  <label key={it.id} className="flex items-center gap-3 py-2 cursor-pointer"
                    data-testid={`noc-${it.id}`}>
                    <input type="checkbox" checked={it.completed} onChange={e => toggle(it.id, e.target.checked)}
                      className="w-4 h-4 accent-primary" />
                    <span className="text-sm flex-1">{it.item}</span>
                    <StatusPill value={it.completed ? "pass" : "warning"}>{it.completed ? "Done" : "Pending"}</StatusPill>
                  </label>
                ))}
              </div>
            </Panel>
          ))}
          {noc.length === 0 && <Empty>No NOC checklists. Add sites first.</Empty>}
        </div>

        <div className="lg:col-span-2">
          <Panel title="AMC Conversion" action={<span className="num text-2xl text-destructive">₹{amc?.total_opportunity_value || 0}</span>}>
            <div className="text-xs text-muted-foreground mb-3 mono">Total opportunity value (suggested).</div>
            <Section label="Expired — Replace / Refill" items={amc?.expired} />
            <Section label="Expiring Soon" items={amc?.expiring} />
            <Section label="Missed Maintenance" items={amc?.missed} taskMode />
          </Panel>
        </div>
      </div>
    </div>
  );
}

function Section({ label, items = [], taskMode }) {
  if (!items.length) return null;
  return (
    <div className="mt-3">
      <div className="overline mb-2">{label}</div>
      <div className="divide-y divide-border border border-border">
        {items.slice(0, 6).map((o, i) => (
          <div key={i} className="flex justify-between items-center px-3 py-2 text-xs">
            <div className="truncate pr-2">
              <div className="font-semibold truncate">{taskMode ? o.task.notes : o.asset.name}</div>
              <div className="mono text-muted-foreground">{o.action}</div>
            </div>
            <div className="num text-xl">₹{o.suggested_price}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
