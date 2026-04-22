"""Users management (client-admin scope + super_admin)."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr

from core.db import db
from core.deps import require_role, tenant_filter
from core.security import hash_password, new_id, iso, now_utc
from core.notify import log_audit
from core.wallet_service import charge
from core.config import COST_PER_USER

router = APIRouter(prefix="/users", tags=["users"])


class UserIn(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str
    phone: Optional[str] = None
    site_ids: Optional[List[str]] = []


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    site_ids: Optional[List[str]] = None


@router.get("")
async def list_users(user: dict = Depends(require_role("super_admin", "client_admin"))):
    q = await tenant_filter(user)
    return await db.users.find(q, {"_id": 0, "password_hash": 0}).to_list(1000)


@router.post("")
async def create_user(body: UserIn, user: dict = Depends(require_role("super_admin", "client_admin"))):
    if await db.users.find_one({"email": body.email.lower()}):
        raise HTTPException(400, "Email exists")

    charge_info = None
    if user["role"] != "super_admin" and user.get("client_id"):
        charge_info = await charge(user["client_id"], COST_PER_USER,
                                   reason="User addition", reference=None)

    doc = {"id": new_id(), "email": body.email.lower(),
           "password_hash": hash_password(body.password),
           "name": body.name, "role": body.role,
           "phone": body.phone or None,
           "client_id": user.get("client_id"), "site_ids": body.site_ids or [],
           "created_at": iso(now_utc())}
    await db.users.insert_one(doc)

    if charge_info:
        await db.wallet_transactions.update_one(
            {"id": charge_info["transaction"]["id"]},
            {"$set": {"reference": doc["id"], "reason": f"User added · {doc['email']}"}},
        )
    await log_audit(user, "user.create", doc["id"], {"email": doc["email"], "role": doc["role"]})
    return {
        "ok": True, "id": doc["id"],
        "wallet_charge": {
            "cost": COST_PER_USER, "balance_after": charge_info["balance"] if charge_info else None,
            "reason": "User addition",
        } if charge_info else None,
    }


@router.patch("/{uid}")
async def update_user(uid: str, body: UserUpdate,
                     user: dict = Depends(require_role("super_admin", "client_admin"))):
    q = {"id": uid}
    if user["role"] != "super_admin":
        q["client_id"] = user.get("client_id")
    target = await db.users.find_one(q, {"_id": 0})
    if not target:
        raise HTTPException(404, "User not found")
    upd = {k: v for k, v in body.model_dump().items() if v is not None}
    if not upd:
        return {"ok": True}
    await db.users.update_one(q, {"$set": upd})
    await log_audit(user, "user.update", uid, upd)
    return {"ok": True}


@router.post("/me/phone")
async def set_my_phone(body: UserUpdate, user: dict = Depends(require_role(
        "super_admin", "client_admin", "fire_officer", "technician", "inspector"))):
    """Self-service phone number update for the current user."""
    if not body.phone:
        raise HTTPException(400, "phone required")
    await db.users.update_one({"id": user["id"]}, {"$set": {"phone": body.phone}})
    await log_audit(user, "user.phone_update", user["id"], {"phone": body.phone})
    return {"ok": True}
