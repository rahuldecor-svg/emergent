"""Thin FastAPI entrypoint — mounts routers, middleware, startup handlers."""
import logging
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from core.config import FRONTEND_URL
from core.db import ensure_indexes
from core.security import iso, now_utc
from seed import seed_initial

from routers import (
    auth as auth_r, admin as admin_r, assets as assets_r,
    compliance as compliance_r, wallet as wallet_r,
    documents as documents_r, users as users_r, notifications as notifications_r,
)

app = FastAPI(title="Fire Compliance OS", version="1.1.0")

api = APIRouter(prefix="/api")


@api.get("/")
async def root():
    return {"name": "Fire Compliance OS API", "version": "1.1.0",
            "status": "operational", "time": iso(now_utc())}


api.include_router(auth_r.router)
api.include_router(admin_r.router)
api.include_router(assets_r.router)
api.include_router(compliance_r.router)
api.include_router(wallet_r.router)
api.include_router(documents_r.router)
api.include_router(users_r.router)
api.include_router(notifications_r.router)

app.include_router(api)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s :: %(message)s")
log = logging.getLogger("fire-os")


@app.on_event("startup")
async def on_startup():
    await ensure_indexes()
    await seed_initial()
    log.info("Fire Compliance OS started — DB ready, seed idempotent.")


@app.on_event("shutdown")
async def on_shutdown():
    log.info("Shutting down.")
