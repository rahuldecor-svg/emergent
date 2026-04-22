/**
 * Help Center content — English + Hindi side-by-side.
 * Keep simple, step-by-step, non-technical.
 */
export const HELP = {
  tabs: [
    { key: "user", label_en: "User Manual", label_hi: "User Manual", roles: ["client_admin", "fire_officer", "auditor"] },
    { key: "field", label_en: "Field Guide", label_hi: "Field Guide", roles: ["client_admin", "fire_officer", "technician"] },
    { key: "qr", label_en: "QR Printing", label_hi: "QR Printing", roles: ["client_admin", "fire_officer", "technician"] },
    { key: "faq", label_en: "FAQ", label_hi: "Sawal-Jawab", roles: ["all"] },
    { key: "support", label_en: "Support SOP", label_hi: "Support SOP", roles: ["super_admin"] },
    { key: "terms", label_en: "Terms & Disclaimer", label_hi: "Niyam-Shartein", roles: ["all"] },
  ],

  user: {
    en: [
      { title: "Sign in / Reset password", steps: [
        "Open the Fire Compliance OS login page.",
        "Enter the email and password shared by SSPL.",
        "Forgot password? Contact your SSPL account manager or client admin.",
        "If login fails 5 times in a row the account is locked for 15 minutes.",
      ]},
      { title: "Add your first site", steps: [
        "Open the Sites page from the sidebar.",
        "Click + Add Site.",
        "Enter site name, address and coordinates (if known).",
        "Click Save. The site is now available when adding assets.",
      ]},
      { title: "Add fire assets", steps: [
        "Open Assets from the sidebar.",
        "Click + Add Asset.",
        "Pick a category (extinguisher, hydrant, sprinkler, alarm, hose, pump).",
        "Select a sub-type from the list, or type a custom one.",
        "Enter install date, expiry date and serial number.",
        "Save — ₹10 is deducted from wallet; a QR is generated automatically.",
      ]},
      { title: "Print QR codes for equipment", steps: [
        "Open an asset and click Download QR PDF for a single label.",
        "Or open Assets list and select multiple rows, click Print QR Sheet.",
        "Choose layout: 1 / 10 / 20 QR codes per A4 page.",
        "Recommended size: 2×2 inch. Use sticker or laminated print for durability.",
      ]},
      { title: "Perform an inspection", steps: [
        "Open an asset page (or scan the QR on the equipment).",
        "Click + Log Inspection.",
        "Tick each checklist item as OK or fail.",
        "Add notes, sign, and submit.",
        "₹5 is deducted from wallet. On failure, admins get a critical alert.",
      ]},
      { title: "Read the Fire Safety Score", steps: [
        "Open the Dashboard — the large number is your real-time score (0–100).",
        "Safe ≥ 85, Warning 60–84, Critical < 60.",
        "Each expired asset lowers the score by 8; each missed maintenance by 4.",
        "The 6-month trend chart shows the direction of travel.",
      ]},
      { title: "Download the compliance PDF report", steps: [
        "Open Dashboard → Download Compliance Report (PDF).",
        "The report includes score, NOC readiness, expired list, failed inspections.",
        "Share it with auditors, board, or insurance. SSPL-branded.",
      ]},
      { title: "Wallet and recharge", steps: [
        "Wallet deducts on creation: ₹10 per asset, ₹5 per inspection, ₹20 per user.",
        "Warning appears below ₹500 balance.",
        "At ₹0 the platform enters read-only mode — new creations blocked.",
        "Contact your SSPL manager for recharge. GST invoice is auto-generated.",
      ]},
    ],
    hi: [
      { title: "Sign in / Password reset", steps: [
        "Fire Compliance OS ki login page kholein.",
        "SSPL dwara diya gaya email aur password daalein.",
        "Password bhool gaye? Apne SSPL account manager ya client admin se sampark karein.",
        "Lagataar 5 galat login pe account 15 minute ke liye lock ho jata hai.",
      ]},
      { title: "Apni pehli site add karein", steps: [
        "Sidebar se Sites page kholein.",
        "+ Add Site par click karein.",
        "Site ka naam, address aur coordinates bharein.",
        "Save karein. Ab is site par assets add kar sakte hain.",
      ]},
      { title: "Fire assets add karein", steps: [
        "Sidebar se Assets kholein.",
        "+ Add Asset par click karein.",
        "Category chunein (extinguisher, hydrant, sprinkler, alarm, hose, pump).",
        "List me se sub-type chunein, ya custom likhein.",
        "Install date, expiry date, serial number daalein.",
        "Save — wallet se ₹10 kata jayega; QR apne aap ban jayega.",
      ]},
      { title: "Equipment ke liye QR print karein", steps: [
        "Kisi asset ko kholkar Download QR PDF par click karein (single label).",
        "Ya Assets list me multiple assets select karke Print QR Sheet par click karein.",
        "Layout chunein: 1 / 10 / 20 QR per A4 page.",
        "Recommended size 2×2 inch. Sticker ya laminated print istemaal karein.",
      ]},
      { title: "Inspection karein", steps: [
        "Asset page kholein (ya equipment pe laga QR scan karein).",
        "+ Log Inspection par click karein.",
        "Har checklist item ko OK ya fail tick karein.",
        "Note daalein, signature karein, submit karein.",
        "₹5 wallet se katega. Fail hone par admins ko critical alert jaata hai.",
      ]},
      { title: "Fire Safety Score kaise padhein", steps: [
        "Dashboard kholein — bada number aapka real-time score (0–100) hai.",
        "Safe ≥ 85, Warning 60–84, Critical 60 se kam.",
        "Har expired asset se 8 points, missed maintenance se 4 points kate hain.",
        "6 mahine ka trend chart direction dikhata hai.",
      ]},
      { title: "Compliance PDF report download karein", steps: [
        "Dashboard → Download Compliance Report (PDF) par click karein.",
        "Report me score, NOC readiness, expired list, failed inspections hoti hain.",
        "Auditors, management ya insurance ke saath share kar sakte hain. SSPL branded.",
      ]},
      { title: "Wallet aur recharge", steps: [
        "Wallet deduction: ₹10 per asset, ₹5 per inspection, ₹20 per user.",
        "Balance ₹500 se kam hone par warning aayegi.",
        "₹0 hone par platform read-only ho jata hai — nayi creation block.",
        "Recharge ke liye SSPL manager se sampark karein. GST invoice auto-generate hota hai.",
      ]},
    ],
  },

  field: {
    en: [
      { title: "Daily technician workflow", steps: [
        "Sign in from the phone or tablet with your technician login.",
        "Open Maintenance — you will see only tasks assigned to you.",
        "Walk to the asset, scan the QR or open it from the app.",
        "Log the inspection: tick checklist, add photos, add notes, sign.",
        "Click Mark Done on the maintenance task once service is complete.",
      ]},
      { title: "Safety checklist before inspection", steps: [
        "Wear safety shoes, gloves and helmet.",
        "Carry a torch, pressure gauge, seal tool, spare seals.",
        "Ensure nearby area is cleared of people.",
        "Switch off electrical supply if working on electrical panels.",
        "Never test a fire alarm without informing the site in advance.",
      ]},
      { title: "Do's and Don'ts", steps: [
        "DO take before-and-after photos for every service.",
        "DO refuse to tamper with an alarm system without written approval.",
        "DO keep the seal and pressure gauge record in the photo.",
        "DON'T skip checklist items even if they look OK — tick every one.",
        "DON'T leave the site without marking the task Done in the app.",
      ]},
      { title: "Emergency handling", steps: [
        "If you discover an active fire hazard — leave the area immediately.",
        "Raise alarm and call local fire brigade (101 in India).",
        "Log incident via Emergency → + Log Incident in the app with severity = critical.",
        "Notify client admin by phone if app is offline.",
      ]},
    ],
    hi: [
      { title: "Technician ka daily workflow", steps: [
        "Phone ya tablet se technician login karein.",
        "Maintenance kholein — sirf aapko assign ki hui tasks dikhengi.",
        "Asset ke paas jaakar QR scan karein ya app me kholein.",
        "Inspection log karein: checklist tick karein, photos daalein, note daalein, sign karein.",
        "Service poori hote hi Mark Done click karein.",
      ]},
      { title: "Inspection se pehle safety checklist", steps: [
        "Safety shoes, gloves aur helmet pehnein.",
        "Torch, pressure gauge, seal tool, spare seals saath rakhein.",
        "Asset ke aas-paas se log ko hata dein.",
        "Electrical panel par kaam karte samay supply band karein.",
        "Fire alarm test karte samay site ko pehle inform karein.",
      ]},
      { title: "Karein aur Na karein", steps: [
        "KAREIN: har service ka pehle aur baad ka photo lein.",
        "KAREIN: likhit approval ke bina alarm system se chhedchhad se mana karein.",
        "KAREIN: seal aur pressure gauge ka record photo me rakhein.",
        "NA KAREIN: checklist me koi bhi item skip na karein — sab tick karein.",
        "NA KAREIN: task Done mark kiye bina site se jaane na niklein.",
      ]},
      { title: "Emergency handling", steps: [
        "Agar active fire hazard mile — turant bahar niklein.",
        "Alarm bajaein aur fire brigade ko 101 par call karein.",
        "App ke Emergency → + Log Incident me critical severity daalein.",
        "App offline ho to client admin ko call karein.",
      ]},
    ],
  },

  qr: {
    en: [
      { title: "Why QR?", steps: [
        "Every asset gets a unique QR. Scanning opens full history — inspections, maintenance, expiry.",
        "Inspectors scan the QR to log results without typing.",
      ]},
      { title: "How to print", steps: [
        "Single QR: Asset detail page → Download QR PDF → print on 2×2 inch sticker.",
        "Bulk: Assets list → select → Print QR Sheet → pick 1 / 10 / 20 per page.",
        "Recommended: A4 sticker paper or Dymo-style label printer. Laminate if installed outdoor.",
      ]},
      { title: "Placement tips", steps: [
        "Stick the QR on the asset at eye level.",
        "Keep away from direct sunlight and moisture if possible.",
        "If damaged, reprint from the same asset — the URL stays the same.",
      ]},
    ],
    hi: [
      { title: "QR kyun?", steps: [
        "Har asset ka ek unique QR banta hai. Scan karte hi history dikh jati hai — inspections, maintenance, expiry.",
        "Inspector QR scan karke bina type kiye inspection log kar sakte hain.",
      ]},
      { title: "Print kaise karein", steps: [
        "Single QR: Asset detail page → Download QR PDF → 2×2 inch sticker par print.",
        "Bulk: Assets list → select → Print QR Sheet → 1 / 10 / 20 per page chunein.",
        "Sifarish: A4 sticker paper ya Dymo label printer. Bahar lagana ho to laminate karein.",
      ]},
      { title: "Lagane ke tips", steps: [
        "Asset par eye level par sticker lagayein.",
        "Dhoop aur paani se bachayein.",
        "Kharaab ho to dobara print karein — URL waise ka waisa rehta hai.",
      ]},
    ],
  },

  faq: {
    en: [
      { q: "I can't log in — what do I do?",
        a: "Check your email (case-insensitive) and password. After 5 wrong tries the account locks for 15 minutes. Contact your SSPL or client admin." },
      { q: "QR scan does nothing when I point my camera.",
        a: "Most modern phones scan QR from the camera app directly. Ensure internet is available. Print must be crisp and not glossy." },
      { q: "My wallet shows ₹0 — everything is blocked.",
        a: "The platform is in read-only mode. Contact your SSPL manager for recharge. Until recharged, you can still view but not create." },
      { q: "How do I download the compliance report?",
        a: "Dashboard → Download Compliance Report (PDF). It includes Fire Safety Score, NOC readiness, expired assets and failed inspections." },
      { q: "Inspection button is missing for me.",
        a: "Inspections can be logged by client_admin, fire_officer, technician and auditor. Ask your admin for the right role." },
      { q: "How often should I inspect extinguishers?",
        a: "Monthly visual check, annual pressure test, 5-yearly refill (IS 2190). The system schedules routine checks as per NFPA-10 / IS standards." },
      { q: "Does QR need internet?",
        a: "Yes — scanning opens the asset page in the app. Offline scan will cache the URL; details appear once connected." },
    ],
    hi: [
      { q: "Login nahi ho raha — kya karun?",
        a: "Email (capital/small se farq nahi) aur password check karein. 5 galat login pe account 15 minute ke liye lock. SSPL ya client admin se sampark karein." },
      { q: "QR scan kuch nahi kar raha.",
        a: "Aaj ke phone direct camera app se QR scan karte hain. Internet chaahiye. Print saaf ho, glossy nahi." },
      { q: "Mera wallet ₹0 hai — sab block.",
        a: "Platform read-only mode me hai. SSPL manager se recharge ke liye sampark karein. Tab tak view kar sakte hain, create nahi." },
      { q: "Compliance report kaise download karun?",
        a: "Dashboard → Download Compliance Report (PDF). Isme Fire Safety Score, NOC readiness, expired assets aur failed inspections milti hain." },
      { q: "Inspection ka button nahi dikh raha.",
        a: "Inspection client_admin, fire_officer, technician aur auditor log kar sakte hain. Admin se sahi role maangein." },
      { q: "Extinguisher kitni baar check karne chahiye?",
        a: "Har mahine visual check, saal me pressure test, 5 saal me refill (IS 2190). System NFPA-10 / IS standards ke hisaab se schedule karta hai." },
      { q: "QR me internet chahiye?",
        a: "Haan — scan karne par asset page app me khulta hai. Offline scan URL yaad rakhta hai; connect hote hi detail dikhti hai." },
    ],
  },

  support: {
    en: [
      { title: "Level-1 Support common issues", steps: [
        "Login / password reset — verify email with client admin; reset password via SSPL admin.",
        "QR scan issue — ensure good lighting and flat sticker; ask user to open asset via app directly.",
        "Wallet exhausted — open SSPL admin → Clients → Recharge; raise GST invoice.",
        "PDF report empty — verify the client has at least one site and one asset.",
      ]},
      { title: "Standard reply scripts", steps: [
        "English (polite close): \"Your issue has been logged with reference ID. Our team will revert within 4 business hours. Thank you for using Fire Compliance OS.\"",
        "Hindi: \"Aapki request reference ID ke saath log kar di gayi hai. Humari team 4 business hours me reply karegi. Dhanyawaad.\"",
      ]},
      { title: "Escalation flow", steps: [
        "Level 1 — Support agent (common issues, password, recharge)",
        "Level 2 — Technical (API errors, data corrections, integration)",
        "Level 3 — SSPL Super Admin (license suspension, kill-switch, legal)",
        "Escalate only after 24 hours or if the user is blocked.",
      ]},
    ],
    hi: [
      { title: "Level-1 common issues", steps: [
        "Login / password reset — client admin se email verify karein; SSPL admin se password reset.",
        "QR scan issue — acchi light aur flat sticker; user ko app se direct asset kholne ko kahein.",
        "Wallet exhausted — SSPL admin → Clients → Recharge; GST invoice bhej dein.",
        "PDF report khali — client ke paas kam se kam ek site aur ek asset hone chahiye.",
      ]},
      { title: "Standard reply scripts", steps: [
        "English: \"Your issue has been logged with reference ID. Our team will revert within 4 business hours. Thank you.\"",
        "Hindi: \"Aapki request reference ID ke saath log kar di gayi hai. Humari team 4 business hours me reply karegi. Dhanyawaad.\"",
      ]},
      { title: "Escalation flow", steps: [
        "Level 1 — Support agent (common issues, password, recharge)",
        "Level 2 — Technical (API errors, data correction, integration)",
        "Level 3 — SSPL Super Admin (license, kill-switch, legal)",
        "24 ghante ke baad ya user block hone par hi escalate karein.",
      ]},
    ],
  },

  terms: {
    en: [
      "Fire Compliance OS is a software tool provided by Securrise Solution Pvt Ltd (SSPL) to help organisations track fire-safety assets, inspections, maintenance and compliance status.",
      "The platform provides recommendations, schedules and risk indicators. Final responsibility for the life-safety of the premises remains with the client organisation, its officers and nominated fire safety personnel.",
      "Compliance scores, NOC readiness, risk levels and AMC suggestions are indicative, generated from the data you input. They are not a substitute for statutory inspection, government NOC, or insurance certification.",
      "Accuracy of reports depends on accurate and timely data entry by the client's team. SSPL is not responsible for losses arising from incorrect or stale data.",
      "Reports, QR labels and audit trails are generated for internal tracking and management review. They may support — but do not replace — official filings required by local Chief Fire Officer, Factory Inspector or insurance carrier.",
      "SSPL owns and operates the platform, its source code, database and licensing. Access may be modified, suspended or revoked at SSPL's discretion in case of non-payment, misuse or regulatory concern.",
      "By continuing to use Fire Compliance OS, you acknowledge that you have read and accept these terms.",
    ],
    hi: [
      "Fire Compliance OS Securrise Solution Pvt Ltd (SSPL) dwara diya gaya software tool hai, jo fire-safety assets, inspections, maintenance aur compliance track karne me madad karta hai.",
      "Platform recommendations, schedules aur risk indicators deta hai. Premises ki life-safety ki antim zimmedari client organisation aur unke nominated fire safety officers par hai.",
      "Compliance scores, NOC readiness, risk levels aur AMC suggestions indicative hain — aapke diye data par based. Yeh statutory inspection, government NOC ya insurance certification ka replacement nahi hain.",
      "Reports ki accuracy aapki team ke data entry par depend karti hai. Galat ya purane data se hone wale nuksan ki SSPL zimmedar nahi hai.",
      "Reports, QR labels aur audit trails internal tracking ke liye hain. Yeh official filings (CFO, Factory Inspector, insurance) ko support karte hain, replace nahi karte.",
      "Platform, source code, database aur licensing SSPL ki property hai. Non-payment, misuse ya regulatory concern me SSPL access modify / suspend / revoke kar sakti hai.",
      "Platform use karke aap in niyamon ko accept karte hain.",
    ],
  },
};
