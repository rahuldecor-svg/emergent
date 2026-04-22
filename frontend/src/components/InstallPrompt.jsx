import { useEffect, useState } from "react";
import { toast } from "sonner";
import { Download, X } from "lucide-react";

/**
 * "Add to Home Screen" prompt — renders a banner the first time Chrome/Android
 * fires beforeinstallprompt. Dismissed choice is persisted for 7 days.
 */
export default function InstallPrompt() {
  const [ev, setEv] = useState(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const dismissedAt = Number(localStorage.getItem("fos_install_dismissed") || 0);
    const recent = Date.now() - dismissedAt < 7 * 24 * 60 * 60 * 1000;
    const onPrompt = (e) => {
      e.preventDefault();
      setEv(e);
      if (!recent) setVisible(true);
    };
    const onInstalled = () => {
      setVisible(false); setEv(null);
      toast.success("Fire OS installed to your device");
    };
    window.addEventListener("beforeinstallprompt", onPrompt);
    window.addEventListener("appinstalled", onInstalled);
    return () => {
      window.removeEventListener("beforeinstallprompt", onPrompt);
      window.removeEventListener("appinstalled", onInstalled);
    };
  }, []);

  if (!visible || !ev) return null;

  const install = async () => {
    try {
      ev.prompt();
      const { outcome } = await ev.userChoice;
      if (outcome !== "accepted") {
        localStorage.setItem("fos_install_dismissed", String(Date.now()));
      }
    } catch { /* ignore */ }
    setVisible(false); setEv(null);
  };

  const dismiss = () => {
    localStorage.setItem("fos_install_dismissed", String(Date.now()));
    setVisible(false);
  };

  return (
    <div className="fixed left-0 right-0 bottom-0 z-40 md:bottom-6 md:left-auto md:right-6 md:max-w-sm"
         data-testid="install-prompt">
      <div className="panel bg-primary text-primary-foreground p-4 shadow-xl md:border">
        <div className="flex items-start gap-3">
          <Download size={18} className="mt-0.5 shrink-0" />
          <div className="flex-1">
            <div className="font-heading font-bold">Install Fire OS</div>
            <div className="text-xs opacity-80 mt-1">
              Add to home screen for faster, full-screen access on the field.
            </div>
            <div className="flex gap-2 mt-3">
              <button onClick={install}
                data-testid="install-accept"
                className="px-3 py-1.5 bg-primary-foreground text-primary text-xs font-semibold">
                Install
              </button>
              <button onClick={dismiss}
                data-testid="install-dismiss"
                className="px-3 py-1.5 border border-primary-foreground/40 text-xs font-semibold">
                Not now
              </button>
            </div>
          </div>
          <button onClick={dismiss} className="opacity-60 hover:opacity-100" aria-label="Close">
            <X size={14} />
          </button>
        </div>
      </div>
    </div>
  );
}
