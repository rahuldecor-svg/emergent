import { useEffect, useRef, useState } from "react";
import { http, API } from "@/lib/api";
import { PageHeader, Panel, Btn, Empty } from "@/components/ui-kit";
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
        subtitle="NOCs, certificates, drawings, insurance — stored on your tenant-scoped vault."
        actions={<Btn onClick={() => setShow(true)} data-testid="new-doc-btn">+ Upload Document</Btn>}
      />
      <div className="panel">
        {items.length === 0 ? <Empty>No documents uploaded.</Empty> :
          <table className="w-full text-sm" data-testid="documents-table">
            <thead><tr className="border-b border-border text-left">
              <th className="overline p-3">Title</th>
              <th className="overline">Type</th>
              <th className="overline">Site</th>
              <th className="overline">File</th>
              <th className="overline">Expires</th>
              <th className="overline">Uploaded By</th>
              <th className="overline">Action</th>
            </tr></thead>
            <tbody>
              {items.map(d => (
                <tr key={d.id} className="border-b border-border last:border-0">
                  <td className="p-3 font-semibold">{d.title}</td>
                  <td className="uppercase mono text-xs">{d.doc_type}</td>
                  <td className="text-xs">{sites.find(s => s.id === d.site_id)?.name || "Global"}</td>
                  <td className="mono text-xs">{d.file_name || (d.file_url ? "URL" : "—")}</td>
                  <td className="mono text-xs">{d.expires_on || "—"}</td>
                  <td className="text-xs">{d.uploaded_by}</td>
                  <td>
                    {d.file_name ? (
                      <a href={`${API}/documents/file/${d.id}`} target="_blank" rel="noreferrer"
                        className="text-xs text-primary underline" data-testid={`download-${d.id}`}>download</a>
                    ) : d.file_url ? (
                      <a href={d.file_url} target="_blank" rel="noreferrer"
                        className="text-xs text-primary underline">link</a>
                    ) : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>}
      </div>
      {show && <UploadDoc sites={sites} onClose={() => setShow(false)} onDone={() => { setShow(false); load(); }} />}
    </div>
  );
}

function UploadDoc({ sites, onClose, onDone }) {
  const [f, setF] = useState({ title: "", doc_type: "noc", site_id: "", expires_on: "" });
  const [file, setFile] = useState(null);
  const [busy, setBusy] = useState(false);
  const ref = useRef();

  const submit = async (e) => {
    e.preventDefault();
    if (!file) { toast.error("Choose a file to upload"); return; }
    setBusy(true);
    try {
      const form = new FormData();
      form.append("file", file);
      form.append("title", f.title);
      form.append("doc_type", f.doc_type);
      if (f.site_id) form.append("site_id", f.site_id);
      if (f.expires_on) form.append("expires_on", f.expires_on);
      await http.post("/documents/upload", form, { headers: { "Content-Type": "multipart/form-data" } });
      toast.success("Document uploaded");
      onDone();
    } catch (e) {
      toast.error(e.response?.data?.detail || "Upload failed");
    } finally { setBusy(false); }
  };

  return (
    <Modal title="Upload Document" onClose={onClose}>
      <form onSubmit={submit} className="space-y-3" data-testid="upload-doc-form">
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
        <div>
          <label className="overline block mb-1">File (max 25 MB)</label>
          <input ref={ref} type="file" onChange={e => setFile(e.target.files?.[0] || null)}
            data-testid="doc-file-input"
            className="w-full border border-input bg-card px-3 py-2 text-sm" required />
          {file && <div className="mono text-xs mt-1 text-muted-foreground">{file.name} · {(file.size/1024).toFixed(1)} KB</div>}
        </div>
        <div className="flex justify-end gap-2 pt-3">
          <Btn type="button" variant="outline" onClick={onClose}>Cancel</Btn>
          <Btn type="submit" disabled={busy} data-testid="upload-submit">{busy ? "Uploading…" : "Upload"}</Btn>
        </div>
      </form>
    </Modal>
  );
}
