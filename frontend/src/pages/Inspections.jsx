import { useEffect, useState } from "react";
import { http } from "@/lib/api";
import { PageHeader, Panel, StatusPill, Empty } from "@/components/ui-kit";

export default function Inspections() {
  const [items, setItems] = useState([]);
  useEffect(() => { http.get("/inspections").then(r => setItems(r.data)); }, []);
  return (
    <div>
      <PageHeader eyebrow="Operations / Quality" title="Inspections" subtitle="All pass/fail records with timestamp and inspector." />
      <div className="panel">
        {items.length === 0 ? <Empty>No inspections logged yet. Log from an asset page.</Empty> :
          <table className="w-full text-sm" data-testid="inspections-table">
            <thead><tr className="border-b border-border text-left">
              <th className="overline p-3">When</th>
              <th className="overline">Inspector</th>
              <th className="overline">Checks</th>
              <th className="overline">Result</th>
              <th className="overline">Notes</th>
            </tr></thead>
            <tbody>
              {items.map(i => (
                <tr key={i.id} className="border-b border-border last:border-0">
                  <td className="p-3 mono text-xs">{i.created_at.slice(0,16).replace("T"," ")}</td>
                  <td className="font-semibold">{i.inspector_name}</td>
                  <td className="mono text-xs">{i.checklist?.length || 0} items</td>
                  <td><StatusPill value={i.overall_result}>{i.overall_result}</StatusPill></td>
                  <td className="text-xs text-muted-foreground">{i.notes || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>}
      </div>
    </div>
  );
}
