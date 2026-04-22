"""SSPL Super Admin routes."""
from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field

from core.db import db
from core.deps import require_role
from core.security import hash_password, new_id, iso, now_utc
from core.notify import log_audit, notify
from core.wallet_service import credit as wallet_credit

router = APIRouter(prefix="/admin", tags=["admin"])


class ClientIn(BaseModel):
    name: str
    industry: Optional[str] = "General"
    gstin: Optional[str] = None
    subscription_plan: str = "basic"
    admin_email: EmailStr
    admin_password: str
    admin_name: str


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    gstin: Optional[str] = None
    subscription_plan: Optional[str] = None
    license_active: Optional[bool] = None
    features: Optional[Dict[str, bool]] = None


class WalletRechargeIn(BaseModel):
    client_id: str
    amount: float = Field(gt=0, description="Must be positive")
    reference: Optional[str] = None
    note: Optional[str] = None


# ---- Clients ----
@router.get("/clients")
async def list_clients(user: dict = Depends(require_role("super_admin"))):
    clients = await db.clients.find({}, {"_id": 0}).to_list(1000)
    for c in clients:
        c["user_count"] = await db.users.count_documents({"client_id": c["id"]})
        c["asset_count"] = await db.assets.count_documents({"client_id": c["id"]})
    return clients


@router.post("/clients")
async def create_client(body: ClientIn, user: dict = Depends(require_role("super_admin"))):
    if await db.users.find_one({"email": body.admin_email.lower()}):
        raise HTTPException(status_code=400, detail="Admin email already in use")
    cid = new_id()
    now = iso(now_utc())
    await db.clients.insert_one({
        "id": cid, "name": body.name, "industry": body.industry or "General",
        "gstin": body.gstin, "subscription_plan": body.subscription_plan,
        "license_active": True, "wallet_balance": 0.0,
        "features": {"emergency": True, "risk_map": True, "amc_engine": True, "noc": True},
        "created_at": now,
    })
    await db.users.insert_one({
        "id": new_id(), "email": body.admin_email.lower(),
        "password_hash": hash_password(body.admin_password),
        "name": body.admin_name, "role": "client_admin",
        "client_id": cid, "site_ids": [], "created_at": now,
    })
    await log_audit(user, "client.create", cid, {"name": body.name})
    return {"ok": True, "client_id": cid}


@router.patch("/clients/{cid}")
async def update_client(cid: str, body: ClientUpdate, user: dict = Depends(require_role("super_admin"))):
    upd = {k: v for k, v in body.model_dump().items() if v is not None}
    if not upd:
        return {"ok": True}
    await db.clients.update_one({"id": cid}, {"$set": upd})
    await log_audit(user, "client.update", cid, upd)
    return {"ok": True}


@router.post("/clients/{cid}/kill-switch")
async def kill_switch(cid: str, user: dict = Depends(require_role("super_admin"))):
    c = await db.clients.find_one({"id": cid})
    if not c:
        raise HTTPException(404, "Not found")
    new_state = not c.get("license_active", True)
    await db.clients.update_one({"id": cid}, {"$set": {"license_active": new_state}})
    await log_audit(user, "client.kill_switch", cid, {"license_active": new_state})
    return {"license_active": new_state}


