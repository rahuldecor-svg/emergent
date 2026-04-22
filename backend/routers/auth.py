"""Auth routes: login, logout, me, refresh, password reset."""
import hashlib
import secrets
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, EmailStr, Field
import jwt

from core.db import db
from core.security import (
    verify_password, create_access_token, create_refresh_token, decode_token,
    set_auth_cookies, clear_auth_cookies, user_to_public, iso, now_utc,
    revoke_jti, hash_password, new_id, ACCESS_MIN,
)
from core.deps import get_current_user
from core.config import JWT_ALGO, JWT_SECRET, FRONTEND_URL, PASSWORD_RESET_TTL_HOURS
from core.emailer import send_email, tpl_password_reset

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginIn(BaseModel):
    email: EmailStr
    password: str


@router.post("/login")
async def login(body: LoginIn, response: Response, request: Request):
    email = body.email.lower()
    ident = f"{request.client.host if request.client else 'na'}:{email}"
    attempt = await db.login_attempts.find_one({"identifier": ident})
    if attempt and attempt.get("locked_until"):
        from datetime import datetime
        if datetime.fromisoformat(attempt["locked_until"]) > now_utc():
            raise HTTPException(status_code=429, detail="Too many attempts. Try later.")
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user or not verify_password(body.password, user["password_hash"]):
        fails = (attempt or {}).get("count", 0) + 1
        lock = iso(now_utc() + timedelta(minutes=15)) if fails >= 5 else None
        await db.login_attempts.update_one(
            {"identifier": ident},
            {"$set": {"count": fails, "locked_until": lock, "updated_at": iso(now_utc())}},
            upsert=True,
        )
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if user["role"] != "super_admin" and user.get("client_id"):
        c = await db.clients.find_one({"id": user["client_id"]}, {"_id": 0})
        if c and not c.get("license_active", True):
            raise HTTPException(status_code=403, detail="Client license suspended by SSPL")
    await db.login_attempts.delete_one({"identifier": ident})
    access, _a_jti, _a_exp = create_access_token(user["id"], user["email"], user["role"], user.get("client_id"))
    refresh, _r_jti, _r_exp = create_refresh_token(user["id"])
    set_auth_cookies(response, access, refresh)
    return {"user": user_to_public(user), "access_token": access}


@router.post("/logout")
async def logout(request: Request, response: Response, user: dict = Depends(get_current_user)):
    # Revoke current access JTI so token can't be reused even if stolen
    access = request.cookies.get("access_token")
    if access:
        try:
            payload = decode_token(access)
            jti = payload.get("jti")
            from datetime import datetime, timezone
            exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
            if jti:
                await revoke_jti(jti, exp)
        except Exception:
            pass
    # Revoke refresh too
    refresh = request.cookies.get("refresh_token")
    if refresh:
        try:
            payload = decode_token(refresh)
            jti = payload.get("jti")
            from datetime import datetime, timezone
            exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
            if jti:
                await revoke_jti(jti, exp)
        except Exception:
            pass
    clear_auth_cookies(response)
    return {"ok": True}


@router.get("/me")
async def me(user: dict = Depends(get_current_user)):
    return user_to_public(user)


@router.post("/refresh")
async def refresh_token(request: Request, response: Response):
    rt = request.cookies.get("refresh_token")
    if not rt:
        raise HTTPException(status_code=401, detail="No refresh token")
    try:
        payload = decode_token(rt)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    # Ensure refresh wasn't revoked
    from core.security import is_revoked
    if payload.get("jti") and await is_revoked(payload["jti"]):
        raise HTTPException(status_code=401, detail="Session revoked")
    user = await db.users.find_one({"id": payload["sub"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    access, _jti, _exp = create_access_token(user["id"], user["email"], user["role"], user.get("client_id"))
    response.set_cookie("access_token", access, httponly=True, secure=True, samesite="none",
                        max_age=ACCESS_MIN * 60, path="/")
    return {"ok": True}


# ---------- Password reset ----------
class ResetRequestIn(BaseModel):
    email: EmailStr


class ResetConfirmIn(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


@router.post("/password-reset/request")
async def password_reset_request(body: ResetRequestIn):
    """Always returns 200 (does not leak whether email exists)."""
    email = body.email.lower()
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if user:
        # Invalidate previous active tokens
        await db.password_reset_tokens.delete_many({"user_id": user["id"]})

        raw = secrets.token_urlsafe(48)
        token_hash = _hash_token(raw)
        from datetime import datetime
        expires_at = now_utc() + timedelta(hours=PASSWORD_RESET_TTL_HOURS)
        await db.password_reset_tokens.insert_one({
            "id": new_id(),
            "user_id": user["id"],
            "email": email,
            "token_hash": token_hash,
            "expires_at": expires_at,  # TTL index on this field
            "used": False,
            "created_at": iso(now_utc()),
        })
        reset_url = f"{FRONTEND_URL.rstrip('/')}/reset-password?token={raw}"
        subject, html = tpl_password_reset(user.get("name", ""), reset_url, PASSWORD_RESET_TTL_HOURS)
        await send_email([email], subject, html)
    return {"ok": True, "message":
            "If an account with that email exists, a reset link has been sent."}


@router.post("/password-reset/confirm")
async def password_reset_confirm(body: ResetConfirmIn):
    token_hash = _hash_token(body.token)
    tok = await db.password_reset_tokens.find_one({"token_hash": token_hash}, {"_id": 0})
    if not tok or tok.get("used"):
        raise HTTPException(400, "Invalid or expired token")

    from datetime import datetime, timezone
    exp = tok["expires_at"]
    if isinstance(exp, str):
        exp = datetime.fromisoformat(exp)
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    if exp < now_utc():
        raise HTTPException(400, "Token expired")

    user = await db.users.find_one({"id": tok["user_id"]}, {"_id": 0})
    if not user:
        raise HTTPException(400, "Invalid token")

    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {"password_hash": hash_password(body.new_password),
                  "password_updated_at": iso(now_utc())}},
    )
    await db.password_reset_tokens.update_one(
        {"id": tok["id"]},
        {"$set": {"used": True, "used_at": iso(now_utc())}},
    )
    # Revoke any login lockouts
    await db.login_attempts.delete_many({"identifier": {"$regex": f":{user['email']}$"}})
    return {"ok": True, "message": "Password updated. Please log in."}
