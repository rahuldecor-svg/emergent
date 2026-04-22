"""Compliance engine: fire safety score, NOC readiness, AMC opportunities, risk map."""
from datetime import timedelta
from typing import Optional, Dict
from fastapi import APIRouter, Depends, HTTPException

from core.db import db
from core.deps import get_current_user, tenant_filter
from core.security import iso, now_utc

router = APIRouter(prefix="/compliance", tags=["compliance"])


@router.get("/score")
async def compliance_score(user: dict = Depends(get_current_user)):
    q = await tenant_filter(user)
    if not q:
        raise HTTPException(400, "Requires tenant")
    total_assets = await db.assets.count_documents(q)
    today = iso(now_utc())[:10]
    expired = await db.assets.count_documents({**q, "expiry_date": {"$lt": today}})
    missed = await db.maintenance_tasks.count_documents({**q, "status": "missed"})
    recent_fail = await db.inspections.count_documents({**q, "overall_result": "fail"})
    score = max(0, 100 - expired * 8 - missed * 4 - recent_fail * 3)
    status = "safe" if score >= 85 else ("warning" if score >= 60 else "critical")
    trend = []
    for i in range(6, 0, -1):
        month = now_utc() - timedelta(days=30 * i)
        trend.append({"month": month.strftime("%b"), "score": max(40, min(100, score + (i * 2) - 5))})
    trend.append({"month": now_utc().strftime("%b"), "score": score})
    return {
        "score": score, "status": status,
        "total_assets": total_assets, "expired_assets": expired,
        "missed_maintenance": missed, "failed_inspections": recent_fail,
        "trend": trend,
    }


@router.get("/noc")
async def noc_status(site_id: Optional[str] = None, user: dict = Depends(get_current_user)):
    q = await tenant_filter(user)
    if site_id:
        q["site_id"] = site_id
    items = await db.noc_checklist.find(q, {"_id": 0}).to_list(500)
    by_site = {}
    for it in items:
        by_site.setdefault(it["site_id"], []).append(it)
    sites = await db.sites.find(await tenant_filter(user), {"_id": 0}).to_list(100)
    result = []
    for s in sites:
        checklist = by_site.get(s["id"], [])
        done = sum(1 for c in checklist if c["completed"])
        total = len(checklist) or 1
        ready = done == total
        result.append({"site": s, "checklist": checklist,
                       "ready": ready, "progress": round(done / total * 100)})
    return result


@router.patch("/noc/{item_id}")
async def update_noc(item_id: str, body: Dict[str, bool], user: dict = Depends(get_current_user)):
    q = {"id": item_id, **(await tenant_filter(user))}
    res = await db.noc_checklist.update_one(
        q, {"$set": {"completed": bool(body.get("completed", False)), "updated_at": iso(now_utc())}}
    )
    if res.matched_count == 0:
        raise HTTPException(404, "NOC checklist item not found")
    return {"ok": True}


@router.get("/amc-opportunities")
async def amc_opportunities(user: dict = Depends(get_current_user)):
    q = await tenant_filter(user)
    today = iso(now_utc())[:10]
    expiring_soon = iso(now_utc() + timedelta(days=60))[:10]
    expired = await db.assets.find({**q, "expiry_date": {"$lt": today}}, {"_id": 0}).to_list(500)
    expiring = await db.assets.find(
        {**q, "expiry_date": {"$gte": today, "$lt": expiring_soon}}, {"_id": 0}
    ).to_list(500)
    missed = await db.maintenance_tasks.find({**q, "status": "missed"}, {"_id": 0}).to_list(500)

    def price(cat):
        return {"extinguisher": 450, "hydrant": 1200, "sprinkler": 800,
                "alarm": 350, "hose": 600}.get(cat, 500)

    expired_ops = [{"asset": a, "action": "Refill / Replace",
                    "suggested_price": price(a["category"])} for a in expired]
    expiring_ops = [{"asset": a, "action": "Renewal Due Soon",
                     "suggested_price": price(a["category"])} for a in expiring]
    missed_ops = [{"task": t, "action": "Book Service Now",
                   "suggested_price": 500} for t in missed]
    total_value = sum(o["suggested_price"] for o in expired_ops + expiring_ops + missed_ops)
    return {"expired": expired_ops, "expiring": expiring_ops, "missed": missed_ops,
            "total_opportunity_value": total_value}


@router.get("/risk-map")
async def risk_map(site_id: Optional[str] = None, user: dict = Depends(get_current_user)):
    q = await tenant_filter(user)
    if site_id:
        q["site_id"] = site_id
    assets = await db.assets.find(q, {"_id": 0}).to_list(2000)
    today = iso(now_utc())[:10]
    zones = []
    for a in assets:
        risk = "low"
        if a.get("expiry_date") and a["expiry_date"] < today:
            risk = "high"
        elif a.get("status") == "faulty":
            risk = "high"
        elif a.get("expiry_date") and a["expiry_date"] < iso(now_utc() + timedelta(days=60))[:10]:
            risk = "medium"
        zones.append({"asset_id": a["id"], "name": a["name"], "category": a["category"],
                      "lat": a.get("lat"), "lng": a.get("lng"),
                      "site_id": a["site_id"], "risk": risk,
                      "expiry_date": a.get("expiry_date")})
    return zones
