import { useEffect, useState } from "react";
import { http } from "@/lib/api";
import { PageHeader, Panel, StatusPill, Empty } from "@/components/ui-kit";

export default function Wallet() {
  const [d, setD] = useState(null);
  useEffect(() => { http.get("/wallet").then(r => setD(r.data)); }, []);
  if (!d) return <div className="mono text-sm">LOADING WALLET…</div>;

  const p = d.pricing || {};
  const statusKey = d.status === "exhausted" ? "critical" : d.status === "low" ? "warning" : "safe";

  return (
    <div>
      <PageHeader eyebrow="Finance" title="Wallet & Billing" subtitle="Prepaid balance, usage deductions, GST invoices." />
      <div className="grid md:grid-cols-3 gap-6 mb-6">
        <Panel title="Balance" className="md:col-span-1">
          <div className="num text-7xl leading-none" data-testid="wallet-balance">₹{Math.round(d.balance)}</div>
          <div className="mt-3 flex items-center gap-2">
            <StatusPill value={statusKey}>{d.status?.toUpperCase() || "—"}</StatusPill>
            <span className="overline text-muted-foreground">Plan · {d.subscription_plan?.toUpperCase() || "—"}</span>
          </div>
          {d.status === "exhausted" && (
            <div className="text-xs text-status-critical mt-3 border border-status-critical/50 p-2" data-testid="wallet-readonly-alert">
              🛑 Read-only mode — asset/inspection/user creation blocked. Contact SSPL.
            </div>
          )}
          {d.status === "low" && (
            <div className="text-xs text-status-warning mt-3 border border-status-warning/50 p-2" data-testid="wallet-low-alert">
              ⚠ Balance below ₹{p.low_threshold}. Actions will stop at ₹0.
            </div>
          )}
        </Panel>
        <Panel title="Usage Pricing" className="md:col-span-1">
          <div className="divide-y divide-border text-sm">
            <div className="flex justify-between py-2"><span>Per asset created</span><span className="num text-2xl">₹{p.per_asset}</span></div>
            <div className="flex justify-between py-2"><span>Per inspection</span><span className="num text-2xl">₹{p.per_inspection}</span></div>
            <div className="flex justify-between py-2"><span>Per user added</span><span className="num text-2xl">₹{p.per_user}</span></div>
            <div className="flex justify-between py-2 text-muted-foreground"><span>Low-balance warn</span><span className="mono">₹{p.low_threshold}</span></div>
          </div>
        </Panel>
        <Panel title="How it works" className="md:col-span-1">
          <ol className="text-sm space-y-2 list-decimal pl-4">
            <li>SSPL credits your wallet with GST invoice.</li>
            <li>Every asset/inspection/user debits wallet with a full reference trail.</li>
            <li>Below ₹{p.low_threshold} → warning. At ₹0 → read-only.</li>
            <li>Request recharge from your SSPL account manager.</li>
          </ol>
        </Panel>
      </div>
      <Panel title="Transaction Ledger (credits + usage)">
        {d.transactions.length === 0 ? <Empty>No transactions yet.</Empty> :
          <table className="w-full text-sm" data-testid="wallet-tx-table">
            <thead><tr className="border-b border-border text-left">
              <th className="overline p-3">Invoice / Ref</th>
              <th className="overline">Date</th>
              <th className="overline">Type</th>
              <th className="overline">Reason</th>
              <th className="overline">Amount</th>
              <th className="overline">GST</th>
              <th className="overline">Balance After</th>
            </tr></thead>
            <tbody>
              {d.transactions.map(t => (
                <tr key={t.id} className="border-b border-border last:border-0">
                  <td className="p-3 mono text-xs">{t.gst_invoice_no || t.reference?.slice(0,12) || "—"}</td>
                  <td className="mono text-xs">{t.created_at.slice(0,10)}</td>
                  <td><StatusPill value={t.type === "credit" ? "safe" : "warning"}>{t.type}</StatusPill></td>
                  <td className="text-xs">{t.reason || t.note || "—"}</td>
                  <td className={`mono ${t.amount < 0 ? "text-status-critical" : ""}`}>₹{t.amount}</td>
                  <td className="mono text-xs">₹{t.gst_amount || 0}</td>
                  <td className="mono">₹{t.balance_after}</td>
                </tr>
              ))}
            </tbody>
          </table>}
      </Panel>
    </div>
  );
}
