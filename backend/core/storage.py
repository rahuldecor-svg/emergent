"""Object storage abstraction.

Primary: Cloudflare R2 (S3-compatible) via boto3. Tenant-scoped prefixes.
Fallback: Local disk (for dev environments without R2 keys) — SAME API.

Object key layout: tenants/{client_id}/{doc_id}-{safe_filename}

Public API:
  put_bytes(client_id, doc_id, filename, data, content_type) -> dict(location, key, size, provider)
  get_stream(key) -> (async iterator of bytes, content_type, size)
  get_presigned_url(key, expires=300) -> str | None  (R2 only)
  delete(key) -> bool
"""
import logging
from pathlib import Path
from typing import AsyncIterator, Optional, Tuple

from .config import (
    R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY,
    R2_BUCKET, R2_PUBLIC_BASE_URL, R2_REGION, UPLOAD_DIR,
)

log = logging.getLogger("storage")


def r2_configured() -> bool:
    return bool(R2_ACCOUNT_ID and R2_ACCESS_KEY_ID and R2_SECRET_ACCESS_KEY and R2_BUCKET)


def _r2_client():
    import boto3
    from botocore.config import Config as BotoConfig
    endpoint = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        region_name=R2_REGION,
        config=BotoConfig(
            signature_version="s3v4",
            s3={"addressing_style": "path"},
            retries={"max_attempts": 3, "mode": "standard"},
        ),
    )


def _safe_key(client_id: str, doc_id: str, filename: str) -> str:
    safe = Path(filename or "upload.bin").name
    return f"tenants/{client_id}/{doc_id}-{safe}"


def put_bytes(client_id: str, doc_id: str, filename: str,
              data: bytes, content_type: Optional[str]) -> dict:
    """Store file synchronously. Returns metadata dict."""
    key = _safe_key(client_id, doc_id, filename)
    size = len(data)
    if r2_configured():
        try:
            c = _r2_client()
            c.put_object(
                Bucket=R2_BUCKET, Key=key, Body=data,
                ContentType=content_type or "application/octet-stream",
            )
            location = f"r2://{R2_BUCKET}/{key}"
            return {"provider": "r2", "key": key, "location": location,
                    "size": size, "content_type": content_type}
        except Exception as e:
            log.error("R2 put failed, falling back to local: %s", e)
    # Local fallback
    tenant_dir = UPLOAD_DIR / client_id
    tenant_dir.mkdir(parents=True, exist_ok=True)
    dest = tenant_dir / f"{doc_id}-{Path(filename or 'upload.bin').name}"
    dest.write_bytes(data)
    return {"provider": "local", "key": key, "location": str(dest),
            "size": size, "content_type": content_type}


async def get_stream(key: str, provider: str, location: str
                     ) -> Tuple[AsyncIterator[bytes], str, int]:
    """Return (iterator, content_type, size). content_type may be ''."""
    if provider == "r2" and r2_configured():
        c = _r2_client()
        obj = c.get_object(Bucket=R2_BUCKET, Key=key)
        body = obj["Body"]
        ct = obj.get("ContentType") or "application/octet-stream"
        size = int(obj.get("ContentLength") or 0)

        async def _it():
            # botocore streaming body is sync; iterate chunks
            while True:
                chunk = body.read(1024 * 1024)
                if not chunk:
                    break
                yield chunk
        return _it(), ct, size

    # Local fallback (works for legacy docs stored before R2 migration)
    p = Path(location)
    if not p.exists():
        raise FileNotFoundError(f"Missing local file: {location}")
    size = p.stat().st_size

    async def _it_local():
        with p.open("rb") as f:
            while True:
                chunk = f.read(1024 * 1024)
                if not chunk:
                    break
                yield chunk
    # Guess content-type from nothing; caller usually has stored one
    return _it_local(), "application/octet-stream", size


def get_presigned_url(key: str, expires: int = 300) -> Optional[str]:
    """R2 presigned GET URL (5 min default). Returns None if not R2."""
    if not r2_configured():
        return None
    try:
        c = _r2_client()
        return c.generate_presigned_url(
            "get_object",
            Params={"Bucket": R2_BUCKET, "Key": key},
            ExpiresIn=expires,
        )
    except Exception as e:
        log.error("R2 presign failed: %s", e)
        return None


def delete(key: str, provider: str = "r2") -> bool:
    if provider == "r2" and r2_configured():
        try:
            _r2_client().delete_object(Bucket=R2_BUCKET, Key=key)
            return True
        except Exception as e:
            log.error("R2 delete failed: %s", e)
            return False
    # local best-effort
    try:
        p = Path(key)
        if p.exists():
            p.unlink()
        return True
    except Exception:
        return False
