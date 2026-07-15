"""Document Vault — secure file upload/download backed by object storage (R2 → local fallback).

Security hardening (v1.4.2):
  - Magic-byte MIME detection (rejects spoofed content-type)
  - Extension allow-list
  - Size enforcement during streamed read (no full-memory accumulation beyond cap)
  - Always Content-Disposition: attachment on download (prevents inline execution)
"""
from pathlib import Path
from typing import Optional
import logging

import magic  # python-magic / libmagic

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse, RedirectResponse, FileResponse
from pydantic import BaseModel

from core.db import db
from core.deps import get_current_user, tenant_filter
from core.security import new_id, iso, now_utc
from core.config import MAX_UPLOAD_MB
from core.storage import (
    put_bytes, get_stream, get_presigned_url, r2_configured,
)

log = logging.getLogger("documents")
router = APIRouter(prefix="/documents", tags=["documents"])

# Allow-list: file extensions + their permitted MIME types
ALLOWED_EXTENSIONS = {
    ".pdf":  {"application/pdf"},
    ".jpg":  {"image/jpeg"},
    ".jpeg": {"image/jpeg"},
    ".png":  {"image/png"},
    ".webp": {"image/webp"},
    ".doc":  {"application/msword"},
    ".docx": {"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
              "application/zip"},  # docx is a zip container
    ".xls":  {"application/vnd.ms-excel", "application/x-ole-storage"},
    ".xlsx": {"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
              "application/zip"},
    ".txt":  {"text/plain"},
    ".csv":  {"text/csv", "text/plain", "application/csv"},
}


def _validate_upload(filename: str, head: bytes) -> tuple[str, str]:
    """Validate filename + content. Returns (safe_filename, detected_mime).
    Raises HTTPException on rejection."""
    if not filename:
        raise HTTPException(400, "Filename required")
    safe = Path(filename).name  # strip path traversal
    ext = Path(safe).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            415,
            f"File type '{ext or 'unknown'}' not allowed. "
            f"Accepted: {', '.join(sorted(ALLOWED_EXTENSIONS.keys()))}",
        )
    detected = magic.from_buffer(head, mime=True) if head else "application/octet-stream"
    if detected not in ALLOWED_EXTENSIONS[ext]:
        log.warning("MIME mismatch: filename=%s ext=%s detected=%s expected=%s",
                    safe, ext, detected, ALLOWED_EXTENSIONS[ext])
        raise HTTPException(
            415,
            f"File content does not match extension '{ext}'. Detected: {detected}",
        )
    return safe, detected


class DocumentIn(BaseModel):
    site_id: Optional[str] = None
    title: str
    doc_type: str
    expires_on: Optional[str] = None
    file_url: Optional[str] = None


@router.get("")
async def list_documents(user: dict = Depends(get_current_user)):
    q = await tenant_filter(user)
    return await db.documents.find(q, {"_id": 0}).sort("created_at", -1).to_list(500)


@router.post("")
async def create_document(body: DocumentIn, user: dict = Depends(get_current_user)):
    doc = {"id": new_id(), "client_id": user["client_id"], **body.model_dump(),
           "uploaded_by": user["name"], "storage_provider": None,
           "storage_key": None, "storage_location": None,
           "file_path": None,  # legacy
           "created_at": iso(now_utc())}
    await db.documents.insert_one(doc)
    doc.pop("_id", None)
    return doc


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(..., max_length=200),
    doc_type: str = Form("other", max_length=50),
    site_id: Optional[str] = Form(None, max_length=100),
    expires_on: Optional[str] = Form(None, max_length=30),
    user: dict = Depends(get_current_user),
):
    if user["role"] == "super_admin":
        raise HTTPException(403, "Super admin cannot upload tenant documents")
    if not user.get("client_id"):
        raise HTTPException(403, "No tenant")

    # Read body with strict streaming guard
    max_bytes = MAX_UPLOAD_MB * 1024 * 1024
    buf = bytearray()
    head_for_mime = b""
    total_read = 0
    while True:
        chunk = await file.read(1024 * 1024)
        if not chunk:
            break
        total_read += len(chunk)
        if total_read > max_bytes:
            raise HTTPException(413, f"File too large (max {MAX_UPLOAD_MB} MB)")
        if not head_for_mime:
            head_for_mime = chunk[:2048]
        buf.extend(chunk)

    if total_read == 0:
        raise HTTPException(400, "Empty file")

    # Validate filename + magic-byte content
    safe_name, detected_mime = _validate_upload(file.filename or "upload.bin", head_for_mime)

    doc_id = new_id()
    meta = put_bytes(
        client_id=user["client_id"],
        doc_id=doc_id,
        filename=safe_name,
        data=bytes(buf),
        content_type=detected_mime,  # use server-detected MIME, NOT client-supplied
    )

    doc = {
        "id": doc_id, "client_id": user["client_id"],
        "title": title, "doc_type": doc_type,
        "site_id": site_id, "expires_on": expires_on,
        "storage_provider": meta["provider"],
        "storage_key": meta["key"],
        "storage_location": meta["location"],
        # Legacy compatibility: 'file_path' retained when local
        "file_path": meta["location"] if meta["provider"] == "local" else None,
        "file_name": safe_name, "file_size": meta["size"],
        "content_type": detected_mime,
        "uploaded_by": user["name"],
        "created_at": iso(now_utc()),
    }
    await db.documents.insert_one(doc)
    doc.pop("_id", None)
    return doc


@router.get("/file/{doc_id}")
async def download_document(doc_id: str, user: dict = Depends(get_current_user)):
    q = {"id": doc_id, **(await tenant_filter(user))}
    d = await db.documents.find_one(q, {"_id": 0})
    if not d:
        raise HTTPException(404, "Not found")

    provider = d.get("storage_provider")
    key = d.get("storage_key")
    location = d.get("storage_location") or d.get("file_path")
    ct = d.get("content_type") or "application/octet-stream"
    fname = d.get("file_name") or f"{doc_id}.bin"

    # R2: serve via short-lived presigned redirect (saves egress)
    if provider == "r2" and key and r2_configured():
        url = get_presigned_url(key, expires=300)
        if url:
            return RedirectResponse(url, status_code=302)

    # Local fallback (legacy or R2 missing). Always force download — never inline.
    if not location:
        raise HTTPException(404, "File missing")
    p = Path(location)
    if p.exists():
        return FileResponse(
            p, filename=fname, media_type=ct,
            headers={"Content-Disposition": f'attachment; filename="{fname}"'},
        )

    # R2 object without presigned URL support → stream through backend
    if provider == "r2" and key:
        iterator, ct2, size = await get_stream(key, provider, location or "")
        headers = {"Content-Disposition": f'attachment; filename="{fname}"'}
        if size:
            headers["Content-Length"] = str(size)
        return StreamingResponse(iterator, media_type=ct or ct2, headers=headers)

    raise HTTPException(404, "File missing on storage")
