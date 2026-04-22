import { useState } from "react";
import { Link } from "react-router-dom";
import { Flame, ArrowLeft } from "lucide-react";
import { toast } from "sonner";
import { http, formatApiError } from "@/lib/api";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [sent, setSent] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    try {
      await http.post("/auth/password-reset/request", {
        email: email.trim().toLowerCase(),
      });
      setSent(true);
    } catch (err) {
      toast.error(formatApiError(err.response?.data?.detail) || "Failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-screen grid place-items-center bg-background p-6">
      <div className="w-full max-w-md">
        <Link to="/login" className="inline-flex items-center gap-2 text-sm mb-8 text-muted-foreground hover:text-foreground" data-testid="back-to-login-link">
          <ArrowLeft size={14} /> Back to sign in
        </Link>
        <div className="flex items-center gap-2 mb-6">
          <Flame size={18} />
          <span className="font-heading font-black tracking-tight">FIRE COMPLIANCE OS</span>
        </div>
        <div className="overline text-muted-foreground">Account recovery</div>
        <h1 className="font-heading font-black tracking-tighter text-4xl mt-2">
          Forgot password
        </h1>

        {sent ? (
          <div className="mt-8 border border-border p-4 text-sm" data-testid="forgot-password-sent">
            <div className="font-semibold">Check your inbox.</div>
            <div className="text-muted-foreground mt-2">
              If an account with <b>{email}</b> exists, we've sent password reset
              instructions. The link expires in 1 hour.
            </div>
            <Link to="/login" className="inline-block mt-4 text-xs underline">
              Return to sign in
            </Link>
          </div>
        ) : (
          <form onSubmit={submit} className="mt-8 space-y-4" data-testid="forgot-password-form">
            <p className="text-sm text-muted-foreground">
              Enter your email and we'll send a secure reset link.
            </p>
            <div>
              <label className="overline block mb-2">Email</label>
              <input
                data-testid="forgot-password-email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-card border border-input px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <button
              type="submit"
              disabled={busy}
              data-testid="forgot-password-submit"
              className="w-full bg-primary text-primary-foreground font-semibold py-3 disabled:opacity-50"
            >
              {busy ? "Sending…" : "Send reset link"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
