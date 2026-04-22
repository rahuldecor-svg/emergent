"""Mongo client + common indexes."""
from motor.motor_asyncio import AsyncIOMotorClient
from .config import MONGO_URL, DB_NAME

_client = AsyncIOMotorClient(MONGO_URL)
db = _client[DB_NAME]


async def ensure_indexes():
    await db.users.create_index("email", unique=True)
    await db.password_reset_tokens.create_index("expires_at", expireAfterSeconds=0)
    await db.login_attempts.create_index("identifier")
    await db.assets.create_index("client_id")
    await db.inspections.create_index([("client_id", 1), ("asset_id", 1)])
    await db.maintenance_tasks.create_index([("client_id", 1), ("scheduled_date", 1)])
    await db.notifications.create_index([("user_id", 1), ("created_at", -1)])
    await db.wallet_transactions.create_index([("client_id", 1), ("created_at", -1)])
    await db.wallet_transactions.create_index("gst_invoice_no")
    # TTL on revoked JTIs — auto-cleanup when tokens expire
    await db.revoked_tokens.create_index("expires_at", expireAfterSeconds=0)
