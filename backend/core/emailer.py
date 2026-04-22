"""Resend email wrapper with log-only fallback when RESEND_API_KEY is empty."""
import asyncio
import logging
from typing import List

import resend

from .config import RESEND_API_KEY, EMAIL_FROM

log = logging.getLogger("email")

if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY


async def send_email(to: List[str], subject: str, html: str) -> bool:
    """Send email via Resend. If key missing or send fails, log the email and return False."""
    if not to:
        return False
    if not RESEND_API_KEY:
        log.info("[EMAIL:log-only] to=%s subject=%r", to, subject)
        log.debug("[EMAIL:log-only] body=%s", html[:2000])
        return False
    try:
        params = {"from": EMAIL_FROM, "to": to, "subject": subject, "html": html}
        result = await asyncio.to_thread(resend.Emails.send, params)
        log.info("[EMAIL:sent] to=%s subject=%r id=%s", to, subject, (result or {}).get("id"))
        return True
    except Exception as e:
        log.error("[EMAIL:failed] to=%s subject=%r err=%s", to, subject, e)
        return False


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
      <p>New actions may be restricted at ₹0. Please contact SSPL to recharge.</p>
    </div>"""
    return subject, html


def tpl_wallet_exhausted(client_name: str) -> tuple[str, str]:
    subject = "[Fire OS] Wallet exhausted — read-only mode"
    html = f"""
    <div style="font-family:sans-serif;max-width:560px">
      <h2 style="color:#b91c1c;margin:0">Wallet Exhausted</h2>
      <p><b>{client_name}</b> has a zero or negative wallet balance. The platform is now
      in read-only mode; asset creation, inspections and user additions are blocked
      until SSPL credits the wallet.</p>
    </div>"""
    return subject, html
