import { useEffect, useState } from "react";
import { http } from "@/lib/api";
import { PageHeader, Panel, StatusPill, Empty } from "@/components/ui-kit";
import { Link } from "react-router-dom";
import { LineChart, Line, ResponsiveContainer, XAxis, YAxis, Tooltip, ReferenceLine } from "recharts";

export default function ClientDashboard() {
  const [score, setScore] = useState(null);
  const [noc, setNoc] = useState([]);
  const [amc, setAmc] = useState(null);
  const [assets, setAssets] = useState([]);

  useEffect(() => {
    (async () => {
      const [a, b, c, d] = await Promise.all([
        http.get("/compliance/score"),
        http.get("/compliance/noc"),
        http.get("/compliance/amc-opportunities"),
        http.get("/assets"),
      ]);
      setScore(a.data); setNoc(b.data); setAmc(c.data); setAssets(d.data);
    })();
  }, []);

  if (!score) return <div className="mono text-sm">INITIALIZING DASHBOARD…</div>;

  return (
    <div>
      <PageHeader
        eyebrow="Client / Dashboard"
        title="Compliance Command"
        subtitle="Live fire safety posture across your sites."
      />
      <div className="grid md:grid-cols-3 gap-6 mb-6">
        <Panel title="Fire Safety Score" className="md:col-span-1" data-testid="fire-score-gauge">
          <div className="p-2">
            <div className="num text-8xl leading-none" data-testid="score-value">{score.score}</div>
            <div className="mt-2"><StatusPill value={score.status}>{score.status}</StatusPill></div>
            <div className="h-2 mt-5 bg-accent relative">
              <div
                className={`absolute left-0 top-0 bottom-0 ${
                  score.status === "safe" ? "bg-status-success" :
                  score.status === "warning" ? "bg-status-warning" : "bg-status-critical"
                }`}
                style={{ width: `${score.score}%` }}
              />
            </div>
            <div className="grid grid-cols-3 text-center text-xs mt-4 divide-x divide-border">
              <div><div className="num text-2xl text-status-critical">{score.expired_assets}</div>Expired</div>
              <div><div className="num text-2xl text-status-warning">{score.missed_maintenance}</div>Missed</div>
              <div><div className="num text-2xl">{score.total_assets}</div>Assets</div>
            </div>
          </div>
        </Panel>

        <Panel title="Score Trend (6 mo)" className="md:col-span-2">
          <div style={{ width: "100%", height: 220 }}>
            <ResponsiveContainer>
              <LineChart data={score.trend}>
                <XAxis dataKey="month" stroke="hsl(var(--muted-foreground))" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 100]} stroke="hsl(var(--muted-foreground))" tick={{ fontSize: 11 }} />
                <Tooltip contentStyle={{ background: "white", border: "1px solid hsl(var(--border))", borderRadius: 0 }} />
                <ReferenceLine y={85} stroke="hsl(var(--status-success))" strokeDasharray="3 3" />
                <ReferenceLine y={60} stroke="hsl(var(--status-warning))" strokeDasharray="3 3" />
                <Line type="monotone" dataKey="score" stroke="hsl(var(--primary))" strokeWidth={2} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </div>

      <div className="grid md:grid-cols-2 gap-6 mb-6">
        <Panel title="NOC Readiness" action={<Link to="/app/compliance" className="overline text-muted-foreground hover:text-primary">View all →</Link>}>
          {noc.length === 0 ? <Empty>No sites yet.</Empty> : noc.map(s => (
            <div key={s.site.id} className="flex items-center justify-between py-2 border-b border-border last:border-0">
              <div>
                <div className="font-semibold text-sm">{s.site.name}</div>
                <div className="text-xs text-muted-foreground mono">{s.progress}% complete</div>
              </div>
              <StatusPill value={s.ready ? "safe" : "warning"}>{s.ready ? "Ready" : "Not Ready"}</StatusPill>
            </div>
          ))}
        </Panel>

        <Panel title="AMC Opportunities" action={<span className="num text-2xl text-destructive">₹{amc?.total_opportunity_value || 0}</span>}>
          <div className="grid grid-cols-3 text-center text-xs mb-3 divide-x divide-border">
            <div><div className="num text-2xl text-status-critical">{amc?.expired.length || 0}</div>Expired</div>
            <div><div className="num text-2xl text-status-warning">{amc?.expiring.length || 0}</div>Expiring</div>
            <div><div className="num text-2xl text-status-warning">{amc?.missed.length || 0}</div>Missed</div>
          </div>
          <div className="text-xs text-muted-foreground mono">Auto-generated upsell candidates. Convert from Compliance Center.</div>
        </Panel>
      </div>

      <Panel title="Recent Assets">
        {assets.length === 0 ? <Empty>No assets. Add one from Assets page.</Empty> : (
          <table className="w-full text-sm">
            <thead><tr className="border-b border-border text-left">
              <th className="overline py-2">Name</th><th className="overline">Category</th>
              <th className="overline">Serial</th><th className="overline">Expiry</th><th className="overline">Status</th>
            </tr></thead>
            <tbody>
              {assets.slice(0, 8).map(a => (
                <tr key={a.id} className="border-b border-border last:border-0">
                  <td className="py-2"><Link to={`/app/assets/${a.id}`} className="font-semibold hover:underline">{a.name}</Link></td>
                  <td className="uppercase mono text-xs">{a.category}</td>
                  <td className="mono text-xs">{a.serial_number}</td>
                  <td className="mono text-xs">{a.expiry_date}</td>
                  <td><StatusPill value={a.expiry_status}>{a.expiry_status}</StatusPill></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Panel>
    </div>
  );
}
