"""Email sender with layered fallback:
  1. Resend API (if RESEND_API_KEY set) → primary
  2. SMTP (if SMTP_HOST set) → automatic fallback on Resend failure or missing key
  3. Log-only → last resort, never blocks caller

Every send is recorded in db.email_log for audit/tracking.
"""
import asyncio
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr, formataddr
from typing import List, Optional

import resend

from .config import (
    RESEND_API_KEY, EMAIL_FROM,
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_USE_TLS,
)
from .db import db
from .security import new_id, iso, now_utc

log = logging.getLogger("email")

if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY


def _parse_from(email_from: str) -> tuple[str, str]:
    """`Fire OS <x@y.com>` → ('Fire OS', 'x@y.com')."""
    name, addr = parseaddr(email_from)
    return name, addr


def _send_via_smtp_sync(to: List[str], subject: str, html: str) -> tuple[bool, Optional[str]]:
    """Blocking SMTP send. Returns (ok, provider_message_id_or_error)."""
    if not SMTP_HOST:
        return False, "smtp_not_configured"
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = EMAIL_FROM
        msg["To"] = ", ".join(to)
        msg.attach(MIMEText(html, "html", "utf-8"))
        if SMTP_USE_TLS:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as s:
                s.ehlo()
                s.starttls()
                if SMTP_USER and SMTP_PASSWORD:
                    s.login(SMTP_USER, SMTP_PASSWORD)
                s.sendmail(_parse_from(EMAIL_FROM)[1], to, msg.as_string())
        else:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=20) as s:
                if SMTP_USER and SMTP_PASSWORD:
                    s.login(SMTP_USER, SMTP_PASSWORD)
                s.sendmail(_parse_from(EMAIL_FROM)[1], to, msg.as_string())
        return True, "smtp_ok"
    except Exception as e:
        return False, f"smtp_error:{e}"


def _send_via_resend_sync(to: List[str], subject: str, html: str) -> tuple[bool, Optional[str]]:
    if not RESEND_API_KEY:
        return False, "resend_no_key"
    try:
        params = {"from": EMAIL_FROM, "to": to, "subject": subject, "html": html}
        result = resend.Emails.send(params)
        return True, (result or {}).get("id") or "resend_ok"
    except Exception as e:
        return False, f"resend_error:{e}"


async def send_email(to: List[str], subject: str, html: str) -> bool:
    """Try Resend first, fall back to SMTP, else log. Always records attempt."""
    if not to:
        return False

    provider = None
    provider_id = None
    ok = False

    # 1. Resend
    if RESEND_API_KEY:
        ok, provider_id = await asyncio.to_thread(_send_via_resend_sync, to, subject, html)
        provider = "resend"
        if ok:
            log.info("[EMAIL:resend] to=%s subj=%r id=%s", to, subject, provider_id)

    # 2. SMTP fallback
    if not ok and SMTP_HOST:
        ok, provider_id = await asyncio.to_thread(_send_via_smtp_sync, to, subject, html)
        provider = "smtp"
        if ok:
            log.info("[EMAIL:smtp] to=%s subj=%r", to, subject)

    # 3. Log-only
    if not ok:
        provider = provider or "log_only"
        provider_id = provider_id or "no_provider_configured"
        log.info("[EMAIL:log-only] to=%s subj=%r (%s)", to, subject, provider_id)

    try:
        await db.email_log.insert_one({
            "id": new_id(), "to": to, "subject": subject,
            "provider": provider, "provider_id": provider_id,
            "success": ok, "created_at": iso(now_utc()),
        })
    except Exception as e:
        log.warning("Failed to write email_log: %s", e)

    return ok


# ---- Pre-built templates ----
def tpl_inspection_fail(asset_name: str, inspector: str, notes: str = "") -> tuple[str, str]:
    subject = f"[Fire OS] Inspection FAILED — {asset_name}"
    html = f"""
    <div style="font-family:sans-serif;max-width:560px">
      <h2 style="color:#b91c1c;margin:0">Inspection Failed</h2>
      <p>Asset <b>{asset_name}</b> failed inspection by <b>{inspector}</b>.</p>
      <p><i>{notes or ''}</i></p>
      <p style="color:#555;font-size:13px">Please review in the Fire Compliance OS dashboard.</p>
    </div>"""
    return subject, html


def tpl_maintenance_due(asset_name: str, due_date: str) -> tuple[str, str]:
    subject = f"[Fire OS] Maintenance due — {asset_name}"
    html = f"""
    <div style="font-family:sans-serif;max-width:560px">
      <h2 style="margin:0">Maintenance Due</h2>
      <p>Scheduled maintenance for <b>{asset_name}</b> is due on <b>{due_date}</b>.</p>
    </div>"""
    return subject, html


def tpl_low_balance(client_name: str, balance: float, threshold: float) -> tuple[str, str]:
    subject = "[Fire OS] Low wallet balance"
    html = f"""
    <div style="font-family:sans-serif;max-width:560px">
      <h2 style="color:#d97706;margin:0">Low Wallet Balance</h2>
      <p><b>{client_name}</b> wallet balance is ₹{balance:.2f} (threshold ₹{threshold:.0f}).</p>
      <p>New actions may be restricted at ₹0. Please top up from your Wallet page.</p>
    </div>"""
    return subject, html


def tpl_wallet_exhausted(client_name: str) -> tuple[str, str]:
    subject = "[Fire OS] Wallet exhausted — read-only mode"
    html = f"""
    <div style="font-family:sans-serif;max-width:560px">
      <h2 style="color:#b91c1c;margin:0">Wallet Exhausted</h2>
      <p><b>{client_name}</b> has a zero or negative wallet balance. The platform is now
      in read-only mode; asset creation, inspections and user additions are blocked
      until the wallet is topped up.</p>
    </div>"""
    return subject, html


def tpl_password_reset(name: str, reset_url: str, ttl_hours: int) -> tuple[str, str]:
    subject = "[Fire OS] Password reset instructions"
    html = f"""
    <div style="font-family:sans-serif;max-width:560px">
      <h2 style="margin:0">Password Reset</h2>
      <p>Hi {name or 'there'},</p>
      <p>We received a request to reset your Fire Compliance OS password.
         Click the button below to choose a new one.</p>
      <p style="margin:24px 0">
        <a href="{reset_url}" style="background:#111827;color:#fff;padding:12px 24px;
          text-decoration:none;border-radius:4px;font-weight:bold">Reset Password</a>
      </p>
      <p style="color:#6b7280;font-size:13px">
        This link expires in {ttl_hours} hour(s). If you didn't request this, ignore this email —
        your password will remain unchanged.
      </p>
      <p style="color:#6b7280;font-size:12px;word-break:break-all">{reset_url}</p>
    </div>"""
    return subject, html
