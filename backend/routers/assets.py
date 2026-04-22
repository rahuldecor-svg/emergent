"""Sites + Assets + Inspections + Maintenance + Incidents."""
from datetime import timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from core.db import db
from core.deps import get_current_user, require_role, tenant_filter
from core.security import new_id, iso, now_utc
from core.notify import notify, log_audit
from core.wallet_service import charge
from core.config import COST_PER_ASSET, COST_PER_INSPECTION
from core.emailer import send_email, tpl_inspection_fail, tpl_maintenance_due

router = APIRouter(tags=["operations"])


# ---- Schemas ----
class SiteIn(BaseModel):
    name: str
    address: Optional[str] = ""
    lat: Optional[float] = None
    lng: Optional[float] = None


class AssetIn(BaseModel):
    site_id: str
    name: str
    category: str
    sub_type: Optional[str] = None
    serial_number: Optional[str] = None
    manufacturer: Optional[str] = None
    install_date: Optional[str] = None
    expiry_date: Optional[str] = None
    location_note: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None


class InspectionIn(BaseModel):
    asset_id: str
    checklist: List[Dict[str, Any]]
    overall_result: str
    inspector_name: str
    signature: Optional[str] = None
    notes: Optional[str] = None
    photo_urls: Optional[List[str]] = []


class MaintenanceIn(BaseModel):
    asset_id: str
    scheduled_date: str
    technician_id: Optional[str] = None
    notes: Optional[str] = None


class MaintenanceUpdate(BaseModel):
    status: Optional[str] = None
    completion_note: Optional[str] = None


class IncidentIn(BaseModel):
    site_id: str
    title: str
    severity: str
    description: str
    timeline: Optional[List[Dict[str, Any]]] = []


# ---- Sites ----
@router.get("/sites")
async def list_sites(user: dict = Depends(get_current_user)):
    q = await tenant_filter(user)
    return await db.sites.find(q, {"_id": 0}).to_list(1000)


@router.post("/sites")
async def create_site(body: SiteIn, user: dict = Depends(get_current_user)):
    if user["role"] not in ("super_admin", "client_admin"):
        raise HTTPException(403, "Forbidden")
    doc = {"id": new_id(), "client_id": user.get("client_id"),
           **body.model_dump(), "created_at": iso(now_utc())}
    await db.sites.insert_one(doc)
    doc.pop("_id", None)
    return doc


# ---- Assets ----
@router.get("/assets")
async def list_assets(site_id: Optional[str] = None, user: dict = Depends(get_current_user)):
    q = await tenant_filter(user)
    if site_id:
        q["site_id"] = site_id
    items = await db.assets.find(q, {"_id": 0}).sort("created_at", -1).to_list(2000)
    today = iso(now_utc())[:10]
    for a in items:
        exp = a.get("expiry_date")
        a["expiry_status"] = "expired" if exp and exp < today else (
            "expiring" if exp and exp < iso(now_utc() + timedelta(days=60))[:10] else "ok")
    return items


@router.post("/assets")
async def create_asset(body: AssetIn, user: dict = Depends(get_current_user)):
    if user["role"] not in ("super_admin", "client_admin", "fire_officer"):
        raise HTTPException(403, "Forbidden")
    # Charge wallet first — blocks when balance <= 0
    charge_info = None
    if user["role"] != "super_admin" and user.get("client_id"):
        charge_info = await charge(user["client_id"], COST_PER_ASSET,
                                   reason="Asset creation", reference=None)
    doc = {"id": new_id(), "client_id": user["client_id"], **body.model_dump(),
           "last_inspected": None, "last_maintained": None, "status": "active",
           "created_at": iso(now_utc())}
    await db.assets.insert_one(doc)
    doc.pop("_id", None)
    # Back-fill the usage tx with the asset id for traceability
    if charge_info:
        await db.wallet_transactions.update_one(
            {"id": charge_info["transaction"]["id"]},
            {"$set": {"reference": doc["id"], "reason": f"Asset creation · {doc['name']}"}},
        )
    await log_audit(user, "asset.create", doc["id"], {"name": body.name})
    return {
        **doc,
        "wallet_charge": {
            "cost": COST_PER_ASSET, "balance_after": charge_info["balance"] if charge_info else None,
            "reason": "Asset creation",
        } if charge_info else None,
    }


@router.get("/assets/{aid}")
async def get_asset(aid: str, user: dict = Depends(get_current_user)):
    q = {"id": aid, **(await tenant_filter(user))}
    a = await db.assets.find_one(q, {"_id": 0})
    if not a:
        raise HTTPException(404, "Not found")
    inspections = await db.inspections.find({"asset_id": aid}, {"_id": 0}).sort("created_at", -1).to_list(50)
    maintenance = await db.maintenance_tasks.find({"asset_id": aid}, {"_id": 0}).sort("scheduled_date", -1).to_list(50)
    return {"asset": a, "inspections": inspections, "maintenance": maintenance}


@router.delete("/assets/{aid}")
async def delete_asset(aid: str, user: dict = Depends(require_role("super_admin", "client_admin"))):
    q = {"id": aid, **(await tenant_filter(user))}
    r = await db.assets.delete_one(q)
    if not r.deleted_count:
        raise HTTPException(404, "Not found")
    await log_audit(user, "asset.delete", aid)
    return {"ok": True}


# ---- Inspections ----
@router.get("/inspections")
async def list_inspections(user: dict = Depends(get_current_user)):
    q = await tenant_filter(user)
    return await db.inspections.find(q, {"_id": 0}).sort("created_at", -1).to_list(500)


