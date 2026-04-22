import { Link } from "react-router-dom";
import { HELP } from "@/lib/helpContent";
import { getLang, setLang } from "@/lib/i18n";
import { useEffect, useState } from "react";
import { Flame } from "lucide-react";

export default function Terms() {
  const [lang, setLangState] = useState(getLang());
  useEffect(() => {
    const on = () => setLangState(getLang());
    window.addEventListener("fos-lang", on);
    return () => window.removeEventListener("fos-lang", on);
  }, []);

  const switchLang = (l) => { setLang(l); setLangState(l); };

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-background sticky top-0 z-10">
        <div className="max-w-4xl mx-auto flex items-center justify-between px-6 py-4">
          <Link to="/" className="flex items-center gap-2" data-testid="terms-brand">
            <Flame size={18} className="text-destructive" />
            <span className="font-heading font-black tracking-tight">FIRE COMPLIANCE OS</span>
          </Link>
          <div className="flex items-center gap-4 text-xs">
            <div className="flex border border-border">
              <button onClick={() => switchLang("en")}
                className={`px-2 py-1 ${lang === "en" ? "bg-primary text-primary-foreground" : ""}`}>EN</button>
              <button onClick={() => switchLang("hi")}
                className={`px-2 py-1 ${lang === "hi" ? "bg-primary text-primary-foreground" : ""}`}>HI</button>
            </div>
            <Link to="/" className="overline text-muted-foreground hover:text-primary">← Home</Link>
          </div>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-6 py-14">
        <div className="overline text-muted-foreground">Legal</div>
        <h1 className="font-heading font-black tracking-tighter text-4xl md:text-5xl mt-2 mb-2">
          {lang === "hi" ? "Niyam & Disclaimer" : "Terms & Disclaimer"}
        </h1>
        <p className="text-sm text-muted-foreground mb-10">
          {lang === "hi"
            ? "Fire Compliance OS use karte samay ye baatein dhyan me rakhein."
            : "Please read carefully before using Fire Compliance OS."}
        </p>
        <ol className="list-decimal pl-5 space-y-5 text-base leading-relaxed">
          {HELP.terms[lang].map((t, i) => <li key={i}>{t}</li>)}
        </ol>
        <div className="mt-12 pt-6 border-t border-border mono text-xs text-muted-foreground">
          © {new Date().getFullYear()} Securrise Solution Pvt Ltd (SSPL). All rights reserved.
        </div>
      </main>
    </div>
  );
}
