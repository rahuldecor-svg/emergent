import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Html5Qrcode } from "html5-qrcode";
import { PageHeader, Btn, Panel } from "@/components/ui-kit";
import { toast } from "sonner";
import { QrCode, Camera, X } from "lucide-react";

export default function QrScan() {
  const nav = useNavigate();
  const scannerRef = useRef(null);
  const [running, setRunning] = useState(false);
  const [err, setErr] = useState("");
  const [cameras, setCameras] = useState([]);
  const [camId, setCamId] = useState("");
  const [manual, setManual] = useState("");

  // Pre-list cameras (prefer back camera on mobile)
  useEffect(() => {
    Html5Qrcode.getCameras().then((list) => {
      setCameras(list);
      const back = list.find(c => /back|rear|environment/i.test(c.label));
      setCamId((back || list[0])?.id || "");
    }).catch(() => setCameras([]));
    return () => stop();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleDecoded = (text) => {
    stop();
    // Try to extract asset UUID from URL or treat raw text as ID
    const m = text.match(/\/app\/assets\/([a-f0-9-]{10,})/i);
    const id = m ? m[1] : text.trim();
    toast.success("QR detected — opening asset…");
    nav(`/app/assets/${id}`);
  };

  const start = async () => {
    setErr("");
    if (!camId) { setErr("No camera detected on this device."); return; }
    try {
      scannerRef.current = new Html5Qrcode("qr-reader");
      await scannerRef.current.start(
        camId,
        { fps: 10, qrbox: { width: 240, height: 240 } },
        handleDecoded,
        () => {} // ignore per-frame decode errors
      );
      setRunning(true);
    } catch (e) {
      setErr(e?.message || "Camera access denied. Please allow camera in your browser settings.");
    }
  };

  const stop = async () => {
    try {
      if (scannerRef.current?.isScanning) {
        await scannerRef.current.stop();
        await scannerRef.current.clear();
      }
    } catch { /* ignore */ }
    setRunning(false);
  };

  const submitManual = (e) => {
    e.preventDefault();
    if (!manual.trim()) return;
    handleDecoded(manual.trim());
  };

  return (
    <div>
      <PageHeader
        eyebrow="Field / Scan"
        title="Scan Asset QR"
        subtitle="Point the camera at the QR sticker on any fire asset."
      />
      <div className="grid lg:grid-cols-5 gap-6">
        <Panel title="Camera" className="lg:col-span-3">
          <div className="relative aspect-square bg-black overflow-hidden">
            <div id="qr-reader" className="absolute inset-0 w-full h-full" data-testid="qr-reader" />
            {!running && (
              <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-6 text-primary-foreground bg-black/80">
                <QrCode size={48} className="mb-4 opacity-70" />
                <div className="text-sm opacity-80 mb-4">Tap start to enable the camera.</div>
                <Btn onClick={start} data-testid="scan-start-btn">
                  <Camera size={14} /> Start Camera
                </Btn>
                {err && <div className="text-xs text-destructive mt-4 max-w-xs" data-testid="scan-error">{err}</div>}
              </div>
            )}
            {running && (
              <>
                <div className="absolute inset-x-0 top-0 bg-black/70 text-white text-xs px-3 py-2 flex items-center justify-between z-10">
                  <span>Scanning… hold steady</span>
                  <button onClick={stop} data-testid="scan-stop-btn" className="flex items-center gap-1 text-xs">
                    <X size={12} /> Stop
                  </button>
                </div>
                <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-60 h-60 border-2 border-destructive pointer-events-none">
                  <div className="w-full h-0.5 bg-destructive/70 animate-scan-line" />
                </div>
              </>
            )}
          </div>
          {cameras.length > 1 && (
            <div className="mt-3">
              <label className="overline block mb-1">Camera</label>
              <select value={camId} onChange={e => setCamId(e.target.value)}
                className="w-full border border-input bg-card px-3 py-2 text-sm"
                data-testid="scan-cam-select">
                {cameras.map(c => <option key={c.id} value={c.id}>{c.label || c.id.slice(0,8)}</option>)}
              </select>
            </div>
          )}
        </Panel>

        <Panel title="Or paste the code" className="lg:col-span-2">
          <form onSubmit={submitManual} className="space-y-3" data-testid="manual-scan-form">
            <input value={manual} onChange={e => setManual(e.target.value)}
              data-testid="manual-scan-input"
              placeholder="Paste URL or asset ID…"
              className="w-full border border-input bg-card px-3 py-2 text-sm font-mono" />
            <Btn type="submit" data-testid="manual-scan-submit">Open Asset</Btn>
          </form>
          <div className="mt-6 text-xs text-muted-foreground space-y-1">
            <div className="overline">Tips</div>
            <ul className="list-disc pl-4 space-y-1">
              <li>Allow camera permission when prompted.</li>
              <li>Hold steady at ~15 cm from the sticker.</li>
              <li>Good light helps. Clean the lens.</li>
            </ul>
          </div>
        </Panel>
      </div>
    </div>
  );
}
