"""Shared FastAPI dependencies: auth, RBAC, tenant scoping."""
from fastapi import HTTPException, Request, Depends
import jwt

from .db import db
from .security import decode_token, is_revoked


async def get_current_user(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    # Revocation check
    jti = payload.get("jti")
    if jti and await is_revoked(jti):
        raise HTTPException(status_code=401, detail="Session revoked")
    user = await db.users.find_one({"id": payload["sub"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    user["_jti"] = jti
    return user


def require_role(*roles):
    async def checker(user: dict = Depends(get_current_user)):
        if user["role"] not in roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return checker


async def tenant_filter(user: dict) -> dict:
    if user["role"] == "super_admin":
        return {}
    if not user.get("client_id"):
        raise HTTPException(status_code=403, detail="No tenant")
    return {"client_id": user["client_id"]}
