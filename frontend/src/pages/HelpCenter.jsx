import { useEffect, useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { PageHeader, Panel } from "@/components/ui-kit";
import { HELP } from "@/lib/helpContent";
import { getLang, setLang } from "@/lib/i18n";
import { BookOpen, Languages } from "lucide-react";

export default function HelpCenter() {
  const { user } = useAuth();
  const [lang, setLangState] = useState(getLang());
  const [tab, setTab] = useState("user");

  useEffect(() => {
    const on = () => setLangState(getLang());
    window.addEventListener("fos-lang", on);
    return () => window.removeEventListener("fos-lang", on);
  }, []);

  const role = user?.role || "client_admin";
  const visibleTabs = HELP.tabs.filter(t =>
    t.roles.includes("all") || t.roles.includes(role)
  );
  const activeTab = visibleTabs.find(t => t.key === tab) || visibleTabs[0];

  const switchLang = (l) => { setLang(l); setLangState(l); };

  return (
    <div>
      <PageHeader
        eyebrow="Help Center"
        title={lang === "hi" ? "Madad aur Guides" : "Help & Guides"}
        subtitle={lang === "hi"
          ? "Step-by-step guides, FAQ aur legal terms. Hindi / English me available."
          : "Step-by-step guides, FAQ and legal terms. Hindi and English."}
        actions={
          <div className="flex border border-border" data-testid="lang-toggle">
            <button onClick={() => switchLang("en")}
              data-testid="lang-en"
              className={`px-3 py-2 text-xs font-semibold ${lang === "en" ? "bg-primary text-primary-foreground" : ""}`}>
              <Languages size={12} className="inline mr-1" /> EN
            </button>
            <button onClick={() => switchLang("hi")}
              data-testid="lang-hi"
              className={`px-3 py-2 text-xs font-semibold ${lang === "hi" ? "bg-primary text-primary-foreground" : ""}`}>
              HI
            </button>
          </div>
        }
      />

      <div className="flex flex-wrap gap-2 mb-6 border-b border-border" data-testid="help-tabs">
        {visibleTabs.map(t => (
          <button key={t.key}
            onClick={() => setTab(t.key)}
            data-testid={`tab-${t.key}`}
            className={`px-4 py-2 text-sm font-semibold border-b-2 -mb-px ${
              activeTab.key === t.key ? "border-primary text-primary" : "border-transparent text-muted-foreground hover:text-foreground"
            }`}>
            {lang === "hi" ? t.label_hi : t.label_en}
          </button>
        ))}
      </div>

      {activeTab.key === "faq" ? (
        <FaqBlock items={HELP.faq[lang]} />
      ) : activeTab.key === "terms" ? (
        <TermsBlock items={HELP.terms[lang]} lang={lang} />
      ) : (
        <StepsBlock items={HELP[activeTab.key][lang]} />
      )}
    </div>
  );
}

function StepsBlock({ items }) {
  return (
    <div className="grid md:grid-cols-2 gap-6">
      {items.map((s, i) => (
        <Panel key={i} title={<span className="text-sm"><BookOpen size={14} className="inline mr-2" />{s.title}</span>}>
          <ol className="list-decimal pl-5 space-y-2 text-sm leading-relaxed">
            {s.steps.map((line, j) => <li key={j}>{line}</li>)}
          </ol>
        </Panel>
      ))}
    </div>
  );
}

function FaqBlock({ items }) {
  return (
    <div className="divide-y divide-border border border-border" data-testid="faq-list">
      {items.map((f, i) => (
        <details key={i} className="group p-4">
          <summary className="cursor-pointer font-semibold text-sm flex justify-between items-center">
            <span>Q. {f.q}</span>
            <span className="overline text-muted-foreground group-open:rotate-180 transition-transform">▾</span>
          </summary>
          <p className="mt-3 text-sm text-muted-foreground">{f.a}</p>
        </details>
      ))}
    </div>
  );
}

function TermsBlock({ items, lang }) {
  return (
    <div className="max-w-3xl" data-testid="terms-block">
      <div className="overline text-muted-foreground mb-4">
        {lang === "hi" ? "Niyam aur Disclaimer" : "Terms & Disclaimer"}
      </div>
      <ol className="list-decimal pl-5 space-y-4 text-sm leading-relaxed">
        {items.map((t, i) => <li key={i}>{t}</li>)}
      </ol>
      <p className="mt-8 mono text-xs text-muted-foreground">
        © {new Date().getFullYear()} Securrise Solution Pvt Ltd (SSPL). All rights reserved.
      </p>
    </div>
  );
}
