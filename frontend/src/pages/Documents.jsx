import { useEffect, useState } from "react";
import { http } from "@/lib/api";
import { PageHeader, Panel, StatusPill, Btn, Empty } from "@/components/ui-kit";
import { Modal, Field } from "./ClientsAdmin";
import { toast } from "sonner";

export default function Documents() {
  const [items, setItems] = useState([]);
  const [sites, setSites] = useState([]);
  const [show, setShow] = useState(false);

  const load = async () => {
    const [a, s] = await Promise.all([http.get("/documents"), http.get("/sites")]);
    setItems(a.data); setSites(s.data);
  };
  useEffect(() => { load(); }, []);

  return (
    <div>
      <PageHeader
        eyebrow="Records / Vault"
        title="Document Vault"
        subtitle="NOCs, certificates, drawings, insurance — a single source of truth."
        actions={<Btn onClick={() => setShow(true)} data-testid="new-doc-btn">+ Add Document</Btn>}
      />
      <div className="panel">
        {items.length === 0 ? <Empty>No documents uploaded.</Empty> :
          <table className="w-full text-sm">
            <thead><tr className="border-b border-border text-left">
              <th className="overline p-3">Title</th>
              <th className="overline">Type</th>
              <th className="overline">Site</th>
              <th className="overline">Expires</th>
              <th className="overline">Uploaded By</th>
              <th className="overline">File</th>
            </tr></thead>
            <tbody>
              {items.map(d => (
                <tr key={d.id} className="border-b border-border last:border-0">
                  <td className="p-3 font-semibold">{d.title}</td>
                  <td className="uppercase mono text-xs">{d.doc_type}</td>
                  <td className="text-xs">{sites.find(s => s.id === d.site_id)?.name || "Global"}</td>
                  <td className="mono text-xs">{d.expires_on || "—"}</td>
                  <td className="text-xs">{d.uploaded_by}</td>
                  <td>{d.file_url ? <a href={d.file_url} target="_blank" rel="noreferrer" className="text-primary underline text-xs">link</a> : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>}
      </div>
      {show && <NewDoc sites={sites} onClose={() => setShow(false)} onDone={() => { setShow(false); load(); }} />}
    </div>
  );
}

function NewDoc({ sites, onClose, onDone }) {
  const [f, setF] = useState({ title: "", doc_type: "noc", site_id: sites[0]?.id || "", expires_on: "", file_url: "" });
  const submit = async (e) => {
    e.preventDefault();
    try { await http.post("/documents", f); toast.success("Added"); onDone(); }
    catch { toast.error("Failed"); }
  };
  return (
    <Modal title="Add Document" onClose={onClose}>
      <form onSubmit={submit} className="space-y-3">
        <Field label="TITLE" value={f.title} onChange={v => setF({...f, title: v})} required />
        <div>
          <label className="overline block mb-1">Type</label>
          <select className="w-full border border-input bg-card px-3 py-2 text-sm"
            value={f.doc_type} onChange={e => setF({...f, doc_type: e.target.value})}>
            {["noc","certificate","drawing","insurance","other"].map(t => <option key={t}>{t}</option>)}
          </select>
        </div>
        <div>
          <label className="overline block mb-1">Site</label>
          <select className="w-full border border-input bg-card px-3 py-2 text-sm"
            value={f.site_id} onChange={e => setF({...f, site_id: e.target.value})}>
            <option value="">— Global —</option>
            {sites.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
        </div>
        <Field label="EXPIRES ON" type="date" value={f.expires_on} onChange={v => setF({...f, expires_on: v})} />
        <Field label="FILE URL (optional)" value={f.file_url} onChange={v => setF({...f, file_url: v})} />
        <div className="flex justify-end gap-2 pt-3">
          <Btn type="button" variant="outline" onClick={onClose}>Cancel</Btn>
          <Btn type="submit" data-testid="submit-doc">Save</Btn>
        </div>
      </form>
    </Modal>
  );
}
