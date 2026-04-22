import { useEffect, useState } from "react";
import { http } from "@/lib/api";
import { PageHeader, Panel, StatusPill, Btn, Empty } from "@/components/ui-kit";
import { Modal, Field } from "./ClientsAdmin";
import { toast } from "sonner";
import { LifeBuoy } from "lucide-react";

export default function Support() {
  const [items, setItems] = useState([]);
  const [show, setShow] = useState(false);

  const load = async () => {
    try {
      const { data } = await http.get("/support-requests");
      setItems(data);
    } catch { setItems([]); }
  };
  useEffect(() => { load(); }, []);

  return (
    <div>
      <PageHeader
        eyebrow="Help" title="Service Requests"
        subtitle="Raise a service request — SSPL support is notified instantly."
        actions={<Btn onClick={() => setShow(true)} data-testid="new-request-btn">
          <LifeBuoy size={14} /> Request Service
        </Btn>}
      />
      <div className="panel">
        {items.length === 0 ? <Empty>No service requests yet.</Empty> :
          <table className="w-full text-sm" data-testid="support-table">
            <thead><tr className="border-b border-border text-left">
              <th className="overline p-3">When</th>
              <th className="overline">Subject</th>
              <th className="overline">Category</th>
              <th className="overline">Priority</th>
              <th className="overline">Raised By</th>
              <th className="overline">Status</th>
            </tr></thead>
            <tbody>
              {items.map(r => (
                <tr key={r.id} className="border-b border-border last:border-0">
                  <td className="p-3 mono text-xs">{r.created_at.slice(0,16).replace("T"," ")}</td>
                  <td className="font-semibold">{r.subject}</td>
                  <td className="uppercase mono text-xs">{r.category}</td>
                  <td><StatusPill value={r.priority === "high" ? "critical" : r.priority === "medium" ? "warning" : "low"}>{r.priority}</StatusPill></td>
                  <td className="text-xs">{r.raised_by_name}</td>
                  <td><StatusPill value={r.status === "open" ? "warning" : "success"}>{r.status}</StatusPill></td>
                </tr>
              ))}
            </tbody>
          </table>}
      </div>
      {show && <NewRequest onClose={() => setShow(false)} onDone={() => { setShow(false); load(); }} />}
    </div>
  );
}

function NewRequest({ onClose, onDone }) {
  const [f, setF] = useState({ subject: "", category: "service", priority: "medium", description: "" });
  const submit = async (e) => {
    e.preventDefault();
    try {
      await http.post("/support-requests", f);
      toast.success("Request raised · SSPL support notified");
      onDone();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed");
    }
  };
  return (
    <Modal title="New Service Request" onClose={onClose}>
      <form onSubmit={submit} className="space-y-3" data-testid="support-form">
        <Field label="SUBJECT" value={f.subject} onChange={v => setF({ ...f, subject: v })} required data-testid="sr-subject" />
        <div>
          <label className="overline block mb-1">Category</label>
          <select className="w-full border border-input bg-card px-3 py-2 text-sm"
            value={f.category} onChange={e => setF({ ...f, category: e.target.value })}
            data-testid="sr-category">
            {["service","billing","technical","other"].map(c => <option key={c}>{c}</option>)}
          </select>
        </div>
        <div>
          <label className="overline block mb-1">Priority</label>
          <select className="w-full border border-input bg-card px-3 py-2 text-sm"
            value={f.priority} onChange={e => setF({ ...f, priority: e.target.value })}
            data-testid="sr-priority">
            {["low","medium","high"].map(p => <option key={p}>{p}</option>)}
          </select>
        </div>
        <div>
          <label className="overline block mb-1">Description</label>
          <textarea rows={4} value={f.description} onChange={e => setF({ ...f, description: e.target.value })}
            className="w-full border border-input bg-card px-3 py-2 text-sm" required
            data-testid="sr-description" />
        </div>
        <div className="flex justify-end gap-2 pt-3">
          <Btn type="button" variant="outline" onClick={onClose} data-testid="sr-cancel">Cancel</Btn>
          <Btn type="submit" data-testid="submit-request">Raise Request</Btn>
        </div>
      </form>
    </Modal>
  );
}