@router.post("/inspections")
async def create_inspection(body: InspectionIn, user: dict = Depends(get_current_user)):
    if user["role"] not in ("super_admin", "client_admin", "fire_officer", "technician", "auditor"):
        raise HTTPException(403, "Forbidden")
    asset = await db.assets.find_one({"id": body.asset_id, **(await tenant_filter(user))})
    if not asset:
        raise HTTPException(404, "Asset not found")

    charge_info = None
    if user["role"] != "super_admin" and user.get("client_id"):
        charge_info = await charge(user["client_id"], COST_PER_INSPECTION,
                                   reason="Inspection submission", reference=None)

    doc = {"id": new_id(), "client_id": user["client_id"], **body.model_dump(),
           "created_at": iso(now_utc())}
    await db.inspections.insert_one(doc)
    await db.assets.update_one(
        {"id": body.asset_id},
        {"$set": {"last_inspected": iso(now_utc()),
                  "status": "active" if body.overall_result == "pass" else "faulty"}},
    )

    if charge_info:
        await db.wallet_transactions.update_one(
            {"id": charge_info["transaction"]["id"]},
            {"$set": {"reference": doc["id"], "reason": f"Inspection · {asset['name']}"}},
        )

    if body.overall_result == "fail":
        admins = await db.users.find(
            {"client_id": user["client_id"], "role": {"$in": ["client_admin", "fire_officer"]}},
            {"_id": 0, "id": 1, "email": 1, "phone": 1},
        ).to_list(50)
        await notify([u["id"] for u in admins], "inspection_failed",
                     "Inspection failed",
                     f"Asset {asset['name']} failed inspection",
                     {"asset_id": body.asset_id})
        sub, html = tpl_inspection_fail(asset["name"], body.inspector_name, body.notes or "")
        await send_email([u["email"] for u in admins], sub, html)
        # WhatsApp → SMS fallback
        from core.messaging import send_critical_alert, fire_and_forget
        phones = [u.get("phone") for u in admins if u.get("phone")]
        if phones:
            fire_and_forget(send_critical_alert(
                phones, "inspection_failure",
                [asset["name"], body.inspector_name,
                 (body.notes or "")[:80]],
                {"asset_name": asset["name"],
                 "inspector": body.inspector_name,
                 "notes": (body.notes or "")[:80]},
            ))

    await log_audit(user, "inspection.create", doc["id"], {"result": body.overall_result})
    doc.pop("_id", None)
    return {
        **doc,
        "wallet_charge": {
            "cost": COST_PER_INSPECTION, "balance_after": charge_info["balance"] if charge_info else None,
            "reason": "Inspection submission",
        } if charge_info else None,
    }


# ---- Maintenance ----
@router.get("/maintenance")
async def list_maintenance(user: dict = Depends(get_current_user)):
    q = await tenant_filter(user)
    if user["role"] == "technician":
        q["technician_id"] = user["id"]
    items = await db.maintenance_tasks.find(q, {"_id": 0}).sort("scheduled_date", 1).to_list(500)
    today = iso(now_utc())[:10]
    for t in items:
        if t["status"] == "scheduled" and t["scheduled_date"] < today:
            t["status"] = "missed"
    return items


@router.post("/maintenance")
async def create_maintenance(body: MaintenanceIn, user: dict = Depends(get_current_user)):
    if user["role"] not in ("super_admin", "client_admin", "fire_officer"):
        raise HTTPException(403, "Forbidden")
    doc = {"id": new_id(), "client_id": user["client_id"], **body.model_dump(),
           "status": "scheduled", "created_at": iso(now_utc())}
    await db.maintenance_tasks.insert_one(doc)
    doc.pop("_id", None)
    # Email technician if assigned
    if body.technician_id:
        tech = await db.users.find_one({"id": body.technician_id}, {"_id": 0})
        if tech:
            asset = await db.assets.find_one({"id": body.asset_id}, {"_id": 0})
            sub, html = tpl_maintenance_due((asset or {}).get("name", "asset"), body.scheduled_date)
            await send_email([tech["email"]], sub, html)
    return doc


@router.patch("/maintenance/{tid}")
async def update_maintenance(tid: str, body: MaintenanceUpdate, user: dict = Depends(get_current_user)):
    q = {"id": tid, **(await tenant_filter(user))}
    upd = {k: v for k, v in body.model_dump().items() if v is not None}
    r = await db.maintenance_tasks.update_one(q, {"$set": upd})
    if not r.matched_count:
        raise HTTPException(404, "Not found")
    if body.status == "completed":
        task = await db.maintenance_tasks.find_one(q, {"_id": 0})
        await db.assets.update_one(
            {"id": task["asset_id"]},
            {"$set": {"last_maintained": iso(now_utc())}},
        )
    return {"ok": True}


# ---- Incidents ----
@router.get("/incidents")
async def list_incidents(user: dict = Depends(get_current_user)):
    q = await tenant_filter(user)
    return await db.incidents.find(q, {"_id": 0}).sort("created_at", -1).to_list(500)


@router.post("/incidents")
async def create_incident(body: IncidentIn, user: dict = Depends(get_current_user)):
    doc = {"id": new_id(), "client_id": user["client_id"], **body.model_dump(),
           "status": "open", "reported_by": user["name"],
           "created_at": iso(now_utc())}
    await db.incidents.insert_one(doc)
    doc.pop("_id", None)
    admins = await db.users.find(
        {"client_id": user["client_id"], "role": {"$in": ["client_admin", "fire_officer"]}},
        {"_id": 0, "id": 1}
    ).to_list(50)
    await notify([u["id"] for u in admins], "incident",
                 f"Emergency: {body.title}",
                 f"Severity {body.severity.upper()} reported at site.",
                 {"incident_id": doc["id"]})
    return doc
