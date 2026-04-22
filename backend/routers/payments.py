"""Razorpay payment integration — wallet recharge with GST invoice.

Flow:
  1. Client calls POST /payments/order with amount (in INR).
     Backend creates Razorpay order (idempotent) and stores intent.
  2. Frontend opens Razorpay Checkout with that order_id.
  3. On payment success, frontend calls POST /payments/verify with signature.
     Backend verifies HMAC, credits wallet idempotently, generates GST invoice no.
  4. Webhook POST /payments/webhook acts as async safety net for same flow.
  5. GET /payments/invoice/{invoice_no}  -> PDF GST invoice.

No mock flows. Fails fast if keys are missing.
"""
import hmac
import hashlib
import logging
from io import BytesIO
from typing import Optional

import razorpay
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from pydantic import BaseModel, Field

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
)

from core.db import db
from core.deps import get_current_user, require_role
from core.security import new_id, iso, now_utc
from core.config import (
    RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET, RAZORPAY_WEBHOOK_SECRET,
    SSPL_GSTIN, SSPL_COMPANY_NAME, SSPL_ADDRESS, SSPL_STATE_CODE,
    SSPL_PAN, SSPL_HSN_CODE, GST_RATE,
)
from core.wallet_service import credit as wallet_credit
from core.notify import log_audit

log = logging.getLogger("payments")
router = APIRouter(prefix="/payments", tags=["payments"])


def _rzp_client() -> razorpay.Client:
    if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
        raise HTTPException(
            503,
            "Payments not configured. Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in backend/.env",
        )
    return razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


class OrderIn(BaseModel):
    amount: float = Field(gt=0, description="INR (will be converted to paise)")


