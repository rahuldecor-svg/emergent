import { useEffect, useState } from "react";
import { http } from "@/lib/api";
import { PageHeader, Panel, StatusPill, Btn, Empty } from "@/components/ui-kit";
import { toast } from "sonner";

export default function SuperAdminDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    try {
      const { data } = await http.get("/admin/overview");
      setData(data);
    } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const toggleKill = async (cid) => {
    try {
      const { data } = await http.post(`/admin/clients/${cid}/kill-switch`);
      toast.success(data.license_active ? "Client activated" : "Client suspended");
      load();
    } catch (e) { toast.error("Failed"); }
  };

  if (loading || !data) return <div className="text-sm mono">LOADING COMMAND CENTER…</div>;

  const stats = [
    { label: "Clients", v: data.total_clients },
    { label: "Active", v: data.active_clients },
    { label: "Users", v: data.total_users },
    { label: "Assets Tracked", v: data.total_assets },
    { label: "Wallet Balance (₹)", v: Math.round(data.total_wallet_balance) },
  ];

  return (
    <div>
      <PageHeader
        eyebrow="SSPL / Command Center"
        title="Global Operations"
        subtitle="All clients, revenue, risk and license control — in one view."
      />
      <div className="grid grid-cols-2 md:grid-cols-5 gap-px bg-border mb-6" data-testid="overview-stats">
        {stats.map(s => (
          <div key={s.label} className="bg-card p-5">
            <div className="overline text-muted-foreground">{s.label}</div>
            <div className="num text-4xl mt-2">{s.v}</div>
          </div>
        ))}
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <Panel title="Low Balance Clients" className="lg:col-span-1">
          {data.low_balance_clients.length === 0
            ? <Empty>All wallets healthy.</Empty>
            : data.low_balance_clients.map(c => (
              <div key={c.id} className="flex justify-between items-center py-2 border-b border-border last:border-0">
                <span className="text-sm font-medium">{c.name}</span>
                <span className="mono text-xs text-status-warning">₹{c.balance}</span>
              </div>
            ))}
        </Panel>

        <Panel title="Client Risk Ladder" className="lg:col-span-2" action={<span className="overline text-muted-foreground">lowest score = highest risk</span>}>
          <table className="w-full text-sm" data-testid="clients-risk-table">
            <thead className="text-left">
              <tr className="border-b border-border">
                <th className="overline py-2">Client</th>
                <th className="overline">Plan</th>
                <th className="overline">Score</th>
                <th className="overline">Expired</th>
                <th className="overline">Missed</th>
                <th className="overline">Wallet</th>
                <th className="overline">License</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {data.clients_risk.map(c => (
                <tr key={c.client_id} className="border-b border-border last:border-0">
                  <td className="py-2 font-semibold">{c.name}</td>
                  <td className="uppercase mono text-xs">{c.subscription_plan}</td>
                  <td><span className="num text-xl">{c.score}</span></td>
                  <td className="mono text-status-critical">{c.expired_assets}</td>
                  <td className="mono text-status-warning">{c.missed_maintenance}</td>
                  <td className="mono">₹{Math.round(c.wallet_balance)}</td>
                  <td><StatusPill value={c.license_active ? "active" : "critical"}>{c.license_active ? "Active" : "Suspended"}</StatusPill></td>
                  <td>
                    <Btn variant="outline" onClick={() => toggleKill(c.client_id)} data-testid={`kill-${c.client_id}`}>
                      {c.license_active ? "Suspend" : "Activate"}
                    </Btn>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Panel>
      </div>
    </div>
  );
}
