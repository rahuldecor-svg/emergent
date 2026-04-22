export function PageHeader({ eyebrow, title, subtitle, actions }) {
  return (
    <div className="flex flex-wrap items-end justify-between gap-4 mb-8 pb-6 border-b border-border">
      <div>
        {eyebrow && <div className="overline text-muted-foreground">{eyebrow}</div>}
        <h1 className="font-heading font-black tracking-tighter text-3xl md:text-4xl mt-1">{title}</h1>
        {subtitle && <p className="text-sm text-muted-foreground mt-2 max-w-2xl">{subtitle}</p>}
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </div>
  );
}

export function Panel({ title, children, action, className = "" }) {
  return (
    <div className={`panel ${className}`}>
      {(title || action) && (
        <div className="flex items-center justify-between px-4 py-3 border-b border-border">
          {title && <div className="overline">{title}</div>}
          {action}
        </div>
      )}
      <div className="p-4">{children}</div>
    </div>
  );
}

const STATUS = {
  safe: "border-status-success text-status-success",
  ok: "border-status-success text-status-success",
  active: "border-status-success text-status-success",
  pass: "border-status-success text-status-success",
  success: "border-status-success text-status-success",
  warning: "border-status-warning text-status-warning",
  expiring: "border-status-warning text-status-warning",
  scheduled: "border-status-warning text-status-warning",
  critical: "border-status-critical text-status-critical",
  expired: "border-status-critical text-status-critical",
  faulty: "border-status-critical text-status-critical",
  fail: "border-status-critical text-status-critical",
  missed: "border-status-critical text-status-critical",
  high: "border-status-critical text-status-critical",
  medium: "border-status-warning text-status-warning",
  low: "border-status-success text-status-success",
  open: "border-status-critical text-status-critical",
  completed: "border-status-success text-status-success",
  in_progress: "border-status-warning text-status-warning",
};

export function StatusPill({ value, children }) {
  const cls = STATUS[value] || "border-muted-foreground text-muted-foreground";
  return (
    <span className={`pill ${cls} bg-card`} data-testid={`status-${value}`}>
      <span className={`w-1.5 h-1.5 ${cls.replace("text-", "bg-").replace("border-", "bg-")}`} />
      {children || value}
    </span>
  );
}

export function Empty({ children }) {
  return <div className="text-sm text-muted-foreground border border-dashed border-border p-8 text-center">{children}</div>;
}

export function Btn({ children, variant = "primary", className = "", ...rest }) {
  const base = "px-3 py-2 text-xs font-semibold inline-flex items-center gap-2 transition-transform active:scale-95";
  const v = variant === "primary"
    ? "bg-primary text-primary-foreground hover:bg-slate-900"
    : variant === "destructive"
    ? "bg-destructive text-destructive-foreground hover:opacity-90"
    : "border border-border hover:bg-primary hover:text-primary-foreground";
  return <button className={`${base} ${v} ${className}`} {...rest}>{children}</button>;
}
