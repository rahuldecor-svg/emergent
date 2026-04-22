"""Document Vault — file upload + metadata list."""
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel

from core.db import db
from core.deps import get_current_user, tenant_filter
from core.security import new_id, iso, now_utc
from core.config import UPLOAD_DIR

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
           "uploaded_by": user["name"], "file_path": None,
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
    """Upload a file (multipart/form-data) and persist metadata."""
    if user["role"] == "super_admin":
        raise HTTPException(403, "Super admin cannot upload tenant documents")
    if not user.get("client_id"):
        raise HTTPException(403, "No tenant")
    # Scope upload dir per tenant
    tenant_dir: Path = UPLOAD_DIR / user["client_id"]
    tenant_dir.mkdir(parents=True, exist_ok=True)

    doc_id = new_id()
    safe_name = Path(file.filename or "upload.bin").name
    stored_name = f"{doc_id}-{safe_name}"
    dest = tenant_dir / stored_name

    size = 0
    with dest.open("wb") as out:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            if size > 25 * 1024 * 1024:  # 25 MB
                out.close()
                dest.unlink(missing_ok=True)
                raise HTTPException(413, "File too large (max 25 MB)")
            out.write(chunk)

    doc = {
        "id": doc_id, "client_id": user["client_id"],
        "title": title, "doc_type": doc_type,
        "site_id": site_id, "expires_on": expires_on,
        "file_path": str(dest), "file_name": safe_name, "file_size": size,
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
    if not d or not d.get("file_path"):
        raise HTTPException(404, "Not found")
    p = Path(d["file_path"])
    if not p.exists():
        raise HTTPException(404, "File missing on disk")
    return FileResponse(p, filename=d.get("file_name") or p.name,
                        media_type=d.get("content_type") or "application/octet-stream")
