import { useEffect, useState } from "react";
import { http } from "@/lib/api";
import { PageHeader, Panel, StatusPill, Empty } from "@/components/ui-kit";

export default function RiskMap() {
  const [zones, setZones] = useState([]);
  const [sites, setSites] = useState([]);
  const [siteId, setSiteId] = useState("");

  const load = async () => {
    const [z, s] = await Promise.all([
      http.get("/compliance/risk-map", { params: siteId ? { site_id: siteId } : {} }),
      http.get("/sites"),
    ]);
    setZones(z.data); setSites(s.data);
  };
  useEffect(() => { load(); }, [siteId]);

  const currentSite = sites.find(s => s.id === siteId) || sites[0];
  const baseLat = currentSite?.lat || 18.52;
  const baseLng = currentSite?.lng || 73.85;
  const zoomed = zones.filter(z => z.lat && z.lng);
  // normalize to 0..1 within bounding box
  const lats = zoomed.map(z => z.lat);
  const lngs = zoomed.map(z => z.lng);
  const minLat = Math.min(...lats, baseLat); const maxLat = Math.max(...lats, baseLat) || (baseLat + 0.01);
  const minLng = Math.min(...lngs, baseLng); const maxLng = Math.max(...lngs, baseLng) || (baseLng + 0.01);

  const counts = { high: 0, medium: 0, low: 0 };
  zones.forEach(z => { counts[z.risk] = (counts[z.risk] || 0) + 1; });

  return (
    <div>
      <PageHeader
        eyebrow="Risk Intelligence"
        title="Live Risk Map"
        subtitle="Red zones, expired equipment, faulty systems — visually."
        actions={
          <select value={siteId} onChange={e => setSiteId(e.target.value)}
            data-testid="risk-site-filter"
            className="border border-input bg-card px-3 py-2 text-xs">
            <option value="">All Sites</option>
            {sites.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
        }
      />
      <div className="grid md:grid-cols-3 gap-px bg-border mb-6">
        <div className="bg-card p-4"><div className="overline text-muted-foreground">High Risk</div>
          <div className="num text-4xl text-status-critical">{counts.high}</div></div>
        <div className="bg-card p-4"><div className="overline text-muted-foreground">Medium</div>
          <div className="num text-4xl text-status-warning">{counts.medium}</div></div>
        <div className="bg-card p-4"><div className="overline text-muted-foreground">Low Risk</div>
          <div className="num text-4xl text-status-success">{counts.low}</div></div>
      </div>

      <Panel title="Site Layout">
        {zoomed.length === 0 ? <Empty>No geo-tagged assets.</Empty> :
          <div className="relative bg-grid aspect-[16/9] overflow-hidden">
            {zoomed.map(z => {
              const x = ((z.lng - minLng) / (maxLng - minLng || 1)) * 92 + 4;
              const y = 96 - ((z.lat - minLat) / (maxLat - minLat || 1)) * 92;
              const color = z.risk === "high" ? "bg-status-critical" : z.risk === "medium" ? "bg-status-warning" : "bg-status-success";
              return (
                <div key={z.asset_id}
                  className={`absolute w-3 h-3 ${color} ${z.risk === "high" ? "animate-pulse-dot" : ""}`}
                  style={{ left: `${x}%`, top: `${y}%` }}
                  title={`${z.name} · ${z.risk}`}
                  data-testid={`risk-dot-${z.risk}`}
                />
              );
            })}
          </div>}
      </Panel>

      <Panel title="Legend & List" className="mt-6">
        <div className="flex gap-4 mb-3 text-xs">
          <span className="flex gap-1 items-center"><span className="w-2 h-2 bg-status-critical" />High</span>
          <span className="flex gap-1 items-center"><span className="w-2 h-2 bg-status-warning" />Medium</span>
          <span className="flex gap-1 items-center"><span className="w-2 h-2 bg-status-success" />Low</span>
        </div>
        <table className="w-full text-sm">
          <thead><tr className="border-b border-border text-left">
            <th className="overline p-2">Asset</th><th className="overline">Category</th>
            <th className="overline">Expiry</th><th className="overline">Risk</th>
          </tr></thead>
          <tbody>
            {zones.map(z => (
              <tr key={z.asset_id} className="border-b border-border last:border-0">
                <td className="p-2 font-semibold">{z.name}</td>
                <td className="uppercase mono text-xs">{z.category}</td>
                <td className="mono text-xs">{z.expiry_date}</td>
                <td><StatusPill value={z.risk}>{z.risk}</StatusPill></td>
              </tr>
            ))}
          </tbody>
        </table>
      </Panel>
    </div>
  );
}
