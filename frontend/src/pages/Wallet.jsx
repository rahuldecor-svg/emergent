import { useEffect, useState } from "react";
import { http } from "@/lib/api";
import { PageHeader, Panel, Empty } from "@/components/ui-kit";

export default function Wallet() {
  const [d, setD] = useState(null);
  useEffect(() => { http.get("/wallet").then(r => setD(r.data)); }, []);
  if (!d) return <div className="mono text-sm">LOADING WALLET…</div>;

  return (
    <div>
      <PageHeader eyebrow="Finance" title="Wallet & Billing" subtitle="Prepaid balance, GST invoices and subscription." />
      <div className="grid md:grid-cols-3 gap-6 mb-6">
        <Panel title="Balance" className="md:col-span-1">
          <div className="num text-7xl leading-none" data-testid="wallet-balance">₹{Math.round(d.balance)}</div>
          <div className="overline text-muted-foreground mt-3">Plan · {d.subscription_plan?.toUpperCase() || "—"}</div>
          {d.balance < 1000 && <div className="text-xs text-status-warning mt-3 border border-status-warning/50 p-2">⚠ Low balance — contact SSPL for recharge.</div>}
        </Panel>
        <Panel title="How Recharge Works" className="md:col-span-2">
          <ol className="text-sm space-y-2 list-decimal pl-4">
            <li>Contact your SSPL account manager with the required amount.</li>
            <li>SSPL credits your wallet manually; GST invoice auto-generated.</li>
            <li>Wallet deducts on usage: per asset, inspection, user, location.</li>
            <li>At zero balance, platform enters read-only mode.</li>
          </ol>
        </Panel>
      </div>
      <Panel title="GST Invoice History">
        {d.transactions.length === 0 ? <Empty>No transactions yet.</Empty> :
          <table className="w-full text-sm" data-testid="wallet-tx-table">
            <thead><tr className="border-b border-border text-left">
              <th className="overline p-3">Invoice</th>
              <th className="overline">Date</th>
              <th className="overline">Type</th>
              <th className="overline">Amount</th>
              <th className="overline">GST</th>
              <th className="overline">Balance After</th>
              <th className="overline">Reference</th>
            </tr></thead>
            <tbody>
              {d.transactions.map(t => (
                <tr key={t.id} className="border-b border-border last:border-0">
                  <td className="p-3 mono text-xs">{t.gst_invoice_no || "—"}</td>
                  <td className="mono text-xs">{t.created_at.slice(0,10)}</td>
                  <td className="uppercase mono text-xs">{t.type}</td>
                  <td className="mono">₹{t.amount}</td>
                  <td className="mono text-xs">₹{t.gst_amount || 0}</td>
                  <td className="mono">₹{t.balance_after}</td>
                  <td className="text-xs">{t.reference}</td>
                </tr>
              ))}
            </tbody>
          </table>}
      </Panel>
    </div>
  );
}
