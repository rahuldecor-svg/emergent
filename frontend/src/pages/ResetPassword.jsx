import { useState } from "react";
import { useSearchParams, useNavigate, Link } from "react-router-dom";
import { Flame } from "lucide-react";
import { toast } from "sonner";
import { http, formatApiError } from "@/lib/api";

export default function ResetPassword() {
  const [params] = useSearchParams();
  const token = params.get("token") || "";
  const nav = useNavigate();
  const [pw, setPw] = useState("");
  const [confirm, setConfirm] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    if (pw.length < 8) {
      toast.error("Password must be at least 8 characters");
      return;
    }
    if (pw !== confirm) {
      toast.error("Passwords don't match");
      return;
    }
    if (!token) {
      toast.error("Missing reset token");
      return;
    }
    setBusy(true);
    try {
      await http.post("/auth/password-reset/confirm", {
        token,
        new_password: pw,
      });
      toast.success("Password updated. Sign in with your new password.");
      nav("/login");
    } catch (err) {
      toast.error(
        formatApiError(err.response?.data?.detail) || "Reset failed"
      );
    } finally {
      setBusy(false);
    }
  };

  if (!token) {
    return (
      <div className="min-h-screen grid place-items-center bg-background p-6">
        <div className="w-full max-w-md text-center">
          <h1 className="font-heading font-black tracking-tighter text-3xl">
            Invalid reset link
          </h1>
          <p className="text-muted-foreground mt-4 text-sm">
            The reset link is missing or malformed.
          </p>
          <Link to="/forgot-password" className="inline-block mt-6 underline text-sm">
            Request a new link
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen grid place-items-center bg-background p-6">
      <div className="w-full max-w-md">
        <div className="flex items-center gap-2 mb-6">
          <Flame size={18} />
          <span className="font-heading font-black tracking-tight">
            FIRE COMPLIANCE OS
          </span>
        </div>
        <div className="overline text-muted-foreground">Account recovery</div>
        <h1 className="font-heading font-black tracking-tighter text-4xl mt-2">
          Set a new password
        </h1>

        <form onSubmit={submit} className="mt-8 space-y-4" data-testid="reset-password-form">
          <div>
            <label className="overline block mb-2">New password</label>
            <input
              data-testid="reset-password-new"
              type="password"
              required
              minLength={8}
              value={pw}
              onChange={(e) => setPw(e.target.value)}
              className="w-full bg-card border border-input px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
            <div className="text-[10px] text-muted-foreground mt-1">
              Minimum 8 characters.
            </div>
          </div>
          <div>
            <label className="overline block mb-2">Confirm password</label>
            <input
              data-testid="reset-password-confirm"
              type="password"
              required
              minLength={8}
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              className="w-full bg-card border border-input px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          <button
            type="submit"
            disabled={busy}
            data-testid="reset-password-submit"
            className="w-full bg-primary text-primary-foreground font-semibold py-3 disabled:opacity-50"
          >
            {busy ? "Updating…" : "Update password"}
          </button>
        </form>
      </div>
    </div>
  );
}
