"""Document Vault — file upload/download backed by object storage (R2 → local fallback)."""
from pathlib import Path
from typing import Optional
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

router = APIRouter(prefix="/documents", tags=["documents"])


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
    title: str = Form(...),
    doc_type: str = Form("other"),
    site_id: Optional[str] = Form(None),
    expires_on: Optional[str] = Form(None),
    user: dict = Depends(get_current_user),
):
    if user["role"] == "super_admin":
        raise HTTPException(403, "Super admin cannot upload tenant documents")
    if not user.get("client_id"):
        raise HTTPException(403, "No tenant")

    # Read body with size guard
    max_bytes = MAX_UPLOAD_MB * 1024 * 1024
    buf = bytearray()
    while True:
        chunk = await file.read(1024 * 1024)
        if not chunk:
            break
        buf.extend(chunk)
        if len(buf) > max_bytes:
            raise HTTPException(413, f"File too large (max {MAX_UPLOAD_MB} MB)")

    doc_id = new_id()
    safe_name = Path(file.filename or "upload.bin").name
    meta = put_bytes(
        client_id=user["client_id"],
        doc_id=doc_id,
        filename=safe_name,
        data=bytes(buf),
        content_type=file.content_type,
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
        "content_type": file.content_type,
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

    # Local fallback (legacy or R2 missing)
    if not location:
        raise HTTPException(404, "File missing")
    p = Path(location)
    if p.exists():
        return FileResponse(p, filename=fname, media_type=ct)

    # R2 object without presigned URL support → stream through backend
    if provider == "r2" and key:
        iterator, ct2, size = await get_stream(key, provider, location or "")
        headers = {"Content-Disposition": f'attachment; filename="{fname}"'}
        if size:
            headers["Content-Length"] = str(size)
        return StreamingResponse(iterator, media_type=ct or ct2, headers=headers)

    raise HTTPException(404, "File missing on storage")
