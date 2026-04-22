import { useEffect, useState } from "react";
import { http } from "@/lib/api";
import { PageHeader, Panel, StatusPill, Btn, Empty } from "@/components/ui-kit";
import { Modal, Field } from "./ClientsAdmin";
import { toast } from "sonner";

export default function Maintenance() {
  const [tasks, setTasks] = useState([]);
  const [assets, setAssets] = useState([]);
  const [users, setUsers] = useState([]);
  const [show, setShow] = useState(false);

  const load = async () => {
    const [a, b, u] = await Promise.all([
      http.get("/maintenance"),
      http.get("/assets"),
      http.get("/users").catch(() => ({ data: [] })),
    ]);
    setTasks(a.data); setAssets(b.data); setUsers(u.data);
  };
  useEffect(() => { load(); }, []);

  const completeTask = async (tid) => {
    await http.patch(`/maintenance/${tid}`, { status: "completed" });
    toast.success("Task completed");
    load();
  };

  return (
    <div>
      <PageHeader
        eyebrow="Operations / Maintenance"
        title="Maintenance Engine"
        subtitle="Scheduled and overdue work assigned to technicians."
        actions={<Btn onClick={() => setShow(true)} data-testid="new-task-btn">+ Schedule Task</Btn>}
      />
      <div className="panel">
        {tasks.length === 0 ? <Empty>No maintenance tasks.</Empty> :
          <table className="w-full text-sm" data-testid="maintenance-table">
            <thead><tr className="border-b border-border text-left">
              <th className="overline p-3">Scheduled</th>
              <th className="overline">Asset</th>
              <th className="overline">Notes</th>
              <th className="overline">Status</th>
              <th></th>
            </tr></thead>
            <tbody>
              {tasks.map(t => (
                <tr key={t.id} className="border-b border-border last:border-0">
                  <td className="p-3 mono text-xs">{t.scheduled_date}</td>
                  <td className="font-semibold">{assets.find(a => a.id === t.asset_id)?.name || "—"}</td>
                  <td className="text-xs">{t.notes}</td>
                  <td><StatusPill value={t.status}>{t.status}</StatusPill></td>
                  <td>{t.status !== "completed" &&
                    <Btn variant="outline" onClick={() => completeTask(t.id)} data-testid={`complete-${t.id}`}>Mark Done</Btn>}</td>
                </tr>
              ))}
            </tbody>
          </table>}
      </div>
      {show && <NewTask assets={assets} users={users} onClose={() => setShow(false)} onDone={() => { setShow(false); load(); }} />}
    </div>
  );
}

function NewTask({ assets, users, onClose, onDone }) {
  const [f, setF] = useState({
    asset_id: assets[0]?.id || "", scheduled_date: new Date().toISOString().slice(0,10),
    technician_id: users.find(u => u.role === "technician")?.id || "", notes: "",
  });
  const submit = async (e) => {
    e.preventDefault();
    try { await http.post("/maintenance", f); toast.success("Scheduled"); onDone(); }
    catch { toast.error("Failed"); }
  };
  return (
    <Modal title="Schedule Maintenance" onClose={onClose}>
      <form onSubmit={submit} className="space-y-3">
        <div>
          <label className="overline block mb-1">Asset</label>
          <select className="w-full border border-input bg-card px-3 py-2 text-sm"
            value={f.asset_id} onChange={e => setF({...f, asset_id: e.target.value})}>
            {assets.map(a => <option key={a.id} value={a.id}>{a.name}</option>)}
          </select>
        </div>
        <Field label="DATE" type="date" value={f.scheduled_date} onChange={v => setF({...f, scheduled_date: v})} required />
        <div>
          <label className="overline block mb-1">Technician</label>
          <select className="w-full border border-input bg-card px-3 py-2 text-sm"
            value={f.technician_id} onChange={e => setF({...f, technician_id: e.target.value})}>
            <option value="">— Unassigned —</option>
            {users.filter(u => u.role === "technician").map(u => <option key={u.id} value={u.id}>{u.name}</option>)}
          </select>
        </div>
        <Field label="NOTES" value={f.notes} onChange={v => setF({...f, notes: v})} />
        <div className="flex justify-end gap-2 pt-3">
          <Btn type="button" variant="outline" onClick={onClose}>Cancel</Btn>
          <Btn type="submit" data-testid="submit-task">Schedule</Btn>
        </div>
      </form>
    </Modal>
  );
}
