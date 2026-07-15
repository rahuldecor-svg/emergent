"""JWT + password hashing + token revocation list."""
import uuid
import bcrypt
import jwt
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import Response

from .config import JWT_SECRET, JWT_ALGO, ACCESS_MIN, REFRESH_DAYS, BCRYPT_ROUNDS
from .db import db


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def new_id() -> str:
    return str(uuid.uuid4())


def hash_password(pw: str) -> str:
    # Hard floor at 12 rounds — even if BCRYPT_ROUNDS env is misconfigured below this.
    rounds = max(int(BCRYPT_ROUNDS), 12)
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt(rounds)).decode()


def verify_password(pw: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(pw.encode(), hashed.encode())
    except Exception:
        return False


def create_access_token(user_id: str, email: str, role: str, client_id: Optional[str]) -> tuple[str, str, datetime]:
    jti = new_id()
    exp = now_utc() + timedelta(minutes=ACCESS_MIN)
    payload = {"sub": user_id, "email": email, "role": role, "client_id": client_id,
               "type": "access", "jti": jti, "exp": exp}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)
    return token, jti, exp


def create_refresh_token(user_id: str) -> tuple[str, str, datetime]:
    jti = new_id()
    exp = now_utc() + timedelta(days=REFRESH_DAYS)
    payload = {"sub": user_id, "type": "refresh", "jti": jti, "exp": exp}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)
    return token, jti, exp


def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])


def set_auth_cookies(response: Response, access: str, refresh: str):
    response.set_cookie("access_token", access, httponly=True, secure=True, samesite="none",
                        max_age=ACCESS_MIN * 60, path="/")
    response.set_cookie("refresh_token", refresh, httponly=True, secure=True, samesite="none",
                        max_age=REFRESH_DAYS * 86400, path="/")


def clear_auth_cookies(response: Response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")


async def revoke_jti(jti: str, expires_at: datetime):
    await db.revoked_tokens.insert_one({"jti": jti, "expires_at": expires_at})


async def is_revoked(jti: str) -> bool:
    return await db.revoked_tokens.find_one({"jti": jti}) is not None


def user_to_public(u: dict) -> dict:
    return {
        "id": u["id"], "email": u["email"], "name": u["name"],
        "role": u["role"], "client_id": u.get("client_id"),
        "site_ids": u.get("site_ids", []),
        "created_at": u["created_at"],
    }
