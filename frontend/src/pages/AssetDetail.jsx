import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { http } from "@/lib/api";
import { PageHeader, Panel, StatusPill, Btn, Empty } from "@/components/ui-kit";
import { QRCodeSVG } from "qrcode.react";
import { Modal, Field } from "./ClientsAdmin";
import { toast } from "sonner";

export default function AssetDetail() {
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [showInsp, setShowInsp] = useState(false);

  const load = async () => {
    const { data } = await http.get(`/assets/${id}`);
    setData(data);
  };
  useEffect(() => { load(); }, [id]);

  if (!data) return <div className="mono text-sm">LOADING ASSET…</div>;
  const a = data.asset;

  return (
    <div>
      <PageHeader
        eyebrow="Asset / QR Intelligence"
        title={a.name}
        subtitle={`${a.category.toUpperCase()} · ${a.sub_type || ""}`}
        actions={<>
          <Link to="/app/assets" className="text-xs overline text-muted-foreground hover:text-primary">← Back</Link>
          <Btn onClick={() => setShowInsp(true)} data-testid="log-inspection-btn">+ Log Inspection</Btn>
        </>}
      />
      <div className="grid md:grid-cols-3 gap-6">
        <Panel title="Identity">
          <dl className="text-sm space-y-2">
            {[
              ["Serial", a.serial_number],
              ["Manufacturer", a.manufacturer],
              ["Installed", a.install_date],
              ["Expiry", a.expiry_date],
              ["Location", a.location_note],
              ["Last Inspected", a.last_inspected?.slice(0,10) || "—"],
              ["Last Maintained", a.last_maintained?.slice(0,10) || "—"],
            ].map(([k, v]) => (
              <div key={k} className="flex justify-between gap-4 border-b border-border pb-1">
                <dt className="overline text-muted-foreground">{k}</dt>
                <dd className="mono text-right">{v || "—"}</dd>
              </div>
            ))}
            <div className="pt-2"><StatusPill value={a.status}>{a.status}</StatusPill></div>
          </dl>
        </Panel>

        <Panel title="QR Tag" className="flex items-center justify-center">
          <div className="text-center">
            <div className="bg-white p-4 inline-block border border-border">
              <QRCodeSVG value={`${window.location.origin}/app/assets/${a.id}`} size={160} />
            </div>
            <div className="mono text-xs mt-3 break-all">ASSET-{a.id.slice(0,8).toUpperCase()}</div>
            <div className="overline text-muted-foreground mt-1">Scan to view full history</div>
          </div>
        </Panel>

        <Panel title="Geo">
          <dl className="text-sm space-y-2">
            <div className="flex justify-between"><dt className="overline text-muted-foreground">Latitude</dt><dd className="mono">{a.lat ?? "—"}</dd></div>
            <div className="flex justify-between"><dt className="overline text-muted-foreground">Longitude</dt><dd className="mono">{a.lng ?? "—"}</dd></div>
          </dl>
          <div className="aspect-square bg-grid-sm mt-4 relative">
            {a.lat && <div className="absolute w-3 h-3 bg-destructive animate-pulse-dot" style={{ left: "48%", top: "48%" }} />}
          </div>
        </Panel>
      </div>

      <div className="grid md:grid-cols-2 gap-6 mt-6">
        <Panel title="Inspection Log">
          {data.inspections.length === 0 ? <Empty>No inspections yet.</Empty> :
            data.inspections.map(i => (
              <div key={i.id} className="border-b border-border py-2 last:border-0">
                <div className="flex justify-between items-center">
                  <div>
                    <div className="text-sm font-semibold">{i.inspector_name}</div>
                    <div className="mono text-xs text-muted-foreground">{i.created_at.slice(0,16).replace("T"," ")}</div>
                  </div>
                  <StatusPill value={i.overall_result}>{i.overall_result}</StatusPill>
                </div>
                {i.notes && <div className="text-xs mt-1 text-muted-foreground">{i.notes}</div>}
              </div>
            ))}
        </Panel>
        <Panel title="Maintenance Log">
          {data.maintenance.length === 0 ? <Empty>No maintenance tasks yet.</Empty> :
            data.maintenance.map(t => (
              <div key={t.id} className="border-b border-border py-2 last:border-0 flex justify-between items-center">
                <div>
                  <div className="text-sm">{t.notes}</div>
                  <div className="mono text-xs text-muted-foreground">Scheduled {t.scheduled_date}</div>
                </div>
                <StatusPill value={t.status}>{t.status}</StatusPill>
              </div>
            ))}
        </Panel>
      </div>

      {showInsp && <InspectionModal asset={a} onClose={() => setShowInsp(false)} onDone={() => { setShowInsp(false); load(); }} />}
    </div>
  );
}

function InspectionModal({ asset, onClose, onDone }) {
  const defaultChecks = {
    extinguisher: ["Pressure gauge in green", "Seal intact", "Nozzle clear", "Hose integrity"],
    hydrant: ["Valve operational", "Pressure adequate", "Coupling intact"],
    sprinkler: ["Head unobstructed", "No corrosion", "Spray pattern test"],
    alarm: ["Battery backup", "Audible test pass", "Detector clean"],
    hose: ["No cracks/abrasions", "Correctly reeled"],
    other: ["Visual check OK"],
  }[asset.category] || ["Visual check OK"];

  const [items, setItems] = useState(defaultChecks.map(i => ({ item: i, ok: true, note: "" })));
  const [inspector, setInspector] = useState("");
  const [notes, setNotes] = useState("");
  const overall = items.every(i => i.ok) ? "pass" : "fail";

  const submit = async (e) => {
    e.preventDefault();
    try {
      await http.post("/inspections", {
        asset_id: asset.id, checklist: items, overall_result: overall,
        inspector_name: inspector, notes,
      });
      toast.success(`Inspection logged: ${overall.toUpperCase()}`);
      onDone();
    } catch { toast.error("Failed"); }
  };

  return (
    <Modal title={`Inspect: ${asset.name}`} onClose={onClose}>
      <form onSubmit={submit} className="space-y-3">
        <Field label="INSPECTOR NAME" value={inspector} onChange={setInspector} required />
        <div className="border border-border">
          {items.map((it, idx) => (
            <label key={idx} className="flex items-center gap-3 px-3 py-2 border-b border-border last:border-0 cursor-pointer">
              <input type="checkbox" checked={it.ok}
                onChange={e => setItems(prev => prev.map((x, i) => i === idx ? {...x, ok: e.target.checked} : x))}
                className="w-4 h-4 accent-primary" />
              <span className="text-sm flex-1">{it.item}</span>
              <StatusPill value={it.ok ? "pass" : "fail"}>{it.ok ? "OK" : "FAIL"}</StatusPill>
            </label>
          ))}
        </div>
        <div>
          <label className="overline block mb-1">NOTES</label>
          <textarea value={notes} onChange={e => setNotes(e.target.value)} rows={2}
            className="w-full border border-input bg-card px-3 py-2 text-sm" />
        </div>
        <div className="flex justify-between items-center pt-3 border-t border-border">
          <div>Result: <StatusPill value={overall}>{overall}</StatusPill></div>
          <Btn type="submit" data-testid="submit-inspection">Submit</Btn>
        </div>
      </form>
    </Modal>
  );
}
