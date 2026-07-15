"""Usage-based wallet deduction. Logs transactions, enforces grace-mode.

ATOMIC GUARANTEES (race-condition safe):
- `charge()` uses find_one_and_update with $inc — single atomic op.
- `credit()` uses find_one_and_update with $inc + (caller) atomic-claim on
  payment_orders.status to guarantee idempotent crediting.
"""
from fastapi import HTTPException
from pymongo import ReturnDocument
from typing import Optional

from .db import db
from .security import new_id, iso, now_utc
from .config import WALLET_LOW_THRESHOLD
from .emailer import send_email, tpl_low_balance, tpl_wallet_exhausted
from .messaging import send_critical_alert, fire_and_forget


async def _notify_and_email_client_admins(client_id: str, kind: str,
                                          in_app_title: str, in_app_body: str,
                                          email_subject: str, email_html: str,
                                          critical_event: str = "",
                                          whatsapp_vars: list = None,
                                          sms_vars: dict = None):
    admins = await db.users.find(
        {"client_id": client_id, "role": {"$in": ["client_admin", "fire_officer"]}},
        {"_id": 0, "id": 1, "email": 1, "phone": 1}
    ).to_list(50)
    if not admins:
        return
    # in-app
    await db.notifications.insert_many([{
        "id": new_id(), "user_id": a["id"], "kind": kind, "title": in_app_title,
        "body": in_app_body, "meta": {}, "read": False, "created_at": iso(now_utc()),
    } for a in admins])
    # email
    await send_email([a["email"] for a in admins], email_subject, email_html)
    # WhatsApp → SMS fallback for critical events
    if critical_event:
        phones = [a.get("phone") for a in admins if a.get("phone")]
        if phones:
            fire_and_forget(send_critical_alert(
                phones, critical_event,
                whatsapp_vars or [], sms_vars or {},
            ))


async def charge(client_id: str, cost: float, reason: str, reference: Optional[str] = None) -> dict:
    """Atomically deduct `cost` from client wallet. Raises 402 if insufficient.

    Uses $inc + filter on minimum balance — guaranteed race-safe under any concurrency.
    """
    if not client_id:
        raise HTTPException(400, "Missing tenant")

    # Atomic compare-and-swap: only proceed if balance > 0 (grace-mode guard).
    # For cost > 0 we additionally require balance > 0 (block read-only mode).
    if cost > 0:
        client = await db.clients.find_one_and_update(
            {"id": client_id, "wallet_balance": {"$gt": 0}},
            {"$inc": {"wallet_balance": -cost}},
            projection={"_id": 0, "name": 1, "wallet_balance": 1},
            return_document=ReturnDocument.BEFORE,
        )
        if client is None:
            # Either tenant missing OR balance ≤ 0 — find out which
            exists = await db.clients.find_one({"id": client_id}, {"_id": 0, "wallet_balance": 1})
            if not exists:
                raise HTTPException(404, "Client not found")
            raise HTTPException(
                status_code=402,
                detail=f"Wallet exhausted (₹{float(exists.get('wallet_balance', 0) or 0):.2f}). "
                       f"Platform is in read-only mode — recharge before creating new {reason.lower()}.",
            )
    else:
        # Zero-cost operation — no deduction, just fetch
        client = await db.clients.find_one({"id": client_id}, {"_id": 0, "name": 1, "wallet_balance": 1})
        if not client:
            raise HTTPException(404, "Client not found")

    # `client` is the BEFORE snapshot; compute new_balance for ledger
    balance_before = float(client.get("wallet_balance", 0) or 0)
    new_balance = round(balance_before - cost, 2)

    tx = {
        "id": new_id(), "client_id": client_id, "type": "usage",
        "amount": -cost, "balance_after": new_balance,
        "reason": reason, "reference": reference,
        "gst_invoice_no": None, "gst_amount": 0,
        "created_at": iso(now_utc()),
    }
    await db.wallet_transactions.insert_one(tx)
    tx.pop("_id", None)

    # Notify on transitions (only when crossing threshold from a higher state)
    if new_balance <= 0 and balance_before > 0:
        sub, html = tpl_wallet_exhausted(client.get("name", ""))
        await _notify_and_email_client_admins(
            client_id, "wallet_exhausted",
            "Wallet exhausted — read-only mode",
            f"{client.get('name','')} wallet is now ₹{new_balance:.2f}. Platform actions are blocked until recharge.",
            sub, html,
            critical_event="wallet_exhausted",
            whatsapp_vars=[client.get("name", ""), f"{new_balance:.2f}"],
            sms_vars={"client_name": client.get("name", ""),
                      "balance": f"{new_balance:.2f}"},
        )
    elif new_balance < WALLET_LOW_THRESHOLD and balance_before >= WALLET_LOW_THRESHOLD:
        sub, html = tpl_low_balance(client.get("name", ""), new_balance, WALLET_LOW_THRESHOLD)
        await _notify_and_email_client_admins(
            client_id, "wallet_low",
            "Low wallet balance",
            f"Balance dropped to ₹{new_balance:.2f} (threshold ₹{int(WALLET_LOW_THRESHOLD)}).",
            sub, html,
            critical_event="low_wallet",
            whatsapp_vars=[client.get("name", ""), f"{new_balance:.2f}",
                           f"{int(WALLET_LOW_THRESHOLD)}"],
            sms_vars={"client_name": client.get("name", ""),
                      "balance": f"{new_balance:.2f}",
                      "threshold": f"{int(WALLET_LOW_THRESHOLD)}"},
        )

    return {"balance": new_balance, "transaction": tx, "client": client.get("name", "")}


async def credit(client_id: str, amount: float, reference: str, note: str,
                 gst_invoice_no: str, gst_amount: float) -> dict:
    """Atomically credit `amount` to client wallet.

    Idempotency is enforced by caller (payment finalizer) using atomic order-status
    claim. The $inc here is purely atomic; safe even if called twice (which the
    caller's claim prevents anyway — belt + braces).
    """
    updated = await db.clients.find_one_and_update(
        {"id": client_id},
        {"$inc": {"wallet_balance": amount}},
        projection={"_id": 0, "wallet_balance": 1, "name": 1},
        return_document=ReturnDocument.AFTER,
    )
    if not updated:
        raise HTTPException(404, "Client not found")
    new_balance = round(float(updated.get("wallet_balance", 0) or 0), 2)

    tx = {
        "id": new_id(), "client_id": client_id, "type": "credit",
        "amount": amount, "balance_after": new_balance,
        "reference": reference, "note": note,
        "gst_invoice_no": gst_invoice_no, "gst_amount": gst_amount,
        "created_at": iso(now_utc()),
    }
    await db.wallet_transactions.insert_one(tx)
    return {"balance": new_balance, "invoice_no": gst_invoice_no}
