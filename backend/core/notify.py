"""In-app notification + audit log helpers."""
from typing import List, Optional

from .db import db
from .security import new_id, iso, now_utc


SEVERITY_BY_KIND = {
    "incident": "critical",
    "inspection_failed": "critical",
    "wallet_exhausted": "critical",
    "expired_assets": "critical",
    "wallet_low": "warning",
    "maintenance_due": "warning",
    "support_request": "warning",
    "amc_booked": "info",
    "wallet": "info",
    "user_added": "info",
}


async def notify(user_ids: List[str], kind: str, title: str, body: str,
                 meta: Optional[dict] = None, severity: Optional[str] = None):
    sev = severity or SEVERITY_BY_KIND.get(kind, "info")
    docs = [{
        "id": new_id(), "user_id": uid, "kind": kind, "severity": sev,
        "title": title, "body": body,
        "meta": meta or {}, "read": False, "created_at": iso(now_utc()),
    } for uid in user_ids]
    if docs:
        await db.notifications.insert_many(docs)


async def log_audit(user: dict, action: str, target: str, details: Optional[dict] = None,
                    request=None):
    """Append-only audit log. Optionally captures IP + user-agent from request."""
    entry = {
        "id": new_id(), "user_id": user["id"], "user_email": user["email"],
        "client_id": user.get("client_id"), "action": action, "target": target,
        "details": details or {}, "created_at": iso(now_utc()),
    }
    if request is not None:
        try:
            xff = request.headers.get("x-forwarded-for", "")
            entry["ip"] = (xff.split(",")[0].strip() if xff
                           else (request.client.host if request.client else None))
            entry["user_agent"] = request.headers.get("user-agent", "")[:300]
        except Exception:  # pragma: no cover — never fail audit
            pass
    await db.audit_logs.insert_one(entry)
