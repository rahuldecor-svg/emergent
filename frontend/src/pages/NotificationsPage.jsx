import { useEffect, useState } from "react";
import { http } from "@/lib/api";
import { PageHeader, Panel, Btn, Empty } from "@/components/ui-kit";

export default function NotificationsPage() {
  const [data, setData] = useState({ items: [], unread: 0 });

  const load = async () => { const { data } = await http.get("/notifications"); setData(data); };
  useEffect(() => { load(); }, []);

  const markAll = async () => { await http.post("/notifications/read-all"); load(); };
  const markOne = async (id) => { await http.post(`/notifications/${id}/read`); load(); };

  return (
    <div>
      <PageHeader
        eyebrow="Alerts" title="Notifications"
        subtitle="Compliance-critical updates, incidents and wallet events."
        actions={data.unread ? <Btn onClick={markAll} data-testid="mark-all-read">Mark all read</Btn> : null}
      />
      <div className="panel">
        {data.items.length === 0 ? <Empty>All clear. No alerts.</Empty> :
          data.items.map(n => (
            <div key={n.id}
              className={`p-4 border-b border-border last:border-0 flex justify-between items-start gap-3 ${!n.read ? "bg-secondary" : ""}`}
              data-testid={`notif-${n.id}`}>
              <div>
                <div className="flex items-center gap-2">
                  <div className={`w-1.5 h-1.5 ${!n.read ? "bg-destructive animate-pulse-dot" : "bg-muted-foreground"}`} />
                  <div className="font-semibold text-sm">{n.title}</div>
                </div>
                <div className="text-xs text-muted-foreground mt-1">{n.body}</div>
                <div className="mono text-[10px] text-muted-foreground mt-1">{n.created_at.slice(0,16).replace("T"," ")} · {n.kind}</div>
              </div>
              {!n.read && <Btn variant="outline" onClick={() => markOne(n.id)}>Mark read</Btn>}
            </div>
          ))}
      </div>
    </div>
  );
}
