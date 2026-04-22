"""Auth routes: login, logout, me, refresh."""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, EmailStr
import jwt

from core.db import db
from core.security import (
    verify_password, create_access_token, create_refresh_token, decode_token,
    set_auth_cookies, clear_auth_cookies, user_to_public, iso, now_utc,
    revoke_jti, ACCESS_MIN,
)
from core.deps import get_current_user
from core.config import JWT_ALGO, JWT_SECRET

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
