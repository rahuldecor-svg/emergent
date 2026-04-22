"""In-app notification + audit log helpers."""
from typing import List, Optional

from .db import db
from .security import new_id, iso, now_utc


async def notify(user_ids: List[str], kind: str, title: str, body: str, meta: Optional[dict] = None):
    docs = [{
        "id": new_id(), "user_id": uid, "kind": kind, "title": title, "body": body,
        "meta": meta or {}, "read": False, "created_at": iso(now_utc()),
    } for uid in user_ids]
    if docs:
        await db.notifications.insert_many(docs)


async def log_audit(user: dict, action: str, target: str, details: Optional[dict] = None):
    await db.audit_logs.insert_one({
        "id": new_id(), "user_id": user["id"], "user_email": user["email"],
        "client_id": user.get("client_id"), "action": action, "target": target,
        "details": details or {}, "created_at": iso(now_utc()),
    })
