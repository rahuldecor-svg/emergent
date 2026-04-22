import { useEffect, useState } from "react";
import { http, API } from "@/lib/api";
import { PageHeader, Panel, StatusPill, Btn, Empty } from "@/components/ui-kit";
import { Link } from "react-router-dom";
import { Modal, Field } from "./ClientsAdmin";
import { toast } from "sonner";
import { friendly, getLang } from "@/lib/i18n";
import { Printer } from "lucide-react";

export default function Assets() {
  const [assets, setAssets] = useState([]);
  const [sites, setSites] = useState([]);
  const [showNew, setShowNew] = useState(false);
  const [filter, setFilter] = useState("all");
  const [selected, setSelected] = useState(new Set());
  const [printLayout, setPrintLayout] = useState(10);

  const load = async () => {
    const [a, s] = await Promise.all([http.get("/assets"), http.get("/sites")]);
    setAssets(a.data); setSites(s.data);
  };
  useEffect(() => { load(); }, []);

  const filtered = assets.filter(a => filter === "all" ? true : a.expiry_status === filter);

  const toggleSel = (id) => {
    const n = new Set(selected);
    n.has(id) ? n.delete(id) : n.add(id);
    setSelected(n);
  };

  const printSheet = async () => {
    if (!selected.size) { toast.error("Select at least one asset to print"); return; }
    try {
      const res = await http.post("/qr/sheet",
        { asset_ids: [...selected], layout: Number(printLayout) },
        { responseType: "blob" });
      const url = window.URL.createObjectURL(new Blob([res.data], { type: "application/pdf" }));
      window.open(url, "_blank");
      toast.success(`Printed ${selected.size} QR codes (${printLayout}/page)`);
    } catch (e) {
      toast.error(friendly(e.response?.data?.detail, getLang()));
    }
  };

  return (
    <div>
      <PageHeader
        eyebrow="Field / Asset Register"
        title="Fire Assets"
        subtitle="Every extinguisher, hydrant, sprinkler, alarm, hose — tagged, tracked and traceable."
        actions={<>
          <Btn variant="outline" onClick={printSheet} disabled={!selected.size} data-testid="print-qr-sheet-btn">
            <Printer size={12} /> Print QR ({selected.size})
          </Btn>
          <select value={printLayout} onChange={e => setPrintLayout(e.target.value)}
            data-testid="qr-layout-select"
            className="border border-input bg-card px-2 py-1 text-xs">
            <option value="1">1 / page</option>
            <option value="10">10 / page</option>
            <option value="20">20 / page</option>
          </select>
          <Btn onClick={() => setShowNew(true)} data-testid="add-asset-btn">+ Add Asset</Btn>
        </>}
      />
      <div className="flex gap-2 mb-4" data-testid="asset-filters">
        {["all", "ok", "expiring", "expired"].map(f => (
          <button key={f} onClick={() => setFilter(f)}
            data-testid={`filter-${f}`}
            className={`px-3 py-1.5 text-xs uppercase font-semibold border ${filter === f ? "bg-primary text-primary-foreground border-primary" : "border-border hover:bg-secondary"}`}>
            {f} {f !== "all" && <span className="ml-1 mono">{assets.filter(a => a.expiry_status === f).length}</span>}
          </button>
        ))}
      </div>

      <div className="panel">
        <table className="w-full text-sm" data-testid="assets-table">
          <thead><tr className="border-b border-border text-left">
            <th className="p-3 w-8"></th>
            <th className="overline">Name</th>
            <th className="overline">Category</th>
            <th className="overline">Serial</th>
            <th className="overline">Site</th>
            <th className="overline">Installed</th>
            <th className="overline">Expiry</th>
            <th className="overline">Status</th>
          </tr></thead>
          <tbody>
            {filtered.length === 0 && <tr><td colSpan={8}><Empty>No assets match filter.</Empty></td></tr>}
            {filtered.map(a => (
              <tr key={a.id} className="border-b border-border last:border-0 hover:bg-secondary">
                <td className="p-3">
                  <input type="checkbox" checked={selected.has(a.id)}
                    data-testid={`select-${a.id}`}
                    onChange={() => toggleSel(a.id)} className="w-4 h-4 accent-primary" />
                </td>
                <td><Link to={`/app/assets/${a.id}`} className="font-semibold hover:underline">{a.name}</Link></td>
                <td className="uppercase mono text-xs">{a.category}</td>
                <td className="mono text-xs">{a.serial_number || "—"}</td>
                <td className="text-xs">{sites.find(s => s.id === a.site_id)?.name || "—"}</td>
                <td className="mono text-xs">{a.install_date}</td>
                <td className="mono text-xs">{a.expiry_date}</td>
                <td><StatusPill value={a.expiry_status}>{a.expiry_status}</StatusPill></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showNew && <NewAssetModal sites={sites} onClose={() => setShowNew(false)} onDone={() => { setShowNew(false); load(); }} />}
    </div>
  );
}

function NewAssetModal({ sites, onClose, onDone }) {
  const [master, setMaster] = useState([]);
  const [pickedCat, setPickedCat] = useState("");
  const [pickedSub, setPickedSub] = useState("");
  const [f, setF] = useState({
    site_id: sites[0]?.id || "", name: "", category: "extinguisher",
    sub_type: "", serial_number: "", manufacturer: "",
    install_date: new Date().toISOString().slice(0, 10),
    expiry_date: new Date(Date.now() + 365 * 86400000).toISOString().slice(0, 10),
    location_note: "",
  });

  useEffect(() => { http.get("/asset-master").then(r => setMaster(r.data.categories)); }, []);

  const pickTemplate = (cat, sub) => {
    setPickedCat(cat.category); setPickedSub(sub.sub_type);
    setF(prev => ({
      ...prev, category: cat.category, sub_type: sub.sub_type,
      name: prev.name || sub.sub_type,
    }));
  };

  const submit = async (e) => {
    e.preventDefault();
    try {
      const { data } = await http.post("/assets", f);
      const c = data.wallet_charge;
      toast.success(
        c ? `Asset added · −₹${c.cost} (${c.reason}). Balance ₹${c.balance_after}` : "Asset added",
      );
      onDone();
    } catch (e) {
      toast.error(friendly(e.response?.data?.detail, getLang()));
    }
  };

  return (
    <Modal title="Add Fire Asset" onClose={onClose}>
      <form onSubmit={submit} className="space-y-3" data-testid="new-asset-form">
        <div>
          <label className="overline block mb-2">Pick from Asset Master (optional)</label>
          <div className="border border-border max-h-44 overflow-y-auto" data-testid="asset-master-picker">
            {master.map(cat => (
              <div key={cat.category} className="border-b border-border last:border-0">
                <div className="bg-secondary px-2 py-1 text-xs font-bold uppercase">{cat.label}</div>
                <div className="flex flex-wrap gap-1 p-2">
                  {cat.templates.map(t => (
                    <button key={t.sub_type} type="button"
                      onClick={() => pickTemplate(cat, t)}
                      data-testid={`tpl-${cat.category}-${t.sub_type.replace(/\s/g,"_")}`}
                      className={`text-xs px-2 py-1 border ${
                        pickedCat === cat.category && pickedSub === t.sub_type
                          ? "bg-primary text-primary-foreground border-primary"
                          : "border-border hover:bg-secondary"
                      }`}>
                      {t.sub_type}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
        <div>
          <label className="overline block mb-1">Site</label>
          <select className="w-full border border-input bg-card px-3 py-2 text-sm"
            value={f.site_id} onChange={e => setF({...f, site_id: e.target.value})} required>
            {sites.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
        </div>
        <Field label="NAME" value={f.name} onChange={v => setF({...f, name: v})} required />
        <div>
          <label className="overline block mb-1">Category</label>
          <select className="w-full border border-input bg-card px-3 py-2 text-sm"
            value={f.category} onChange={e => setF({...f, category: e.target.value})}>
            {["extinguisher","hydrant","sprinkler","alarm","hose","pump","other"].map(c => <option key={c}>{c}</option>)}
          </select>
        </div>
        <Field label="SUB-TYPE (e.g. CO2 4.5kg)" value={f.sub_type} onChange={v => setF({...f, sub_type: v})} />
        <Field label="SERIAL NUMBER" value={f.serial_number} onChange={v => setF({...f, serial_number: v})} />
        <Field label="MANUFACTURER" value={f.manufacturer} onChange={v => setF({...f, manufacturer: v})} />
        <div className="grid grid-cols-2 gap-2">
          <Field label="INSTALL DATE" type="date" value={f.install_date} onChange={v => setF({...f, install_date: v})} />
          <Field label="EXPIRY DATE" type="date" value={f.expiry_date} onChange={v => setF({...f, expiry_date: v})} />
        </div>
        <Field label="LOCATION NOTE" value={f.location_note} onChange={v => setF({...f, location_note: v})} />
        <div className="flex justify-end gap-2 pt-3">
          <Btn type="button" variant="outline" onClick={onClose}>Cancel</Btn>
          <Btn type="submit" data-testid="create-asset-submit">Create</Btn>
        </div>
      </form>
    </Modal>
  );
}
