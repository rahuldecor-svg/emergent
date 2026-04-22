import { useEffect, useState } from "react";
import { http } from "@/lib/api";
import { PageHeader, Panel, Btn, Empty } from "@/components/ui-kit";
import { Modal, Field } from "./ClientsAdmin";
import { toast } from "sonner";

const ROLES = ["client_admin", "fire_officer", "technician", "auditor", "partner"];

export default function Users() {
  const [items, setItems] = useState([]);
  const [show, setShow] = useState(false);

  const load = async () => { const { data } = await http.get("/users"); setItems(data); };
  useEffect(() => { load(); }, []);

  return (
    <div>
      <PageHeader eyebrow="Access" title="Team Members"
        actions={<Btn onClick={() => setShow(true)} data-testid="new-user-btn">+ Add User</Btn>} />
      <div className="panel">
        {items.length === 0 ? <Empty>No users.</Empty> :
          <table className="w-full text-sm">
            <thead><tr className="border-b border-border text-left">
              <th className="overline p-3">Name</th><th className="overline">Email</th>
              <th className="overline">Role</th><th className="overline">Joined</th>
            </tr></thead>
            <tbody>
              {items.map(u => (
                <tr key={u.id} className="border-b border-border last:border-0">
                  <td className="p-3 font-semibold">{u.name}</td>
                  <td className="mono text-xs">{u.email}</td>
                  <td className="uppercase mono text-xs">{u.role}</td>
                  <td className="mono text-xs">{u.created_at?.slice(0,10)}</td>
                </tr>
              ))}
            </tbody>
          </table>}
      </div>
      {show && <NewUser onClose={() => setShow(false)} onDone={() => { setShow(false); load(); }} />}
    </div>
  );
}

function NewUser({ onClose, onDone }) {
  const [f, setF] = useState({ name: "", email: "", password: "", role: "technician" });
  const submit = async (e) => {
    e.preventDefault();
    try {
      const { data } = await http.post("/users", f);
      const c = data.wallet_charge;
      toast.success(
        c ? `User created · −₹${c.cost} (${c.reason}). Balance ₹${c.balance_after}` : "User created",
      );
      onDone();
    } catch (e) {
      toast.error(e.response?.data?.detail || "Failed");
    }
  };
  return (
    <Modal title="Add User" onClose={onClose}>
      <form onSubmit={submit} className="space-y-3">
        <Field label="NAME" value={f.name} onChange={v => setF({...f, name: v})} required />
        <Field label="EMAIL" type="email" value={f.email} onChange={v => setF({...f, email: v})} required />
        <Field label="PASSWORD" type="password" value={f.password} onChange={v => setF({...f, password: v})} required />
        <div>
          <label className="overline block mb-1">Role</label>
          <select className="w-full border border-input bg-card px-3 py-2 text-sm"
            value={f.role} onChange={e => setF({...f, role: e.target.value})}>
            {ROLES.map(r => <option key={r}>{r}</option>)}
          </select>
        </div>
        <div className="flex justify-end gap-2 pt-3">
          <Btn type="button" variant="outline" onClick={onClose}>Cancel</Btn>
          <Btn type="submit" data-testid="submit-user">Create</Btn>
        </div>
      </form>
    </Modal>
  );
}
