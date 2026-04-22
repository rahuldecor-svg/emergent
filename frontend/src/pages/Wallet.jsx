import { useEffect, useState } from "react";
import { toast } from "sonner";
import { http, API } from "@/lib/api";
import { PageHeader, Panel, StatusPill, Empty } from "@/components/ui-kit";

function loadRazorpayScript() {
  return new Promise((resolve) => {
    if (window.Razorpay) return resolve(true);
    const s = document.createElement("script");
    s.src = "https://checkout.razorpay.com/v1/checkout.js";
    s.onload = () => resolve(true);
    s.onerror = () => resolve(false);
    document.body.appendChild(s);
  });
}

export default function Wallet() {
  const [d, setD] = useState(null);
  const [cfg, setCfg] = useState({ configured: false, key_id: "" });
  const [amount, setAmount] = useState(5000);
  const [busy, setBusy] = useState(false);

  const loadWallet = () => http.get("/wallet").then((r) => setD(r.data));

  useEffect(() => {
    loadWallet();
    http
      .get("/payments/config")
      .then((r) => setCfg(r.data))
      .catch(() => setCfg({ configured: false, key_id: "" }));
  }, []);

  const handleRecharge = async () => {
    if (!cfg.configured) {
      toast.error("Payments not configured. Contact SSPL.");
      return;
    }
    if (!amount || amount < 1) {
      toast.error("Minimum recharge is ₹1");
      return;
    }
    setBusy(true);
    try {
      const ok = await loadRazorpayScript();
      if (!ok) throw new Error("Failed to load Razorpay SDK");
      const { data: order } = await http.post("/payments/order", { amount });
      const options = {
        key: order.key_id,
        amount: order.amount,
        currency: order.currency,
        order_id: order.order_id,
        name: "Fire Compliance OS",
        description: `Wallet recharge for ${order.client_name}`,
        prefill: { email: order.prefill_email, name: order.prefill_name },
        theme: { color: "#111827" },
        handler: async (resp) => {
          try {
            const { data } = await http.post("/payments/verify", {
              razorpay_order_id: resp.razorpay_order_id,
              razorpay_payment_id: resp.razorpay_payment_id,
              razorpay_signature: resp.razorpay_signature,
            });
            toast.success(
              `Recharge successful · ₹${data.amount ?? amount} credited · Invoice ${data.invoice_no}`
            );
            await loadWallet();
            // Auto-download invoice
            if (data.invoice_no) {
              window.open(`${API}/payments/invoice/${data.invoice_no}`, "_blank");
            }
          } catch (e) {
            toast.error(
              e?.response?.data?.detail || "Payment verification failed"
            );
          }
        },
        modal: {
          ondismiss: () => {
            toast.message("Payment cancelled");
          },
        },
      };
      const rzp = new window.Razorpay(options);
      rzp.on("payment.failed", (resp) => {
        toast.error(
          `Payment failed: ${resp?.error?.description || "unknown error"}`
        );
      });
      rzp.open();
    } catch (e) {
      toast.error(e?.response?.data?.detail || e.message || "Recharge failed");
    } finally {
      setBusy(false);
    }
  };

  if (!d) return <div className="mono text-sm">LOADING WALLET…</div>;

  const p = d.pricing || {};
  const statusKey =
    d.status === "exhausted"
      ? "critical"
      : d.status === "low"
      ? "warning"
      : "safe";

  const isClient = d.status !== undefined; // non-super-admin
  const quickAmounts = [1000, 5000, 10000, 25000, 50000];

  return (
    <div>
      <PageHeader
        eyebrow="Finance"
        title="Wallet & Billing"
        subtitle="Prepaid balance, usage deductions, GST invoices."
      />
      <div className="grid md:grid-cols-3 gap-6 mb-6">
        <Panel title="Balance" className="md:col-span-1">
          <div className="num text-7xl leading-none" data-testid="wallet-balance">
            ₹{Math.round(d.balance)}
          </div>
          <div className="mt-3 flex items-center gap-2">
            <StatusPill value={statusKey}>
              {d.status?.toUpperCase() || "—"}
            </StatusPill>
            <span className="overline text-muted-foreground">
              Plan · {d.subscription_plan?.toUpperCase() || "—"}
            </span>
          </div>
          {d.status === "exhausted" && (
            <div
              className="text-xs text-status-critical mt-3 border border-status-critical/50 p-2"
              data-testid="wallet-readonly-alert"
            >
              🛑 Read-only mode — asset/inspection/user creation blocked.
              Recharge to resume.
            </div>
          )}
          {d.status === "low" && (
            <div
              className="text-xs text-status-warning mt-3 border border-status-warning/50 p-2"
              data-testid="wallet-low-alert"
            >
              ⚠ Balance below ₹{p.low_threshold}. Actions will stop at ₹0.
            </div>
          )}
        </Panel>

        {isClient && (
          <Panel title="Recharge Wallet" className="md:col-span-1">
            <div className="text-xs text-muted-foreground mb-2">
              Prepaid credits · GST invoice issued automatically · Powered by
              Razorpay
            </div>
            <label className="overline text-xs">Amount (₹)</label>
            <input
              type="number"
              min={1}
              step={100}
              value={amount}
              onChange={(e) => setAmount(Number(e.target.value))}
              data-testid="wallet-recharge-amount"
              className="w-full border border-border rounded-none bg-background px-3 py-2 num text-2xl mt-1"
            />
            <div className="flex flex-wrap gap-2 mt-2">
              {quickAmounts.map((v) => (
                <button
                  key={v}
                  onClick={() => setAmount(v)}
                  data-testid={`wallet-quick-${v}`}
                  className="text-xs border border-border px-2 py-1 hover:bg-muted"
                >
                  ₹{v.toLocaleString("en-IN")}
                </button>
              ))}
            </div>
            <button
              onClick={handleRecharge}
              disabled={busy || !cfg.configured}
              data-testid="wallet-recharge-btn"
              className="w-full mt-4 bg-foreground text-background py-3 text-sm font-semibold disabled:opacity-50 hover:opacity-90"
            >
              {busy
                ? "OPENING CHECKOUT…"
                : !cfg.configured
                ? "PAYMENTS UNAVAILABLE"
                : `RECHARGE ₹${Number(amount || 0).toLocaleString("en-IN")}`}
            </button>
            {!cfg.configured && (
              <div className="text-[10px] text-muted-foreground mt-2">
                Razorpay not yet configured on this environment. Contact SSPL.
              </div>
            )}
          </Panel>
        )}

        <Panel title="Usage Pricing" className="md:col-span-1">
          <div className="divide-y divide-border text-sm">
            <div className="flex justify-between py-2">
              <span>Per asset created</span>
              <span className="num text-2xl">₹{p.per_asset}</span>
            </div>
            <div className="flex justify-between py-2">
              <span>Per inspection</span>
              <span className="num text-2xl">₹{p.per_inspection}</span>
            </div>
            <div className="flex justify-between py-2">
              <span>Per user added</span>
              <span className="num text-2xl">₹{p.per_user}</span>
            </div>
            <div className="flex justify-between py-2 text-muted-foreground">
              <span>Low-balance warn</span>
              <span className="mono">₹{p.low_threshold}</span>
            </div>
          </div>
        </Panel>
      </div>

      <Panel title="Transaction Ledger (credits + usage)">
        {d.transactions.length === 0 ? (
          <Empty>No transactions yet.</Empty>
        ) : (
          <table className="w-full text-sm" data-testid="wallet-tx-table">
            <thead>
              <tr className="border-b border-border text-left">
                <th className="overline p-3">Invoice / Ref</th>
                <th className="overline">Date</th>
                <th className="overline">Type</th>
                <th className="overline">Reason</th>
                <th className="overline">Amount</th>
                <th className="overline">GST</th>
                <th className="overline">Balance After</th>
                <th className="overline">Invoice</th>
              </tr>
            </thead>
            <tbody>
              {d.transactions.map((t) => (
                <tr
                  key={t.id}
                  className="border-b border-border last:border-0"
                >
                  <td className="p-3 mono text-xs">
                    {t.gst_invoice_no || t.reference?.slice(0, 12) || "—"}
                  </td>
                  <td className="mono text-xs">{t.created_at.slice(0, 10)}</td>
                  <td>
                    <StatusPill value={t.type === "credit" ? "safe" : "warning"}>
                      {t.type}
                    </StatusPill>
                  </td>
                  <td className="text-xs">{t.reason || t.note || "—"}</td>
                  <td
                    className={`mono ${
                      t.amount < 0 ? "text-status-critical" : ""
                    }`}
                  >
                    ₹{t.amount}
                  </td>
                  <td className="mono text-xs">₹{t.gst_amount || 0}</td>
                  <td className="mono">₹{t.balance_after}</td>
                  <td>
                    {t.gst_invoice_no && t.type === "credit" ? (
                      <a
                        href={`${API}/payments/invoice/${t.gst_invoice_no}`}
                        target="_blank"
                        rel="noreferrer"
                        data-testid={`invoice-dl-${t.gst_invoice_no}`}
                        className="text-xs underline"
                      >
                        PDF
                      </a>
                    ) : (
                      <span className="text-muted-foreground text-xs">—</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Panel>
    </div>
  );
}
