import { useEffect, useState } from "react";
import { http } from "@/lib/api";
import { PageHeader, Panel, StatusPill, Btn, Empty } from "@/components/ui-kit";
import { toast } from "sonner";

export default function ClientsAdmin() {
  const [clients, setClients] = useState([]);
  const [showNew, setShowNew] = useState(false);
  const [showRecharge, setShowRecharge] = useState(null);

  const load = async () => {
    try {
      const { data } = await http.get("/admin/clients");
      setClients(data);
    } catch (e) {
      if (e.response?.status === 403) {
        toast.error("This area is reserved for SSPL Super Admin.");
        setClients([]);
      } else {
        toast.error("Failed to load clients");
      }
    }
  };
  useEffect(() => { load(); }, []);

  const toggleKill = async (cid) => {
    await http.post(`/admin/clients/${cid}/kill-switch`);
    toast.success("License toggled");
    load();
  };

  return (
    <div>
      <PageHeader
        eyebrow="SSPL / Tenants"
        title="Clients & Licenses"
        subtitle="Onboard, suspend and recharge any client wallet."
        actions={<Btn onClick={() => setShowNew(true)} data-testid="new-client-btn">+ New Client</Btn>}
      />
      <div className="panel">
        <table className="w-full text-sm" data-testid="clients-table">
          <thead>
            <tr className="border-b border-border text-left">
              <th className="overline p-3">Name</th>
              <th className="overline">Industry</th>
              <th className="overline">Plan</th>
              <th className="overline">Wallet</th>
              <th className="overline">Users</th>
              <th className="overline">Assets</th>
              <th className="overline">License</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {clients.length === 0 && <tr><td colSpan={8}><Empty>No clients onboarded.</Empty></td></tr>}
            {clients.map(c => (
              <tr key={c.id} className="border-b border-border last:border-0">
                <td className="p-3 font-semibold">{c.name}</td>
                <td>{c.industry}</td>
                <td className="uppercase mono text-xs">{c.subscription_plan}</td>
                <td className="mono">₹{Math.round(c.wallet_balance)}</td>
                <td>{c.user_count}</td>
                <td>{c.asset_count}</td>
                <td><StatusPill value={c.license_active ? "active" : "critical"}>{c.license_active ? "Active" : "Suspended"}</StatusPill></td>
                <td className="flex gap-2 p-3">
                  <Btn variant="outline" onClick={() => setShowRecharge(c)} data-testid={`recharge-${c.id}`}>Recharge</Btn>
                  <Btn variant="outline" onClick={() => toggleKill(c.id)} data-testid={`toggle-${c.id}`}>{c.license_active ? "Suspend" : "Activate"}</Btn>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showNew && <NewClientModal onClose={() => setShowNew(false)} onDone={() => { setShowNew(false); load(); }} />}
      {showRecharge && <RechargeModal client={showRecharge} onClose={() => setShowRecharge(null)} onDone={() => { setShowRecharge(null); load(); }} />}
    </div>
  );
}

function NewClientModal({ onClose, onDone }) {
  const [f, setF] = useState({ name: "", industry: "Manufacturing", gstin: "", subscription_plan: "basic",
    admin_name: "", admin_email: "", admin_password: "" });
  const [busy, setBusy] = useState(false);
  const submit = async (e) => {
    e.preventDefault(); setBusy(true);
    try { await http.post("/admin/clients", f); toast.success("Client created"); onDone(); }
    catch (e) { toast.error(e.response?.data?.detail || "Failed"); }
    finally { setBusy(false); }
  };
  return (
    <Modal onClose={onClose} title="Onboard New Client">
      <form onSubmit={submit} className="space-y-3" data-testid="new-client-form">
        {["name","industry","gstin"].map(k =>
          <Field key={k} label={k.toUpperCase()} value={f[k]} onChange={v => setF({...f, [k]: v})} />
        )}
        <div>
          <label className="overline block mb-1">Plan</label>
          <select className="w-full border border-input bg-card px-3 py-2 text-sm"
            value={f.subscription_plan} onChange={e => setF({...f, subscription_plan: e.target.value})}>
            <option value="basic">Basic</option><option value="pro">Pro</option><option value="enterprise">Enterprise</option>
          </select>
        </div>
        <div className="pt-3 border-t border-border">
          <div className="overline mb-2">Primary Admin</div>
          <Field label="ADMIN NAME" value={f.admin_name} onChange={v => setF({...f, admin_name: v})} required />
          <Field label="ADMIN EMAIL" type="email" value={f.admin_email} onChange={v => setF({...f, admin_email: v})} required />
          <Field label="ADMIN PASSWORD" type="password" value={f.admin_password} onChange={v => setF({...f, admin_password: v})} required />
        </div>
        <div className="flex justify-end gap-2 pt-3">
          <Btn type="button" variant="outline" onClick={onClose}>Cancel</Btn>
          <Btn type="submit" disabled={busy} data-testid="create-client-submit">{busy ? "Creating…" : "Create"}</Btn>
        </div>
      </form>
    </Modal>
  );
}

function RechargeModal({ client, onClose, onDone }) {
  const [amount, setAmount] = useState(1000);
  const [note, setNote] = useState("");
  const submit = async (e) => {
    e.preventDefault();
    try { await http.post("/admin/wallet/recharge", { client_id: client.id, amount: Number(amount), note });
      toast.success("Wallet credited"); onDone(); }
    catch { toast.error("Failed"); }
  };
  return (
    <Modal onClose={onClose} title={`Recharge ${client.name}`}>
      <form onSubmit={submit} className="space-y-3">
        <Field label="AMOUNT (₹)" type="number" value={amount} onChange={setAmount} required />
        <Field label="NOTE" value={note} onChange={setNote} />
        <div className="text-xs text-muted-foreground mono">GST 18% will be auto-computed on invoice.</div>
        <div className="flex justify-end gap-2 pt-3">
          <Btn type="button" variant="outline" onClick={onClose}>Cancel</Btn>
          <Btn type="submit" data-testid="confirm-recharge">Credit</Btn>
        </div>
      </form>
    </Modal>
  );
}

export function Modal({ title, onClose, children }) {
  return (
    <div className="fixed inset-0 bg-black/40 z-40 grid place-items-center p-4" onClick={onClose}>
      <div className="bg-card border border-border max-w-md w-full" onClick={e => e.stopPropagation()}>
        <div className="px-4 py-3 border-b border-border flex justify-between items-center">
          <div className="font-heading font-bold">{title}</div>
          <button onClick={onClose} className="text-muted-foreground hover:text-foreground" data-testid="modal-close">✕</button>
        </div>
        <div className="p-4">{children}</div>
      </div>
    </div>
  );
}

export function Field({ label, value, onChange, type = "text", required, ...rest }) {
  return (
    <div>
      <label className="overline block mb-1">{label}</label>
      <input type={type} value={value} onChange={e => onChange(e.target.value)} required={required}
        className="w-full bg-card border border-input px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
        {...rest} />
    </div>
  );
}
