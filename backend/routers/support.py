"""Support / Service Requests."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from core.db import db
from core.deps import get_current_user, tenant_filter
from core.security import new_id, iso, now_utc
from core.notify import notify, log_audit
from core.emailer import send_email

router = APIRouter(prefix="/support-requests", tags=["support"])


class SupportRequestIn(BaseModel):
    subject: str
    category: str  # service|billing|technical|other
    priority: str  # low|medium|high
    description: str
    related_asset_id: Optional[str] = None


@router.get("")
async def list_requests(user: dict = Depends(get_current_user)):
    if user["role"] == "super_admin":
        items = await db.support_requests.find({}, {"_id": 0}).sort("created_at", -1).to_list(500)
    else:
        q = await tenant_filter(user)
        items = await db.support_requests.find(q, {"_id": 0}).sort("created_at", -1).to_list(500)
    return items


@router.post("")
async def create_request(body: SupportRequestIn, user: dict = Depends(get_current_user)):
    if not user.get("client_id"):
        raise HTTPException(403, "Tenant required to raise service request")
    doc = {
        "id": new_id(), "client_id": user["client_id"],
        "subject": body.subject, "category": body.category,
        "priority": body.priority, "description": body.description,
        "related_asset_id": body.related_asset_id,
        "status": "open", "raised_by_id": user["id"],
        "raised_by_name": user["name"], "raised_by_email": user["email"],
        "created_at": iso(now_utc()),
    }
    await db.support_requests.insert_one(doc)
    doc.pop("_id", None)

    # Notify all SSPL super_admins (in-app + email)
    sspl = await db.users.find({"role": "super_admin"}, {"_id": 0, "id": 1, "email": 1}).to_list(10)
    severity = "critical" if body.priority == "high" else ("warning" if body.priority == "medium" else "info")
    await notify(
        [u["id"] for u in sspl], "support_request",
        f"Service request · {body.subject}",
        f"{body.priority.upper()} priority · {body.category} · from {user['name']}",
        meta={"request_id": doc["id"], "client_id": user["client_id"]},
        severity=severity,
    )
    await send_email(
        [u["email"] for u in sspl],
        f"[Fire OS] Service request ({body.priority.upper()}) — {body.subject}",
        f"<p>{body.description}</p><p>From: {user['name']} ({user['email']})</p>",
    )
    await log_audit(user, "support.create", doc["id"],
                    {"priority": body.priority, "category": body.category})
    return doc


@router.patch("/{rid}")
async def update_request(rid: str, body: dict, user: dict = Depends(get_current_user)):
    # super_admin can update any; client_admin can close their own
    if user["role"] == "super_admin":
        q = {"id": rid}
    elif user["role"] == "client_admin":
        q = {"id": rid, "client_id": user["client_id"]}
    else:
        raise HTTPException(403, "Forbidden")
    allowed = {k: v for k, v in body.items() if k in ("status", "resolution_note")}
    if not allowed:
        return {"ok": True}
    r = await db.support_requests.update_one(q, {"$set": allowed})
    if not r.matched_count:
        raise HTTPException(404, "Not found")
    return {"ok": True}
