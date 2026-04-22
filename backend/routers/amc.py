"""AMC Conversion — Book Service endpoint."""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from core.db import db
from core.deps import get_current_user, tenant_filter
from core.security import new_id, iso, now_utc
from core.notify import log_audit, notify

router = APIRouter(prefix="/amc", tags=["amc"])


class BookServiceIn(BaseModel):
    asset_id: str
    technician_id: Optional[str] = None
    scheduled_date: Optional[str] = None  # YYYY-MM-DD; default tomorrow
    auto_assign: bool = True


PRICE_TABLE = {"extinguisher": 450, "hydrant": 1200, "sprinkler": 800,
               "alarm": 350, "hose": 600}


def suggested_price(category: str) -> int:
    return PRICE_TABLE.get(category, 500)


@router.post("/book-service")
async def book_service(body: BookServiceIn, user: dict = Depends(get_current_user)):
    if user["role"] not in ("super_admin", "client_admin", "fire_officer"):
        raise HTTPException(403, "Forbidden")

    q = await tenant_filter(user)
    asset = await db.assets.find_one({"id": body.asset_id, **q}, {"_id": 0})
    if not asset:
        raise HTTPException(404, "Asset not found")

    # Price + GST
    price = float(suggested_price(asset["category"]))
    gst_amount = round(price * 0.18 / 1.18, 2)

    # Wallet check (for client tenants only — super_admin bypasses)
    if user["role"] != "super_admin":
        client = await db.clients.find_one({"id": user["client_id"]}, {"_id": 0})
        balance = float((client or {}).get("wallet_balance", 0) or 0)
        if balance < price:
            shortfall = round(price - balance, 2)
            raise HTTPException(
                status_code=402,
                detail={
                    "message": "Insufficient wallet balance to book this service.",
                    "current_balance": balance,
                    "required_balance": price,
                    "shortfall": shortfall,
                    "asset_id": body.asset_id,
                    "asset_name": asset["name"],
                },
            )

    # Auto-assign technician if not provided
    tech_id = body.technician_id
    if not tech_id and body.auto_assign and user["role"] != "super_admin":
        tech = await db.users.find_one(
            {"client_id": user["client_id"], "role": "technician"},
            {"_id": 0, "id": 1},
        )
        if tech:
            tech_id = tech["id"]

    scheduled = body.scheduled_date or iso(now_utc() + timedelta(days=1))[:10]

    # Generate pro-forma invoice
    base_inv = f"PRO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    inv_no = base_inv
    while await db.wallet_transactions.find_one({"gst_invoice_no": inv_no}):
        inv_no = f"{base_inv}-{new_id()[:4].upper()}"

    # Create maintenance task
    task = {
        "id": new_id(),
        "client_id": asset["client_id"],
        "asset_id": body.asset_id,
        "scheduled_date": scheduled,
        "technician_id": tech_id,
        "status": "scheduled",
        "notes": f"AMC booked · {asset['name']} · {asset['category']}",
        "source": "amc_conversion",
        "invoice_no": inv_no,
        "price": price,
        "gst_amount": gst_amount,
        "created_at": iso(now_utc()),
    }
    await db.maintenance_tasks.insert_one(task)
    task.pop("_id", None)

    # Debit wallet (skip for super_admin)
    tx = None
    new_balance = None
    if user["role"] != "super_admin":
        client = await db.clients.find_one({"id": user["client_id"]}, {"_id": 0})
        new_balance = round(float(client.get("wallet_balance", 0) or 0) - price, 2)
        await db.clients.update_one({"id": user["client_id"]}, {"$set": {"wallet_balance": new_balance}})
        tx = {
            "id": new_id(), "client_id": user["client_id"],
            "type": "amc_service", "amount": -price, "balance_after": new_balance,
            "reason": f"AMC Service · {asset['name']}", "reference": task["id"],
            "gst_invoice_no": inv_no, "gst_amount": gst_amount,
            "created_at": iso(now_utc()),
        }
        await db.wallet_transactions.insert_one(tx)
        tx.pop("_id", None)

    # Notify technician + admins
    notify_users = []
    if tech_id:
        notify_users.append(tech_id)
    admins = await db.users.find(
        {"client_id": asset["client_id"], "role": {"$in": ["client_admin", "fire_officer"]}},
        {"_id": 0, "id": 1},
    ).to_list(20)
    notify_users += [a["id"] for a in admins]
    if notify_users:
        await notify(
            list(set(notify_users)),
            "amc_booked",
            f"Service booked · {asset['name']}",
            f"Scheduled {scheduled} · ₹{price} (GST ₹{gst_amount}) · Invoice {inv_no}",
            meta={"task_id": task["id"], "asset_id": body.asset_id, "invoice_no": inv_no},
            severity="info",
        )

    await log_audit(user, "amc.book_service", task["id"], {
        "asset_id": body.asset_id, "invoice_no": inv_no, "price": price,
    })

    return {
        "ok": True,
        "task": task,
        "invoice_no": inv_no,
        "price": price,
        "gst_amount": gst_amount,
        "wallet": {"balance_after": new_balance, "transaction_id": (tx or {}).get("id")} if tx else None,
    }
