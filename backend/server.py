"""Thin FastAPI entrypoint — mounts routers, middleware, startup handlers."""
import logging
import os
from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from core.config import FRONTEND_URL
from core.db import ensure_indexes
from core.security import iso, now_utc
from core.scheduler import start_scheduler, stop_scheduler
from seed import seed_initial

from routers import (
    auth as auth_r, admin as admin_r, assets as assets_r,
    compliance as compliance_r, wallet as wallet_r,
    documents as documents_r, users as users_r, notifications as notifications_r,
    amc as amc_r, reports as reports_r, onboarding as onboarding_r,
    support as support_r, demo as demo_r,
    asset_master as am_r, qr as qr_r,
    payments as payments_r,
)

# Optional Sentry — silently no-op if SENTRY_DSN unset
SENTRY_DSN = os.environ.get("SENTRY_DSN", "")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=ENVIRONMENT,
        traces_sample_rate=0.1,
        integrations=[FastApiIntegration()],
        send_default_pii=False,
    )

app = FastAPI(
    title="Fire Compliance OS",
    version="1.4.0",
    docs_url="/api/docs" if ENVIRONMENT != "production" else None,
    redoc_url="/api/redoc" if ENVIRONMENT != "production" else None,
    openapi_url="/api/openapi.json" if ENVIRONMENT != "production" else None,
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds production security headers to every response."""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(self), microphone=(), geolocation=(self)"
        if ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


# Rate limiting (per-IP) — slowapi
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Environment-tunable. Defaults are forgiving for typical multi-tenant SaaS.
DEFAULT_RATE = os.environ.get("RATE_LIMIT_DEFAULT", "300/minute")
AUTH_RATE = os.environ.get("RATE_LIMIT_AUTH", "20/minute")

limiter = Limiter(key_func=get_remote_address, default_limits=[DEFAULT_RATE])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

api = APIRouter(prefix="/api")


@api.get("/")
async def root():
    return {"name": "Fire Compliance OS API", "version": "1.4.0",
            "status": "operational", "environment": ENVIRONMENT,
            "time": iso(now_utc())}


@api.get("/health")
async def health():
    """Lightweight health check for uptime monitors."""
    return {"ok": True, "time": iso(now_utc())}


api.include_router(auth_r.router)
api.include_router(admin_r.router)
api.include_router(assets_r.router)
api.include_router(compliance_r.router)
api.include_router(wallet_r.router)
api.include_router(documents_r.router)
api.include_router(users_r.router)
api.include_router(notifications_r.router)
api.include_router(amc_r.router)
api.include_router(reports_r.router)
api.include_router(onboarding_r.router)
api.include_router(support_r.router)
api.include_router(demo_r.router)
api.include_router(am_r.router)
api.include_router(qr_r.router)
api.include_router(payments_r.router)

app.include_router(api)

# CORS — strict by default; honours FRONTEND_URL + optional comma-separated CORS_ORIGINS
EXTRA_ORIGINS = [o.strip() for o in os.environ.get("CORS_ORIGINS", "").split(",") if o.strip() and o.strip() != "*"]
ALLOWED_ORIGINS = list({FRONTEND_URL, "http://localhost:3000", *EXTRA_ORIGINS})

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=["Content-Disposition"],
    max_age=600,
)
app.add_middleware(SecurityHeadersMiddleware)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s :: %(message)s")
log = logging.getLogger("fire-os")


@app.on_event("startup")
async def on_startup():
    await ensure_indexes()
    await seed_initial()
    start_scheduler()
    log.info("Fire Compliance OS v1.4 started — routers mounted, scheduler running.")


@app.on_event("shutdown")
async def on_shutdown():
    stop_scheduler()
    log.info("Shutting down.")
