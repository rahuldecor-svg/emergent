"""WhatsApp (Meta Cloud API) + SMS (MSG91) with graceful fallback.

Flow:
  1. Send WhatsApp template message via Meta Cloud API (if configured).
  2. If WhatsApp fails OR not configured → send SMS via MSG91 (if configured).
  3. Always record attempt in db.messaging_log. Never raises to caller.

Phone numbers must be E.164 with country code, e.g. +919876543210.
"""
import asyncio
import logging
import re
from typing import List, Optional

import httpx

from .config import (
    WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_ACCESS_TOKEN, WHATSAPP_API_VERSION,
    WHATSAPP_TPLS, WHATSAPP_TPL_LANG,
    MSG91_AUTHKEY, MSG91_SENDER_ID, MSG91_TPLS,
)
from .db import db
from .security import new_id, iso, now_utc

log = logging.getLogger("messaging")

_E164 = re.compile(r"^\+\d{10,15}$")


def _norm(p: str) -> Optional[str]:
    """Accept '+91…' or '91…' or '9876543210' → returns '+91XXXXXXXXXX' for 10-digit India."""
    if not p:
        return None
    p = p.strip().replace(" ", "").replace("-", "")
    if p.startswith("+"):
        return p if _E164.match(p) else None
    if len(p) == 10 and p.isdigit():
        return f"+91{p}"
    if len(p) == 12 and p.isdigit() and p.startswith("91"):
        return f"+{p}"
    return None


async def _log(kind: str, to: str, event: str, provider: str,
               ok: bool, detail: str, notification_id: Optional[str] = None):
    try:
        await db.messaging_log.insert_one({
            "id": new_id(), "kind": kind, "to": to, "event": event,
            "provider": provider, "success": ok, "detail": detail[:1000],
            "notification_id": notification_id,
            "created_at": iso(now_utc()),
        })
    except Exception as e:
        log.warning("messaging_log write failed: %s", e)


async def _send_whatsapp(phone: str, event: str, variables: List[str]) -> tuple[bool, str]:
    if not (WHATSAPP_PHONE_NUMBER_ID and WHATSAPP_ACCESS_TOKEN):
        return False, "whatsapp_not_configured"
    tpl_name = WHATSAPP_TPLS.get(event, "")
    if not tpl_name:
        return False, f"whatsapp_no_template:{event}"
    url = (
        f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/"
        f"{WHATSAPP_PHONE_NUMBER_ID}/messages"
    )
    payload: dict = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone.lstrip("+"),
        "type": "template",
        "template": {
            "name": tpl_name,
            "language": {"code": WHATSAPP_TPL_LANG},
        },
    }
    if variables:
        payload["template"]["components"] = [{
            "type": "body",
            "parameters": [{"type": "text", "text": str(v)} for v in variables],
        }]
    try:
        async with httpx.AsyncClient(timeout=15.0) as c:
            r = await c.post(
                url, json=payload,
                headers={"Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}"},
            )
        if 200 <= r.status_code < 300:
            mid = (r.json().get("messages") or [{}])[0].get("id", "sent")
            return True, f"whatsapp_ok:{mid}"
        return False, f"whatsapp_http_{r.status_code}:{r.text[:300]}"
    except Exception as e:
        return False, f"whatsapp_error:{e}"


async def _send_sms(phone: str, event: str, variables: dict) -> tuple[bool, str]:
    if not MSG91_AUTHKEY:
        return False, "msg91_not_configured"
    tpl_id = MSG91_TPLS.get(event, "")
    if not tpl_id:
        return False, f"msg91_no_template:{event}"
    # MSG91 Flow API (v5)
    url = "https://control.msg91.com/api/v5/flow/"
    recipients = [{"mobiles": phone.lstrip("+"), **variables}]
    payload = {"template_id": tpl_id, "recipients": recipients}
    if MSG91_SENDER_ID:
        payload["sender"] = MSG91_SENDER_ID
    try:
        async with httpx.AsyncClient(timeout=15.0) as c:
            r = await c.post(
                url, json=payload,
                headers={
                    "authkey": MSG91_AUTHKEY,
                    "Content-Type": "application/json",
                    "accept": "application/json",
                },
            )
        if 200 <= r.status_code < 300:
            return True, f"msg91_ok:{r.text[:200]}"
        return False, f"msg91_http_{r.status_code}:{r.text[:300]}"
    except Exception as e:
        return False, f"msg91_error:{e}"


async def send_critical_alert(
    phones: List[str], event: str,
    variables_list: List[str], variables_map: dict,
    notification_id: Optional[str] = None,
) -> dict:
    """Send critical alert: WhatsApp first → SMS fallback. Never raises.

    `variables_list`: ordered values for WhatsApp template body parameters.
    `variables_map`: field->value map for MSG91 template (DLT placeholders).
    """
    results = {"whatsapp": [], "sms": [], "skipped": []}
    if not phones:
        return results
    for raw in phones:
        phone = _norm(raw)
        if not phone:
            results["skipped"].append({"raw": raw, "reason": "invalid_phone"})
            continue

        ok, detail = await _send_whatsapp(phone, event, variables_list)
        await _log("whatsapp", phone, event, "meta", ok, detail, notification_id)
        if ok:
            results["whatsapp"].append({"phone": phone, "detail": detail})
            continue

        ok2, detail2 = await _send_sms(phone, event, variables_map)
        await _log("sms", phone, event, "msg91", ok2, detail2, notification_id)
        if ok2:
            results["sms"].append({"phone": phone, "detail": detail2,
                                   "whatsapp_err": detail})
        else:
            results["skipped"].append({"phone": phone,
                                       "whatsapp_err": detail,
                                       "sms_err": detail2})
    return results


def fire_and_forget(coro):
    """Schedule alert as a background task (non-blocking caller)."""
    try:
        asyncio.get_running_loop().create_task(coro)
    except RuntimeError:
        asyncio.run(coro)
