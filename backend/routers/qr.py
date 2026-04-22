"""QR code print sheets — single asset or bulk sheet (10/20 per A4)."""
from typing import List, Optional
from io import BytesIO
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF

from core.db import db
from core.deps import get_current_user, tenant_filter
from core.config import FRONTEND_URL

router = APIRouter(prefix="/qr", tags=["qr"])


class QrSheetIn(BaseModel):
    asset_ids: List[str]
    layout: int = 10  # 1, 10, 20


def _draw_qr_cell(c, x, y, w, h, url: str, title: str, subtitle: str):
    """Render one QR + label inside the cell at (x,y) (bottom-left)."""
    pad = 0.25 * cm
    qr_size = min(w, h) * 0.65
    # QR
    qw = QrCodeWidget(url)
    bounds = qw.getBounds()
    qw_w = bounds[2] - bounds[0]
    qw_h = bounds[3] - bounds[1]
    d = Drawing(qr_size, qr_size, transform=[qr_size / qw_w, 0, 0, qr_size / qw_h, 0, 0])
    d.add(qw)
    # Center the QR horizontally within the cell
    qx = x + (w - qr_size) / 2
    qy = y + (h - qr_size - 1.0 * cm)
    renderPDF.draw(d, c, qx, qy)
    # Labels
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(x + w / 2, y + 0.7 * cm, title[:34])
    c.setFont("Helvetica", 7)
    c.setFillColor(colors.HexColor("#6b7280"))
    c.drawCentredString(x + w / 2, y + 0.35 * cm, subtitle[:44])
    # Cell border
    c.setStrokeColor(colors.HexColor("#e5e7eb"))
    c.setLineWidth(0.3)
    c.rect(x + pad, y + pad, w - 2 * pad, h - 2 * pad)


def _build_pdf(assets: list, layout: int) -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    W, H = A4

    if layout == 1:
        cols, rows = 1, 1
        top_margin = 6 * cm
        cell_w = 10 * cm
        cell_h = 10 * cm
    elif layout == 20:
        cols, rows = 4, 5
        top_margin = 2.5 * cm
        cell_w = (W - 3 * cm) / cols
        cell_h = (H - top_margin - 2 * cm) / rows
    else:  # 10
        cols, rows = 2, 5
        top_margin = 2.5 * cm
        cell_w = (W - 3 * cm) / cols
        cell_h = (H - top_margin - 2 * cm) / rows

    per_page = cols * rows

    def draw_header():
        c.setFillColor(colors.HexColor("#111827"))
        c.rect(0, H - 1.5 * cm, W, 1.5 * cm, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(1.5 * cm, H - 1 * cm, "FIRE COMPLIANCE OS — QR PRINT SHEET")
        c.setFont("Helvetica", 8)
        c.drawRightString(W - 1.5 * cm, H - 1 * cm,
                          "Recommended 2x2 inch label · laminate after printing")
        c.setFillColor(colors.HexColor("#6b7280"))
        c.setFont("Helvetica", 7)
        c.drawString(1.5 * cm, 1 * cm,
                     "Tamper-evident sticker recommended. A4 or label printer. © SSPL")

    for i, a in enumerate(assets):
        idx_in_page = i % per_page
        if idx_in_page == 0:
            if i > 0:
                c.showPage()
            draw_header()

        col = idx_in_page % cols
        row = idx_in_page // cols
        x = 1.5 * cm + col * cell_w
        y = H - top_margin - (row + 1) * cell_h

        url = f"{FRONTEND_URL}/app/assets/{a['id']}"
        subtitle = f"{a.get('category','').upper()} · {a.get('serial_number') or a['id'][:8]}"
        if layout == 1:
            subtitle = f"{a.get('category','').upper()} · {a.get('serial_number') or a['id'][:8]} · Scan to view history"
        _draw_qr_cell(c, x, y, cell_w, cell_h, url, a.get("name", "Asset"), subtitle)

    c.save()
    pdf = buf.getvalue()
    buf.close()
    return pdf


@router.get("/asset/{aid}")
async def qr_single(aid: str, user: dict = Depends(get_current_user)):
    q = {"id": aid, **(await tenant_filter(user))}
    asset = await db.assets.find_one(q, {"_id": 0})
    if not asset:
        raise HTTPException(404, "Asset not found")
    pdf = _build_pdf([asset], layout=1)
    name = (asset.get("name") or "asset").replace(" ", "_")
    return Response(pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="qr-{name}.pdf"'})


@router.post("/sheet")
async def qr_sheet(body: QrSheetIn, user: dict = Depends(get_current_user)):
    if body.layout not in (1, 10, 20):
        raise HTTPException(400, "layout must be 1, 10, or 20")
    q = await tenant_filter(user)
    ids = body.asset_ids or []
    if not ids:
        raise HTTPException(400, "asset_ids required")
    assets = await db.assets.find({"id": {"$in": ids}, **q}, {"_id": 0}).to_list(500)
    # Preserve requested order
    by_id = {a["id"]: a for a in assets}
    ordered = [by_id[i] for i in ids if i in by_id]
    if not ordered:
        raise HTTPException(404, "No matching assets")
    pdf = _build_pdf(ordered, layout=body.layout)
    return Response(pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="qr-sheet-{body.layout}.pdf"'})
