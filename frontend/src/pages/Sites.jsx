import { useEffect, useState } from "react";
import { http } from "@/lib/api";
import { PageHeader, Panel, Btn, Empty } from "@/components/ui-kit";
import { Modal, Field } from "./ClientsAdmin";
import { toast } from "sonner";

export default function Sites() {
  const [sites, setSites] = useState([]);
  const [show, setShow] = useState(false);

  const load = async () => { const { data } = await http.get("/sites"); setSites(data); };
  useEffect(() => { load(); }, []);

  return (
    <div>
      <PageHeader eyebrow="Network" title="Sites"
        subtitle="Your plants, warehouses, offices, campuses."
        actions={<Btn onClick={() => setShow(true)} data-testid="new-site-btn">+ Add Site</Btn>} />
      <div className="grid md:grid-cols-3 gap-px bg-border">
        {sites.length === 0 && <div className="col-span-3 bg-card"><Empty>No sites yet.</Empty></div>}
        {sites.map(s => (
          <div key={s.id} className="bg-card p-5">
            <div className="overline text-muted-foreground">{s.address || "—"}</div>
            <div className="font-heading font-bold text-xl mt-1">{s.name}</div>
            <div className="mono text-xs mt-3 text-muted-foreground">
              {s.lat ? `${s.lat}, ${s.lng}` : "No geo"}
            </div>
          </div>
        ))}
      </div>
      {show && <NewSite onClose={() => setShow(false)} onDone={() => { setShow(false); load(); }} />}
    </div>
  );
}

function NewSite({ onClose, onDone }) {
  const [f, setF] = useState({ name: "", address: "", lat: "", lng: "" });
  const submit = async (e) => {
    e.preventDefault();
    try {
      const body = { ...f, lat: f.lat ? Number(f.lat) : null, lng: f.lng ? Number(f.lng) : null };
      await http.post("/sites", body); toast.success("Site added"); onDone();
    } catch { toast.error("Failed"); }
  };
  return (
    <Modal title="Add Site" onClose={onClose}>
      <form onSubmit={submit} className="space-y-3">
        <Field label="NAME" value={f.name} onChange={v => setF({...f, name: v})} required />
        <Field label="ADDRESS" value={f.address} onChange={v => setF({...f, address: v})} />
        <div className="grid grid-cols-2 gap-2">
          <Field label="LAT" value={f.lat} onChange={v => setF({...f, lat: v})} />
          <Field label="LNG" value={f.lng} onChange={v => setF({...f, lng: v})} />
        </div>
        <div className="flex justify-end gap-2 pt-3">
          <Btn type="button" variant="outline" onClick={onClose}>Cancel</Btn>
          <Btn type="submit" data-testid="submit-site">Save</Btn>
        </div>
      </form>
    </Modal>
  );
}
