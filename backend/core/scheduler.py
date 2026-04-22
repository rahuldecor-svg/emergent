"""Daily automation: scan expired assets + maintenance due tomorrow; alert & email."""
import logging
from datetime import timedelta, datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from .db import db
from .security import iso, now_utc, new_id
from .emailer import send_email, tpl_maintenance_due
from .notify import notify

log = logging.getLogger("scheduler")
_scheduler: AsyncIOScheduler | None = None


async def scan_and_alert() -> dict:
    """Scan every client; send alerts for maintenance-due-tomorrow and expired assets.
    De-duplicated per (client_id, day) to avoid spamming when run multiple times a day.
    """
    today = iso(now_utc())[:10]
    tomorrow = iso(now_utc() + timedelta(days=1))[:10]
    sent_summary = {"clients_scanned": 0, "maintenance_alerts": 0, "expired_alerts": 0}

    clients = await db.clients.find({"license_active": True}, {"_id": 0}).to_list(1000)
    for c in clients:
        sent_summary["clients_scanned"] += 1
        cid = c["id"]

        # Dedupe: one alert per day per client
        daily_key = f"alerts:{cid}:{today}"
        if await db.scheduler_runs.find_one({"key": daily_key}):
            continue

        # Maintenance due tomorrow
        upcoming = await db.maintenance_tasks.find(
            {"client_id": cid, "status": "scheduled", "scheduled_date": tomorrow},
            {"_id": 0}
        ).to_list(500)
        # Expired assets (still active status)
        expired = await db.assets.find(
            {"client_id": cid, "expiry_date": {"$lt": today}},
            {"_id": 0}
        ).to_list(500)

        if not upcoming and not expired:
            await db.scheduler_runs.insert_one({"key": daily_key, "at": iso(now_utc())})
            continue

        admins = await db.users.find(
            {"client_id": cid, "role": {"$in": ["client_admin", "fire_officer"]}},
            {"_id": 0, "id": 1, "email": 1}
        ).to_list(50)
        admin_ids = [a["id"] for a in admins]
        admin_emails = [a["email"] for a in admins]

        for t in upcoming:
            asset = await db.assets.find_one({"id": t["asset_id"]}, {"_id": 0}) or {}
            await notify(admin_ids, "maintenance_due",
                         f"Maintenance due tomorrow — {asset.get('name','asset')}",
                         f"Scheduled {t['scheduled_date']}. Please ensure technician availability.",
                         meta={"asset_id": t.get("asset_id"), "task_id": t["id"]},
                         severity="warning")
            sub, html = tpl_maintenance_due(asset.get("name", "asset"), t["scheduled_date"])
            await send_email(admin_emails, sub, html)
            sent_summary["maintenance_alerts"] += 1

        if expired:
            names = ", ".join([a["name"] for a in expired[:5]])
            more = f" (+{len(expired)-5} more)" if len(expired) > 5 else ""
            await notify(admin_ids, "expired_assets",
                         f"{len(expired)} expired asset(s) need attention",
                         f"Expired items: {names}{more}",
                         meta={"count": len(expired)}, severity="critical")
            await send_email(admin_emails,
                             f"[Fire OS] {len(expired)} expired asset(s) in your inventory",
                             f"<p>These assets have crossed expiry and require refill/replacement:</p><p>{names}{more}</p>")
            sent_summary["expired_alerts"] += 1

        await db.scheduler_runs.insert_one({"key": daily_key, "at": iso(now_utc())})

    log.info("scan_and_alert done: %s", sent_summary)
    return sent_summary


def start_scheduler():
    global _scheduler
    if _scheduler and _scheduler.running:
        return _scheduler
    _scheduler = AsyncIOScheduler(timezone="UTC")
    # Daily at 03:00 UTC (~ 08:30 IST)
    _scheduler.add_job(scan_and_alert, CronTrigger(hour=3, minute=0),
                       id="daily_compliance_scan", replace_existing=True)
    _scheduler.start()
    log.info("Scheduler started — daily_compliance_scan at 03:00 UTC")
    return _scheduler


def stop_scheduler():
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