class VerifyIn(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


# ---------- Config (public key for frontend) ----------
@router.get("/config")
async def payments_config(user: dict = Depends(get_current_user)):
    return {
        "key_id": RAZORPAY_KEY_ID,
        "configured": bool(RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET),
        "gst_rate": GST_RATE,
    }


# ---------- Create order ----------
@router.post("/order")
async def create_order(body: OrderIn, user: dict = Depends(get_current_user)):
    if user["role"] == "super_admin":
        raise HTTPException(400, "Super admin does not have a wallet. Use client account to recharge.")
    if not user.get("client_id"):
        raise HTTPException(400, "No tenant")
    client = await db.clients.find_one({"id": user["client_id"]}, {"_id": 0})
    if not client:
        raise HTTPException(404, "Client not found")

    rzp = _rzp_client()
    amount_paise = int(round(body.amount * 100))
    if amount_paise < 100:
        raise HTTPException(400, "Minimum recharge is ₹1")

    receipt = f"wr-{new_id()[:12]}"
    try:
        order = rzp.order.create({
            "amount": amount_paise,
            "currency": "INR",
            "receipt": receipt,
            "payment_capture": 1,
            "notes": {
                "client_id": user["client_id"],
                "client_name": client.get("name", ""),
                "user_id": user["id"],
                "purpose": "wallet_recharge",
            },
        })
    except Exception as e:
        log.error("razorpay.order.create failed: %s", e)
        raise HTTPException(502, f"Razorpay order creation failed: {e}")

    await db.payment_orders.insert_one({
        "id": new_id(),
        "order_id": order["id"],
        "receipt": receipt,
        "client_id": user["client_id"],
        "user_id": user["id"],
        "amount_inr": body.amount,
        "amount_paise": amount_paise,
        "currency": "INR",
        "status": "created",
        "payment_id": None,
        "invoice_no": None,
        "created_at": iso(now_utc()),
    })
    await log_audit(user, "payments.order.create", user["client_id"],
                    {"order_id": order["id"], "amount": body.amount})
    return {
        "order_id": order["id"],
        "amount": amount_paise,
        "currency": "INR",
        "key_id": RAZORPAY_KEY_ID,
        "receipt": receipt,
        "client_name": client.get("name", ""),
        "prefill_email": user.get("email", ""),
        "prefill_name": user.get("name", ""),
    }


def _verify_signature(order_id: str, payment_id: str, signature: str) -> bool:
    msg = f"{order_id}|{payment_id}".encode()
    expected = hmac.new(RAZORPAY_KEY_SECRET.encode(), msg, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


async def _finalize_payment(order_id: str, payment_id: str,
                            source: str) -> Optional[dict]:
    """Idempotently credit wallet for an order. Returns tx info if newly credited,
    None if already processed. `source` is 'verify' or 'webhook'."""
    po = await db.payment_orders.find_one({"order_id": order_id}, {"_id": 0})
    if not po:
        # Unknown order — record for later audit, do nothing
        log.warning("Finalize: unknown order_id=%s (source=%s)", order_id, source)
        return None
    if po.get("status") == "paid":
        log.info("Finalize: order %s already processed (source=%s)", order_id, source)
        return None

    # Generate unique GST invoice number
    base_inv = f"INV-{now_utc().strftime('%Y%m%d%H%M%S')}"
    inv_no = base_inv
    while await db.wallet_transactions.find_one({"gst_invoice_no": inv_no}):
        inv_no = f"{base_inv}-{new_id()[:4].upper()}"

    amount_inr = float(po["amount_inr"])
    gst_amount = round(amount_inr * (GST_RATE / 100) / (1 + GST_RATE / 100), 2)

    result = await wallet_credit(
        client_id=po["client_id"],
        amount=amount_inr,
        reference=f"rzp:{payment_id}",
        note=f"Razorpay recharge (order {order_id}) via {source}",
        gst_invoice_no=inv_no,
        gst_amount=gst_amount,
    )

    await db.payment_orders.update_one(
        {"order_id": order_id},
        {"$set": {
            "status": "paid",
            "payment_id": payment_id,
            "invoice_no": inv_no,
            "finalized_via": source,
            "paid_at": iso(now_utc()),
        }},
    )
    return {
        "invoice_no": inv_no,
        "balance": result["balance"],
        "amount": amount_inr,
        "gst_amount": gst_amount,
    }


# ---------- Verify ----------
@router.post("/verify")
async def verify_payment(body: VerifyIn, user: dict = Depends(get_current_user)):
    if not RAZORPAY_KEY_SECRET:
        raise HTTPException(503, "Payments not configured")

    po = await db.payment_orders.find_one({"order_id": body.razorpay_order_id}, {"_id": 0})
    if not po:
        raise HTTPException(404, "Unknown order")
    if po["client_id"] != user.get("client_id"):
        raise HTTPException(403, "Order does not belong to this tenant")

    if not _verify_signature(body.razorpay_order_id,
                             body.razorpay_payment_id,
                             body.razorpay_signature):
        await db.payment_orders.update_one(
            {"order_id": body.razorpay_order_id},
            {"$set": {"status": "signature_failed",
                      "payment_id": body.razorpay_payment_id}},
        )
        raise HTTPException(400, "Signature verification failed")

    result = await _finalize_payment(
        body.razorpay_order_id, body.razorpay_payment_id, source="verify",
    )
    if result is None:
        # Already processed — return existing invoice
        po2 = await db.payment_orders.find_one(
            {"order_id": body.razorpay_order_id}, {"_id": 0},
        ) or {}
        client = await db.clients.find_one({"id": user["client_id"]}, {"_id": 0}) or {}
        return {
            "ok": True,
            "already_processed": True,
            "invoice_no": po2.get("invoice_no"),
            "balance": float(client.get("wallet_balance", 0) or 0),
        }
    await log_audit(user, "payments.verify.success", user["client_id"],
                    {"order_id": body.razorpay_order_id,
                     "payment_id": body.razorpay_payment_id,
                     "invoice_no": result["invoice_no"]})
    return {"ok": True, **result}


# ---------- Webhook ----------
@router.post("/webhook")
async def webhook(request: Request):
    if not RAZORPAY_WEBHOOK_SECRET:
        raise HTTPException(503, "Webhook not configured")
    payload = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")
    expected = hmac.new(RAZORPAY_WEBHOOK_SECRET.encode(), payload,
                        hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(400, "Invalid webhook signature")

    data = await request.json()
    event = data.get("event", "")
    log.info("Razorpay webhook: %s", event)

    if event in ("payment.captured", "order.paid"):
        p = (data.get("payload") or {}).get("payment", {}).get("entity") or {}
        order_id = p.get("order_id")
        payment_id = p.get("id")
        if order_id and payment_id:
            await _finalize_payment(order_id, payment_id, source="webhook")
    return {"ok": True}


# ---------- GST Invoice PDF ----------
def _invoice_pdf(po: dict, client: dict, tx: dict) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4, topMargin=1.5 * cm, bottomMargin=1.5 * cm,
        leftMargin=1.5 * cm, rightMargin=1.5 * cm,
    )
    styles = getSampleStyleSheet()
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontName="Helvetica-Bold",
                        fontSize=11, spaceAfter=3, spaceBefore=10,
                        textColor=colors.HexColor("#111827"))
    body = ParagraphStyle("body", parent=styles["BodyText"], fontSize=9)
    small = ParagraphStyle("small", parent=styles["BodyText"], fontSize=8,
                           textColor=colors.HexColor("#6b7280"))

    amount = float(tx.get("amount", 0))
    gst_total = float(tx.get("gst_amount", 0))
    taxable = round(amount - gst_total, 2)
    cgst = round(gst_total / 2, 2)
    sgst = round(gst_total / 2, 2)

    story = []
    header_tbl = Table([[
        Paragraph("<b>TAX INVOICE</b><br/><font size=8 color='#6b7280'>Original for Recipient</font>", body),
        Paragraph(f"<b>{SSPL_COMPANY_NAME}</b><br/><font size=8>{SSPL_ADDRESS}</font><br/>"
                  f"<font size=8>GSTIN: {SSPL_GSTIN} · PAN: {SSPL_PAN}</font>", body),
    ]], colWidths=[6 * cm, 11 * cm])
    header_tbl.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#111827")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#f3f4f6")),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#d1d5db")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(header_tbl)
    story.append(Spacer(1, 0.4 * cm))

    meta_tbl = Table([
        ["Invoice No.", tx.get("gst_invoice_no", "—"),
         "Invoice Date", (tx.get("created_at", "") or "")[:10]],
        ["Payment ID", po.get("payment_id", "—"),
         "Order ID", po.get("order_id", "—")],
        ["Place of Supply", f"State code {SSPL_STATE_CODE}",
         "HSN/SAC", SSPL_HSN_CODE],
    ], colWidths=[3.2 * cm, 5.3 * cm, 3.2 * cm, 5.3 * cm])
    meta_tbl.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#d1d5db")),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f9fafb")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#f9fafb")),
    ]))
    story.append(meta_tbl)

    story.append(Paragraph("Billed To", h2))
    billed = Table([[
        Paragraph(f"<b>{client.get('name', '—')}</b><br/>"
                  f"<font size=8>GSTIN: {client.get('gstin') or '—'}</font><br/>"
                  f"<font size=8>Industry: {client.get('industry', '—')}</font>", body),
    ]], colWidths=[17 * cm])
    billed.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.3, colors.HexColor("#d1d5db")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(billed)

    story.append(Paragraph("Items", h2))
    items = Table([
        ["Description", "HSN", "Qty", "Rate", "Taxable", "CGST 9%", "SGST 9%", "Total"],
        [
            Paragraph("Fire Compliance OS — Wallet Recharge (prepaid platform credits)", body),
            SSPL_HSN_CODE, "1", f"₹{taxable:.2f}", f"₹{taxable:.2f}",
            f"₹{cgst:.2f}", f"₹{sgst:.2f}", f"₹{amount:.2f}",
        ],
    ], colWidths=[5.5 * cm, 1.5 * cm, 1 * cm, 1.8 * cm, 2 * cm, 1.8 * cm, 1.8 * cm, 1.6 * cm])
    items.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#d1d5db")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(items)

    story.append(Spacer(1, 0.4 * cm))
    totals = Table([
        ["Taxable Value", f"₹{taxable:.2f}"],
        ["CGST @ 9%", f"₹{cgst:.2f}"],
        ["SGST @ 9%", f"₹{sgst:.2f}"],
        ["Total (incl. GST)", f"₹{amount:.2f}"],
    ], colWidths=[4 * cm, 3 * cm])
    totals.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#d1d5db")),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#111827")),
        ("TEXTCOLOR", (0, -1), (-1, -1), colors.white),
    ]))
    wrap = Table([[Paragraph(" ", body), totals]], colWidths=[10 * cm, 7 * cm])
    wrap.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(wrap)

    story.append(Spacer(1, 0.6 * cm))
    story.append(Paragraph(
        "This is a computer-generated tax invoice under GST Act, 2017. "
        "No signature required.", small,
    ))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        f"For {SSPL_COMPANY_NAME} · Authorised Signatory (digital)", small,
    ))

    doc.build(story)
    pdf = buf.getvalue()
    buf.close()
    return pdf


