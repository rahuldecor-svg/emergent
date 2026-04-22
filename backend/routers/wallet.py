"""Client-facing wallet (balance + transactions + pricing transparency)."""
from fastapi import APIRouter, Depends
from core.db import db
from core.deps import get_current_user
from core.config import (
    COST_PER_ASSET, COST_PER_INSPECTION, COST_PER_USER, WALLET_LOW_THRESHOLD,
)

router = APIRouter(prefix="/wallet", tags=["wallet"])


@router.get("")
async def get_wallet(user: dict = Depends(get_current_user)):
    pricing = {
        "per_asset": COST_PER_ASSET,
        "per_inspection": COST_PER_INSPECTION,
        "per_user": COST_PER_USER,
        "low_threshold": WALLET_LOW_THRESHOLD,
    }
    if user["role"] == "super_admin":
        # Backward-compat: super_admin wallet returns 0 (tenant concept doesn't apply).
        # Aggregate revenue/usage data is available on /api/admin/overview.
        return {"balance": 0, "subscription_plan": None,
                "transactions": [], "pricing": pricing}

    client = await db.clients.find_one({"id": user["client_id"]}, {"_id": 0})
    tx = await db.wallet_transactions.find(
        {"client_id": user["client_id"]}, {"_id": 0}
    ).sort("created_at", -1).to_list(200)
    balance = float(client.get("wallet_balance", 0) or 0) if client else 0
    status = "exhausted" if balance <= 0 else ("low" if balance < WALLET_LOW_THRESHOLD else "ok")
    return {
        "balance": balance,
        "status": status,
        "subscription_plan": client.get("subscription_plan") if client else None,
        "transactions": tx,
        "pricing": pricing,
    }
