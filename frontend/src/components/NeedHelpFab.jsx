import { useState } from "react";
import { Link } from "react-router-dom";
import { LifeBuoy, X, BookOpen, PhoneCall, MessageSquarePlus } from "lucide-react";

/**
 * Floating "Need Help" button (bottom-right) with 3 actions:
 * - Raise support request
 * - Call support (placeholder number)
 * - Open Help Center
 */
export default function NeedHelpFab() {
  const [open, setOpen] = useState(false);

  return (
    <div className="fixed bottom-6 right-6 z-30" data-testid="need-help-fab">
      {open && (
        <div className="mb-3 panel bg-card w-64 p-3 shadow-lg" data-testid="need-help-menu">
          <div className="overline text-muted-foreground mb-2">Need Help?</div>
          <Link to="/app/help" onClick={() => setOpen(false)}
            data-testid="help-goto-center"
            className="flex items-center gap-3 p-2 hover:bg-secondary text-sm">
            <BookOpen size={14} /> Help Center & FAQ
          </Link>
          <Link to="/app/support" onClick={() => setOpen(false)}
            data-testid="help-raise-request"
            className="flex items-center gap-3 p-2 hover:bg-secondary text-sm">
            <MessageSquarePlus size={14} /> Raise service request
          </Link>
          <a href="tel:+919999999999" onClick={() => setOpen(false)}
            data-testid="help-call-support"
            className="flex items-center gap-3 p-2 hover:bg-secondary text-sm">
            <PhoneCall size={14} /> Call SSPL support
          </a>
          <div className="mono text-[10px] text-muted-foreground mt-2">Mon–Sat · 09:00–19:00 IST</div>
        </div>
      )}
      <button onClick={() => setOpen(v => !v)}
        data-testid="need-help-btn"
        className="w-12 h-12 bg-primary text-primary-foreground flex items-center justify-center hover:bg-slate-900 transition-transform active:scale-95 shadow-lg">
        {open ? <X size={18} /> : <LifeBuoy size={18} />}
      </button>
    </div>
  );
}
