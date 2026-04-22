"""Onboarding progress — tracks Site → Asset → First Inspection."""
from fastapi import APIRouter, Depends
from core.db import db
from core.deps import get_current_user, tenant_filter

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.get("/progress")
async def progress(user: dict = Depends(get_current_user)):
    if user["role"] == "super_admin" or not user.get("client_id"):
        return {"applicable": False}
    q = await tenant_filter(user)
    sites = await db.sites.count_documents(q)
    assets = await db.assets.count_documents(q)
    inspections = await db.inspections.count_documents(q)

    steps = [
        {"key": "add_site", "title": "Add your first site",
         "done": sites > 0, "action_path": "/app/sites",
         "action_label": "Go to Sites"},
        {"key": "add_asset", "title": "Add your first asset",
         "done": assets > 0, "action_path": "/app/assets",
         "action_label": "Go to Assets"},
        {"key": "first_inspection", "title": "Perform your first inspection",
         "done": inspections > 0, "action_path": "/app/assets",
         "action_label": "Open an asset"},
    ]
    done_count = sum(1 for s in steps if s["done"])
    progress_pct = round(done_count / len(steps) * 100)
    return {
        "applicable": True,
        "steps": steps,
        "done_count": done_count,
        "total": len(steps),
        "progress_pct": progress_pct,
        "completed": done_count == len(steps),
    }