@router.get("/invoice/{invoice_no}")
async def download_invoice(invoice_no: str, user: dict = Depends(get_current_user)):
    tx = await db.wallet_transactions.find_one(
        {"gst_invoice_no": invoice_no}, {"_id": 0},
    )
    if not tx:
        raise HTTPException(404, "Invoice not found")
    # RBAC: super_admin or same tenant only
    if user["role"] != "super_admin" and tx.get("client_id") != user.get("client_id"):
        raise HTTPException(403, "Forbidden")
    client = await db.clients.find_one({"id": tx["client_id"]}, {"_id": 0}) or {}
    po = await db.payment_orders.find_one({"invoice_no": invoice_no}, {"_id": 0}) or {}
    pdf = _invoice_pdf(po, client, tx)
    filename = f"invoice-{invoice_no}.pdf"
    return Response(
        content=pdf, media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ---------- Orders history (for admin/debug) ----------
@router.get("/orders")
async def list_orders(user: dict = Depends(get_current_user)):
    q = {} if user["role"] == "super_admin" else {"client_id": user.get("client_id")}
    orders = await db.payment_orders.find(q, {"_id": 0}).sort("created_at", -1).to_list(200)
    return orders


@router.get("/admin/orders")
async def admin_list_orders(user: dict = Depends(require_role("super_admin"))):
    return await db.payment_orders.find({}, {"_id": 0}).sort("created_at", -1).to_list(500)
