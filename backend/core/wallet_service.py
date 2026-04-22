"""Usage-based wallet deduction. Logs transactions, enforces grace-mode."""
from fastapi import HTTPException
from typing import Optional

from .db import db
from .security import new_id, iso, now_utc
from .config import WALLET_LOW_THRESHOLD
from .emailer import send_email, tpl_low_balance, tpl_wallet_exhausted


async def _notify_and_email_client_admins(client_id: str, kind: str,
                                          in_app_title: str, in_app_body: str,
                                          email_subject: str, email_html: str):
    admins = await db.users.find(
        {"client_id": client_id, "role": {"$in": ["client_admin", "fire_officer"]}},
        {"_id": 0, "id": 1, "email": 1}
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


async def charge(client_id: str, cost: float, reason: str, reference: Optional[str] = None) -> dict:
    """Deduct `cost` from client wallet. Raises 402 if balance <= 0 AND cost > 0.

    Returns updated client snapshot + transaction record.
    """
    if not client_id:
        raise HTTPException(400, "Missing tenant")
    client = await db.clients.find_one({"id": client_id}, {"_id": 0})
    if not client:
        raise HTTPException(404, "Client not found")

    balance = float(client.get("wallet_balance", 0) or 0)

    # Hard restriction: balance ≤ 0 — block any paid action (grace mode = read-only)
    if cost > 0 and balance <= 0:
        raise HTTPException(
            status_code=402,
            detail=f"Wallet exhausted (₹{balance:.2f}). Platform is in read-only mode — "
                   "contact SSPL to recharge before creating new {}.".format(reason.lower()),
        )

    new_balance = round(balance - cost, 2)
    await db.clients.update_one({"id": client_id}, {"$set": {"wallet_balance": new_balance}})

    tx = {
        "id": new_id(), "client_id": client_id, "type": "usage",
        "amount": -cost, "balance_after": new_balance,
        "reason": reason, "reference": reference,
        "gst_invoice_no": None, "gst_amount": 0,
        "created_at": iso(now_utc()),
    }
    await db.wallet_transactions.insert_one(tx)
    tx.pop("_id", None)

    # Notify on transitions
    if new_balance <= 0 and balance > 0:
        sub, html = tpl_wallet_exhausted(client.get("name", ""))
        await _notify_and_email_client_admins(
            client_id, "wallet_exhausted",
            "Wallet exhausted — read-only mode",
            f"{client.get('name','')} wallet is now ₹{new_balance:.2f}. Platform actions are blocked until SSPL recharges.",
            sub, html,
        )
    elif new_balance < WALLET_LOW_THRESHOLD and balance >= WALLET_LOW_THRESHOLD:
        sub, html = tpl_low_balance(client.get("name", ""), new_balance, WALLET_LOW_THRESHOLD)
        await _notify_and_email_client_admins(
            client_id, "wallet_low",
            "Low wallet balance",
            f"Balance dropped to ₹{new_balance:.2f} (threshold ₹{int(WALLET_LOW_THRESHOLD)}).",
            sub, html,
        )

    return {"balance": new_balance, "transaction": tx, "client": client.get("name", "")}


async def credit(client_id: str, amount: float, reference: str, note: str,
                 gst_invoice_no: str, gst_amount: float) -> dict:
    client = await db.clients.find_one({"id": client_id}, {"_id": 0})
    if not client:
        raise HTTPException(404, "Client not found")
    new_balance = round(float(client.get("wallet_balance", 0) or 0) + amount, 2)
    await db.clients.update_one({"id": client_id}, {"$set": {"wallet_balance": new_balance}})
    tx = {
        "id": new_id(), "client_id": client_id, "type": "credit",
        "amount": amount, "balance_after": new_balance,
        "reference": reference, "note": note,
        "gst_invoice_no": gst_invoice_no, "gst_amount": gst_amount,
        "created_at": iso(now_utc()),
    }
    await db.wallet_transactions.insert_one(tx)
    return {"balance": new_balance, "invoice_no": gst_invoice_no}
