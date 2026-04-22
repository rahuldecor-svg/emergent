/**
 * Friendly / bilingual error-message translation layer.
 * Maps backend HTTPException detail strings to simple Hindi+English messages.
 */
const MAP = [
  { match: /wallet exhausted/i,
    en: "Wallet balance is zero — the platform is read-only. Please contact SSPL to recharge.",
    hi: "Wallet balance khatam ho gaya hai — abhi sirf read-only mode hai. Kripya SSPL se recharge karein." },
  { match: /insufficient wallet/i,
    en: "Not enough wallet balance for this action. Please recharge first.",
    hi: "Is action ke liye wallet mein paise kam hain. Pehle recharge karein." },
  { match: /invalid credentials/i,
    en: "Wrong email or password. Please try again.",
    hi: "Email ya password galat hai. Phir se try karein." },
  { match: /too many attempts/i,
    en: "Too many attempts — please wait 15 minutes.",
    hi: "Bahut zyada galat login hue — 15 minute ruk kar try karein." },
  { match: /not authenticated/i,
    en: "Please sign in again.",
    hi: "Kripya dobara sign in karein." },
  { match: /session revoked|token expired/i,
    en: "Your session has ended. Please sign in again.",
    hi: "Aapka session khatam ho gaya. Kripya phir se sign in karein." },
  { match: /license suspended/i,
    en: "Your account access is paused by SSPL. Please contact your SSPL manager.",
    hi: "Aapka account SSPL dwara paused hai. Apne SSPL manager se baat karein." },
  { match: /forbidden/i,
    en: "You don't have permission for this action.",
    hi: "Aapko is action ki permission nahi hai." },
  { match: /not found/i,
    en: "We couldn't find that record. Please refresh and try again.",
    hi: "Data nahi mila, please check karein aur phir try karein." },
  { match: /email already/i,
    en: "This email is already registered.",
    hi: "Yeh email pehle se registered hai." },
  { match: /file too large/i,
    en: "File is too large. Maximum 25 MB.",
    hi: "File bahut badi hai. Maximum 25 MB tak upload ho sakta hai." },
];

export function friendly(detail, lang = "en") {
  if (!detail) return lang === "hi" ? "Kuch galat hua. Phir se try karein." : "Something went wrong. Please try again.";
  let text = "";
  if (typeof detail === "string") text = detail;
  else if (Array.isArray(detail)) text = detail.map(d => d?.msg || "").join(" ");
  else if (detail?.message) text = detail.message;
  else text = JSON.stringify(detail);

  for (const row of MAP) {
    if (row.match.test(text)) return row[lang] || row.en;
  }
  return text;
}

export function getLang() {
  return localStorage.getItem("fos_lang") || "en";
}

export function setLang(l) {
  localStorage.setItem("fos_lang", l);
  window.dispatchEvent(new Event("fos-lang"));
}
