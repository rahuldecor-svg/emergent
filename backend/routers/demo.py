"""Demo Mode — one-click access + reset of the pre-seeded demo tenant."""
from fastapi import APIRouter, Depends, HTTPException, Response
from datetime import timedelta

from core.db import db
from core.deps import get_current_user
from core.security import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    set_auth_cookies, user_to_public, new_id, iso, now_utc,
)

router = APIRouter(prefix="/demo", tags=["demo"])

DEMO_EMAIL = "demo@fire-os.in"
DEMO_PASSWORD = "Demo@12345"
DEMO_CLIENT_NAME = "Demo Industries (Sample)"


async def _ensure_demo_tenant():
    existing = await db.users.find_one({"email": DEMO_EMAIL})
    if existing:
        return existing
    cid = new_id()
    now = iso(now_utc())
    await db.clients.insert_one({
        "id": cid, "name": DEMO_CLIENT_NAME, "industry": "Demo",
        "subscription_plan": "pro", "license_active": True, "wallet_balance": 9999.0,
        "features": {"emergency": True, "risk_map": True, "amc_engine": True, "noc": True},
        "demo": True, "created_at": now,
    })
    admin = {
        "id": new_id(), "email": DEMO_EMAIL,
        "password_hash": hash_password(DEMO_PASSWORD),
        "name": "Demo Admin", "role": "client_admin",
        "client_id": cid, "site_ids": [],
        "demo": True, "created_at": now,
    }
    await db.users.insert_one(admin)
    await _seed_demo_data(cid)
    return admin


async def _seed_demo_data(cid: str):
    now = iso(now_utc())
    s1 = new_id()
    await db.sites.insert_one({
        "id": s1, "client_id": cid, "name": "Demo HQ", "address": "Sample Address",
        "lat": 18.52, "lng": 73.85, "demo": True, "created_at": now,
    })
    samples = [("extinguisher", "CO2 4.5kg"), ("extinguisher", "ABC 9kg"),
               ("hydrant", "Wet Riser"), ("sprinkler", "Upright"),
               ("alarm", "Smoke Detector"), ("hose", "Fire Hose 30m")]
    assets = []
    for i, (cat, st) in enumerate(samples):
        expiry_days = -15 if i == 0 else 200
        assets.append({
            "id": new_id(), "client_id": cid, "site_id": s1,
            "name": f"{st} · Demo {i+1}", "category": cat, "sub_type": st,
            "serial_number": f"DEMO-{1000+i}",
            "install_date": iso(now_utc() - timedelta(days=180))[:10],
            "expiry_date": iso(now_utc() + timedelta(days=expiry_days))[:10],
            "location_note": f"Demo Bay {i+1}",
            "lat": 18.52 + i * 0.001, "lng": 73.85 + i * 0.001,
            "last_inspected": None, "last_maintained": None,
            "status": "active", "demo": True, "created_at": now,
        })
    if assets:
        await db.assets.insert_many(assets)

    noc_items = ["Fire NOC from CFO", "Hydrant System Test", "Emergency Lighting Test",
                 "Fire Drill Records", "Smoke Detector Functional Test"]
    await db.noc_checklist.insert_many([
        {"id": new_id(), "client_id": cid, "site_id": s1, "item": it,
         "completed": (i < 2), "demo": True, "updated_at": now}
        for i, it in enumerate(noc_items)
    ])
    await db.wallet_transactions.insert_one({
        "id": new_id(), "client_id": cid, "type": "credit",
        "amount": 9999.0, "balance_after": 9999.0,
        "reference": "Demo Seed", "note": "Demo wallet top-up",
        "gst_invoice_no": f"INV-DEMO-{new_id()[:6].upper()}",
        "gst_amount": round(9999 * 0.18 / 1.18, 2),
        "demo": True, "created_at": now,
    })


@router.post("/login")
async def demo_login(response: Response):
    """One-click demo login — idempotently creates tenant if missing, returns user + cookies."""
    user = await _ensure_demo_tenant()
    # Ensure password synced
    if not verify_password(DEMO_PASSWORD, user["password_hash"]):
        await db.users.update_one(
            {"email": DEMO_EMAIL},
            {"$set": {"password_hash": hash_password(DEMO_PASSWORD)}},
        )
    user = await db.users.find_one({"email": DEMO_EMAIL}, {"_id": 0})
    access, _a_jti, _a_exp = create_access_token(
        user["id"], user["email"], user["role"], user.get("client_id")
    )
    refresh, _r_jti, _r_exp = create_refresh_token(user["id"])
    set_auth_cookies(response, access, refresh)
    return {"user": user_to_public(user), "demo": True}


@router.post("/reset")
async def demo_reset(user: dict = Depends(get_current_user)):
    if user.get("email") != DEMO_EMAIL and user["role"] != "super_admin":
        raise HTTPException(403, "Demo reset is only available to the demo account or SSPL admin")
    # Only wipe data flagged demo=True
    cid = user["client_id"]
    demo_client = await db.clients.find_one({"id": cid, "demo": True}) if cid else None
    if not demo_client:
        raise HTTPException(400, "Not a demo tenant")
    coll = ["sites", "assets", "inspections", "maintenance_tasks", "incidents",
            "documents", "noc_checklist", "wallet_transactions",
            "notifications", "audit_logs", "support_requests"]
    for c in coll:
        await db[c].delete_many({"client_id": cid})
    # Keep the user + client but reset wallet and re-seed sample data
    await db.clients.update_one({"id": cid}, {"$set": {"wallet_balance": 9999.0}})
    await _seed_demo_data(cid)
    return {"ok": True, "message": "Demo tenant reset with fresh sample data"}
