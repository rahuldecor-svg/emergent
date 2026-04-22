import { useEffect, useState } from "react";
import { http } from "@/lib/api";
import { PageHeader, Panel, StatusPill, Btn, Empty } from "@/components/ui-kit";
import { Modal, Field } from "./ClientsAdmin";
import { toast } from "sonner";
import { Siren } from "lucide-react";

export default function Incidents() {
  const [items, setItems] = useState([]);
  const [sites, setSites] = useState([]);
  const [show, setShow] = useState(false);

  const load = async () => {
    const [a, s] = await Promise.all([http.get("/incidents"), http.get("/sites")]);
    setItems(a.data); setSites(s.data);
  };
  useEffect(() => { load(); }, []);

  return (
    <div>
      <PageHeader
        eyebrow="Emergency / Incident Log"
        title="Emergency Mode"
        subtitle="Tap to log an incident with severity and timeline. Auto-notifies site admins."
        actions={<Btn variant="destructive" onClick={() => setShow(true)} data-testid="log-incident-btn">
          <Siren size={14} /> Log Incident
        </Btn>}
      />
      <div className="panel">
        {items.length === 0 ? <Empty>No incidents. Stay safe.</Empty> :
          items.map(i => (
            <div key={i.id} className="border-b border-border last:border-0 p-4" data-testid={`incident-${i.id}`}>
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <StatusPill value={i.severity}>{i.severity}</StatusPill>
                    <span className="mono text-xs text-muted-foreground">{i.created_at.slice(0,16).replace("T"," ")}</span>
                  </div>
                  <div className="font-heading font-bold text-lg">{i.title}</div>
                  <div className="text-sm text-muted-foreground mt-1">{i.description}</div>
                </div>
                <StatusPill value={i.status}>{i.status}</StatusPill>
              </div>
            </div>
          ))}
      </div>
      {show && <NewIncident sites={sites} onClose={() => setShow(false)} onDone={() => { setShow(false); load(); }} />}
    </div>
  );
}

function NewIncident({ sites, onClose, onDone }) {
  const [f, setF] = useState({ site_id: sites[0]?.id || "", title: "", severity: "high", description: "" });
  const submit = async (e) => {
    e.preventDefault();
    try { await http.post("/incidents", f); toast.success("Logged — admins alerted"); onDone(); }
    catch { toast.error("Failed"); }
  };
  return (
    <Modal title="Log Incident" onClose={onClose}>
      <form onSubmit={submit} className="space-y-3">
        <div>
          <label className="overline block mb-1">Site</label>
          <select className="w-full border border-input bg-card px-3 py-2 text-sm" value={f.site_id} onChange={e => setF({...f, site_id: e.target.value})}>
            {sites.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
        </div>
        <Field label="TITLE" value={f.title} onChange={v => setF({...f, title: v})} required />
        <div>
          <label className="overline block mb-1">Severity</label>
          <select className="w-full border border-input bg-card px-3 py-2 text-sm" value={f.severity} onChange={e => setF({...f, severity: e.target.value})}>
            {["low","medium","high","critical"].map(s => <option key={s}>{s}</option>)}
          </select>
        </div>
        <div>
          <label className="overline block mb-1">Description</label>
          <textarea rows={3} value={f.description} onChange={e => setF({...f, description: e.target.value})}
            className="w-full border border-input bg-card px-3 py-2 text-sm" required />
        </div>
        <div className="flex justify-end gap-2 pt-3">
          <Btn type="button" variant="outline" onClick={onClose}>Cancel</Btn>
          <Btn type="submit" variant="destructive" data-testid="submit-incident">Raise Alert</Btn>
        </div>
      </form>
    </Modal>
  );
}
