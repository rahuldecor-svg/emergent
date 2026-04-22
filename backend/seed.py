"""Initial seed (idempotent): SSPL super admin + demo Acme client."""
from datetime import timedelta

from core.db import db
from core.security import hash_password, verify_password, new_id, iso, now_utc
from core.config import ADMIN_EMAIL, ADMIN_PASSWORD


async def seed_initial():
    existing = await db.users.find_one({"email": ADMIN_EMAIL})
    if not existing:
        await db.users.insert_one({
            "id": new_id(), "email": ADMIN_EMAIL, "password_hash": hash_password(ADMIN_PASSWORD),
            "name": "SSPL Super Admin", "role": "super_admin", "client_id": None,
            "site_ids": [], "created_at": iso(now_utc()),
        })
    else:
        if not verify_password(ADMIN_PASSWORD, existing["password_hash"]):
            await db.users.update_one(
                {"email": ADMIN_EMAIL}, {"$set": {"password_hash": hash_password(ADMIN_PASSWORD)}}
            )

    any_client = await db.clients.find_one({})
    if any_client:
        return

    cid = new_id()
    now = iso(now_utc())
    await db.clients.insert_one({
        "id": cid, "name": "Acme Industries", "industry": "Manufacturing",
        "gstin": "27ABCDE1234F1Z5", "subscription_plan": "pro",
        "license_active": True, "wallet_balance": 5000.0,
        "features": {"emergency": True, "risk_map": True, "amc_engine": True, "noc": True},
        "created_at": now,
    })
    s1 = new_id()
    s2 = new_id()
    await db.sites.insert_many([
        {"id": s1, "client_id": cid, "name": "Plant A - Pune",
         "address": "MIDC Pune", "lat": 18.52, "lng": 73.85, "created_at": now},
        {"id": s2, "client_id": cid, "name": "Warehouse - Mumbai",
         "address": "JNPT Road", "lat": 19.07, "lng": 72.87, "created_at": now},
    ])
    admin_id = new_id(); off_id = new_id(); tech_id = new_id()
    await db.users.insert_many([
        {"id": admin_id, "email": "admin@acme.in", "password_hash": hash_password("Acme@12345"),
         "name": "Rohit Sharma", "role": "client_admin", "client_id": cid,
         "site_ids": [s1, s2], "created_at": now},
        {"id": off_id, "email": "officer@acme.in", "password_hash": hash_password("Officer@123"),
         "name": "Priya Nair", "role": "fire_officer", "client_id": cid,
         "site_ids": [s1], "created_at": now},
        {"id": tech_id, "email": "tech@acme.in", "password_hash": hash_password("Tech@12345"),
         "name": "Suresh Kumar", "role": "technician", "client_id": cid,
         "site_ids": [s1, s2], "created_at": now},
    ])

    cats = [("extinguisher", "CO2 4.5kg"), ("extinguisher", "ABC 9kg"), ("hydrant", "Wet Riser"),
            ("sprinkler", "Upright"), ("alarm", "Smoke Detector"), ("hose", "Fire Hose 30m")]
    asset_docs = []
    for i, (cat, st) in enumerate(cats * 3):
        expiry_days = -30 if i % 7 == 0 else (45 if i % 5 == 0 else 365)
        install_days = -400 + (i * 20)
        asset_docs.append({
            "id": new_id(), "client_id": cid,
            "site_id": s1 if i % 2 == 0 else s2,
            "name": f"{st} #{i+1}", "category": cat, "sub_type": st,
            "serial_number": f"SN-{1000+i}",
            "manufacturer": "Ceasefire" if i % 2 else "Safex",
            "install_date": iso(now_utc() + timedelta(days=install_days))[:10],
            "expiry_date": iso(now_utc() + timedelta(days=expiry_days))[:10],
            "location_note": f"Bay {i+1}",
            "lat": 18.52 + i * 0.001, "lng": 73.85 + i * 0.001,
            "last_inspected": None, "last_maintained": None,
            "status": "active", "created_at": now,
        })
    await db.assets.insert_many(asset_docs)

    tasks = []
    for i, a in enumerate(asset_docs[:8]):
        delta = -5 if i % 3 == 0 else (7 if i % 2 == 0 else 30)
        tasks.append({
            "id": new_id(), "client_id": cid, "asset_id": a["id"],
            "scheduled_date": iso(now_utc() + timedelta(days=delta))[:10],
            "technician_id": tech_id,
            "status": "missed" if delta < 0 else "scheduled",
            "notes": "Routine check per NFPA-10", "created_at": now,
        })
    await db.maintenance_tasks.insert_many(tasks)

    noc_items = ["Fire NOC from CFO", "Building Plan Sanction", "Hydrant System Test",
                 "Emergency Lighting Test", "Fire Drill Records (last 6 months)",
                 "Fire Extinguisher Refill Certificate", "Smoke Detector Functional Test"]
    for sid in [s1, s2]:
        await db.noc_checklist.insert_many([
            {"id": new_id(), "client_id": cid, "site_id": sid, "item": it,
             "completed": (i < 4), "updated_at": now}
            for i, it in enumerate(noc_items)
        ])

    await db.wallet_transactions.insert_one({
        "id": new_id(), "client_id": cid, "type": "credit", "amount": 5000.0,
        "balance_after": 5000.0, "reference": "Seed", "note": "Initial credit",
        "gst_invoice_no": "INV-SEED-0001", "gst_amount": round(5000 * 0.18 / 1.18, 2),
        "created_at": now,
    })