# ---- Overview (Revenue Dashboard) ----
@router.get("/overview")
async def admin_overview(user: dict = Depends(require_role("super_admin"))):
    from core.config import WALLET_LOW_THRESHOLD
    total_clients = await db.clients.count_documents({})
    active_clients = await db.clients.count_documents({"license_active": True})
    total_assets = await db.assets.count_documents({})
    total_users = await db.users.count_documents({})
    clients = await db.clients.find({}, {"_id": 0}).to_list(1000)
    total_wallet = sum(float(c.get("wallet_balance", 0) or 0) for c in clients)

    # Revenue: sum of all credit transactions (GST-inclusive)
    credit_pipeline = [
        {"$match": {"type": "credit"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}, "count": {"$sum": 1}}},
    ]
    credit_agg = await db.wallet_transactions.aggregate(credit_pipeline).to_list(1)
    total_revenue = float(credit_agg[0]["total"]) if credit_agg else 0.0
    total_credit_tx = int(credit_agg[0]["count"]) if credit_agg else 0

    # Usage: total spend
    usage_pipeline = [
        {"$match": {"type": "usage"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}, "count": {"$sum": 1}}},
    ]
    usage_agg = await db.wallet_transactions.aggregate(usage_pipeline).to_list(1)
    total_usage = float(usage_agg[0]["total"]) if usage_agg else 0.0
    total_usage_tx = int(usage_agg[0]["count"]) if usage_agg else 0

    total_transactions = await db.wallet_transactions.count_documents({})

    low_balance = [c for c in clients if float(c.get("wallet_balance", 0) or 0) < WALLET_LOW_THRESHOLD]
    wallets_by_client = [{
        "id": c["id"], "name": c["name"],
        "balance": float(c.get("wallet_balance", 0) or 0),
        "plan": c.get("subscription_plan"),
        "license_active": c.get("license_active", True),
    } for c in clients]
    wallets_by_client.sort(key=lambda x: x["balance"])

    risk = []
    today = iso(now_utc())[:10]
    for c in clients:
        expired = await db.assets.count_documents({"client_id": c["id"], "expiry_date": {"$lt": today}})
        missed = await db.maintenance_tasks.count_documents({"client_id": c["id"], "status": "missed"})
        score = max(0, 100 - expired * 10 - missed * 3)
        risk.append({"client_id": c["id"], "name": c["name"], "score": score,
                     "expired_assets": expired, "missed_maintenance": missed,
                     "wallet_balance": float(c.get("wallet_balance", 0) or 0),
                     "subscription_plan": c.get("subscription_plan"),
                     "license_active": c.get("license_active", True)})
    risk.sort(key=lambda x: x["score"])

    recent_tx = await db.wallet_transactions.find({}, {"_id": 0}).sort("created_at", -1).to_list(10)
    # enrich recent_tx with client name
    by_id = {c["id"]: c["name"] for c in clients}
    for t in recent_tx:
        t["client_name"] = by_id.get(t.get("client_id"), "—")

    return {
        "total_clients": total_clients, "active_clients": active_clients,
        "total_assets": total_assets, "total_users": total_users,
        "total_wallet_balance": total_wallet,
        "total_revenue": total_revenue,
        "total_usage": abs(total_usage),
        "total_transactions": total_transactions,
        "total_credit_transactions": total_credit_tx,
        "total_usage_transactions": total_usage_tx,
        "low_balance_clients": [{"id": c["id"], "name": c["name"],
                                 "balance": float(c.get("wallet_balance", 0) or 0)} for c in low_balance],
        "wallets_by_client": wallets_by_client,
        "recent_transactions": recent_tx,
        "clients_risk": risk,
    }


# ---- Wallet Recharge ----
@router.post("/wallet/recharge")
async def wallet_recharge(body: WalletRechargeIn, user: dict = Depends(require_role("super_admin"))):
    # Compute invoice number (unique, 4-hex suffix on collision)
    base_inv = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    inv_no = base_inv
    while await db.wallet_transactions.find_one({"gst_invoice_no": inv_no}):
        inv_no = f"{base_inv}-{new_id()[:4].upper()}"
    gst_amount = round(body.amount * 0.18 / 1.18, 2)

    result = await wallet_credit(
        client_id=body.client_id, amount=body.amount,
        reference=body.reference or "Manual",
        note=body.note or "", gst_invoice_no=inv_no, gst_amount=gst_amount,
    )
    await log_audit(user, "wallet.recharge", body.client_id,
                    {"amount": body.amount, "invoice_no": inv_no})
    # Notify client admins
    admins = await db.users.find({"client_id": body.client_id, "role": "client_admin"},
                                 {"_id": 0, "id": 1}).to_list(50)
    await notify([u["id"] for u in admins], "wallet",
                 "Wallet recharged",
                 f"₹{body.amount} credited. New balance ₹{result['balance']}. Invoice {inv_no}.")
    return {"balance": result["balance"], "invoice_no": inv_no, "gst_amount": gst_amount}


# ---- Audit log ----
@router.get("/audit")
async def audit_logs(user: dict = Depends(require_role("super_admin"))):
    return await db.audit_logs.find({}, {"_id": 0}).sort("created_at", -1).to_list(500)
