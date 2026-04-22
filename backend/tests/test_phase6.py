"""Phase-6 backend tests — payments, password reset, documents, messaging."""
import io
import os
import re
import hashlib
import pytest
import requests
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv("/app/backend/.env")
BASE = os.environ["REACT_APP_BACKEND_URL"].rstrip("/") if os.environ.get("REACT_APP_BACKEND_URL") else \
       os.environ.get("FRONTEND_URL", "https://fire-safety-engine.preview.emergentagent.com").rstrip("/")
# Use backend URL from frontend .env
with open("/app/frontend/.env") as f:
    for ln in f:
        if ln.startswith("REACT_APP_BACKEND_URL"):
            BASE = ln.split("=", 1)[1].strip().strip('"').rstrip("/")
API = f"{BASE}/api"

ADMIN = {"email": "admin@acme.in", "password": "Acme@12345"}
SUPER = {"email": "superadmin@sspl.in", "password": "Sspl@12345"}
TECH = {"email": "tech@acme.in", "password": "Tech@12345"}


def _login(cred):
    s = requests.Session()
    r = s.post(f"{API}/auth/login", json=cred, timeout=20)
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text}"
    return s


@pytest.fixture(scope="module")
def admin():
    return _login(ADMIN)


@pytest.fixture(scope="module")
def superadmin():
    return _login(SUPER)


# ==================== PAYMENTS ====================
class TestPayments:
    def test_config_unconfigured(self, admin):
        r = admin.get(f"{API}/payments/config")
        assert r.status_code == 200
        d = r.json()
        assert "key_id" in d and "configured" in d and "gst_rate" in d
        # env currently has empty RAZORPAY_KEY_ID -> configured=False
        assert d["configured"] is False
        assert float(d["gst_rate"]) == 18.0

    def test_order_503_when_unconfigured(self, admin):
        r = admin.post(f"{API}/payments/order", json={"amount": 100})
        assert r.status_code == 503, f"expected 503 got {r.status_code} {r.text}"

    def test_order_rejects_super_admin(self, superadmin):
        r = superadmin.post(f"{API}/payments/order", json={"amount": 100})
        assert r.status_code == 400

    def test_verify_unknown_order(self, admin):
        r = admin.post(f"{API}/payments/verify", json={
            "razorpay_order_id": "order_nonexistent_xxxx",
            "razorpay_payment_id": "pay_xxx", "razorpay_signature": "x" * 64,
        })
        # 503 (secret missing) OR 404 (unknown order). Both acceptable as unconfigured.
        assert r.status_code in (503, 404)

    def test_invoice_not_found(self, admin):
        r = admin.get(f"{API}/payments/invoice/INV-DOES-NOT-EXIST")
        assert r.status_code == 404

    def test_orders_list_tenant_scoped(self, admin, superadmin):
        r = admin.get(f"{API}/payments/orders")
        assert r.status_code == 200
        admin_orders = r.json()
        assert isinstance(admin_orders, list)
        # All orders in admin response must belong to admin's tenant
        me = admin.get(f"{API}/auth/me").json()
        for o in admin_orders:
            assert o.get("client_id") == me.get("client_id")

        r2 = superadmin.get(f"{API}/payments/orders")
        assert r2.status_code == 200
        assert isinstance(r2.json(), list)


# ==================== PASSWORD RESET ====================
class TestPasswordReset:
    def test_request_nonexistent_email_returns_200(self):
        r = requests.post(f"{API}/auth/password-reset/request",
                          json={"email": "nobody-phase6@example.com"}, timeout=20)
        assert r.status_code == 200
        assert r.json().get("ok") is True

    def test_request_existing_email_returns_200(self):
        r = requests.post(f"{API}/auth/password-reset/request",
                          json={"email": ADMIN["email"]}, timeout=20)
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_reset_token_written_and_confirm_flow(self):
        mongo = AsyncIOMotorClient(os.environ["MONGO_URL"])
        db = mongo[os.environ["DB_NAME"]]
        try:
            # Request reset
            requests.post(f"{API}/auth/password-reset/request",
                          json={"email": ADMIN["email"]}, timeout=20)
            # Admin user
            user = await db.users.find_one({"email": ADMIN["email"]}, {"_id": 0})
            assert user is not None

            # Confirm token doc was written with hash + expires_at
            tok = await db.password_reset_tokens.find_one({"user_id": user["id"]}, {"_id": 0})
            assert tok is not None, "password_reset_tokens must have entry"
            assert tok.get("token_hash") and len(tok["token_hash"]) == 64
            assert tok.get("expires_at") is not None
            assert tok.get("used") is False

            # email_log written (log_only since Resend/SMTP unconfigured)
            em = await db.email_log.find_one(
                {"to": {"$in": [[ADMIN["email"]], ADMIN["email"]]}},
                sort=[("created_at", -1)],
            )
            assert em is not None, "email_log must record attempt"
            assert em.get("provider") in ("log_only", "resend", "smtp")

            # ---- Invalid token ----
            r = requests.post(f"{API}/auth/password-reset/confirm",
                              json={"token": "bogus_token_xxxxx",
                                    "new_password": "NewPass@123"}, timeout=20)
            assert r.status_code == 400

            # ---- Expired token ----
            from datetime import datetime, timezone, timedelta
            import secrets as _secrets
            raw_expired = _secrets.token_urlsafe(48)
            await db.password_reset_tokens.insert_one({
                "id": "expired-test", "user_id": user["id"],
                "email": user["email"],
                "token_hash": hashlib.sha256(raw_expired.encode()).hexdigest(),
                "expires_at": datetime.now(timezone.utc) - timedelta(hours=1),
                "used": False, "created_at": "2020-01-01T00:00:00+00:00",
            })
            r = requests.post(f"{API}/auth/password-reset/confirm",
                              json={"token": raw_expired,
                                    "new_password": "NewPass@123"}, timeout=20)
            assert r.status_code == 400
            await db.password_reset_tokens.delete_one({"id": "expired-test"})

            # ---- Valid flow ----
            # Force-create a fresh valid token
            raw_valid = _secrets.token_urlsafe(48)
            await db.password_reset_tokens.delete_many({"user_id": user["id"]})
            await db.password_reset_tokens.insert_one({
                "id": "valid-test", "user_id": user["id"],
                "email": user["email"],
                "token_hash": hashlib.sha256(raw_valid.encode()).hexdigest(),
                "expires_at": datetime.now(timezone.utc) + timedelta(hours=1),
                "used": False, "created_at": "2026-01-01T00:00:00+00:00",
            })
            new_pw = "TempReset@99999"
            r = requests.post(f"{API}/auth/password-reset/confirm",
                              json={"token": raw_valid, "new_password": new_pw}, timeout=20)
            assert r.status_code == 200, f"confirm failed: {r.text}"

            # Token marked used
            t2 = await db.password_reset_tokens.find_one({"id": "valid-test"}, {"_id": 0})
            assert t2 is not None and t2.get("used") is True

            # User can login with new password
            r = requests.post(f"{API}/auth/login",
                              json={"email": ADMIN["email"], "password": new_pw}, timeout=20)
            assert r.status_code == 200, f"login with new pw failed: {r.text}"

            # Restore password
            raw_restore = _secrets.token_urlsafe(48)
            await db.password_reset_tokens.insert_one({
                "id": "restore-test", "user_id": user["id"],
                "email": user["email"],
                "token_hash": hashlib.sha256(raw_restore.encode()).hexdigest(),
                "expires_at": datetime.now(timezone.utc) + timedelta(hours=1),
                "used": False, "created_at": "2026-01-01T00:00:00+00:00",
            })
            r = requests.post(f"{API}/auth/password-reset/confirm",
                              json={"token": raw_restore,
                                    "new_password": "Acme@12345"}, timeout=20)
            assert r.status_code == 200

            # Verify restored
            r = requests.post(f"{API}/auth/login", json=ADMIN, timeout=20)
            assert r.status_code == 200, "admin must still login with Acme@12345"
        finally:
            mongo.close()


# ==================== DOCUMENTS ====================
class TestDocuments:
    def test_upload_local_fallback(self, admin):
        files = {"file": ("sample.txt", io.BytesIO(b"hello phase6 test"), "text/plain")}
        data = {"title": "TEST_Phase6_Doc", "doc_type": "other"}
        r = admin.post(f"{API}/documents/upload", files=files, data=data, timeout=30)
        assert r.status_code == 200, f"upload failed: {r.text}"
        d = r.json()
        assert d.get("storage_provider") == "local"
        assert d.get("storage_key")
        assert d.get("storage_location")
        assert d.get("file_size") == len(b"hello phase6 test")
        TestDocuments._doc_id = d["id"]

    def test_upload_blocked_for_super_admin(self, superadmin):
        files = {"file": ("sample.txt", io.BytesIO(b"x"), "text/plain")}
        data = {"title": "TEST_super", "doc_type": "other"}
        r = superadmin.post(f"{API}/documents/upload", files=files, data=data, timeout=20)
        assert r.status_code == 403

    def test_download_local(self, admin):
        doc_id = getattr(TestDocuments, "_doc_id", None)
        assert doc_id, "upload test must run first"
        r = admin.get(f"{API}/documents/file/{doc_id}", timeout=20)
        assert r.status_code == 200
        assert b"hello phase6 test" in r.content

    def test_download_nonexistent(self, admin):
        r = admin.get(f"{API}/documents/file/nonexistent-id-xxx", timeout=20)
        assert r.status_code == 404

    def test_list_tenant_scoped(self, admin):
        r = admin.get(f"{API}/documents", timeout=20)
        assert r.status_code == 200
        assert isinstance(r.json(), list)


# ==================== MESSAGING ====================
class TestMessaging:
    def test_norm_phone_numbers(self):
        from sys import path as _p
        _p.insert(0, "/app/backend")
        from core.messaging import _norm
        assert _norm("+919876543210") == "+919876543210"
        assert _norm("9876543210") == "+919876543210"
        assert _norm("919876543210") == "+919876543210"
        assert _norm("98765-43210") == "+919876543210"
        assert _norm("") is None
        assert _norm(None) is None
        assert _norm("abc") is None
        assert _norm("12345") is None
        assert _norm("+91 98765 43210") == "+919876543210"

    @pytest.mark.asyncio
    async def test_send_critical_alert_graceful_when_unconfigured(self):
        from sys import path as _p
        _p.insert(0, "/app/backend")
        from core.messaging import send_critical_alert
        res = await send_critical_alert(
            phones=["+919876543210", "9123456789"],
            event="inspection_fail",
            variables_list=["A", "B"],
            variables_map={"var1": "A", "var2": "B"},
        )
        assert "skipped" in res
        # Both phones should be in skipped since both WA+SMS unconfigured
        assert len(res["skipped"]) == 2
        assert res["whatsapp"] == []
        assert res["sms"] == []


# ==================== REGRESSION ====================
class TestRegression:
    def test_me_and_wallet(self, admin):
        r = admin.get(f"{API}/auth/me")
        assert r.status_code == 200
        r = admin.get(f"{API}/wallet")
        assert r.status_code == 200
        assert "balance" in r.json()

    def test_assets(self, admin):
        r = admin.get(f"{API}/assets")
        assert r.status_code == 200

    def test_inspections(self, admin):
        r = admin.get(f"{API}/inspections")
        assert r.status_code == 200

    def test_compliance_score(self, admin):
        r = admin.get(f"{API}/compliance/score")
        assert r.status_code == 200

    def test_notifications(self, admin):
        r = admin.get(f"{API}/notifications")
        assert r.status_code == 200


# ==================== DB INDEXES ====================
class TestIndexes:
    @pytest.mark.asyncio
    async def test_indexes_exist(self):
        mongo = AsyncIOMotorClient(os.environ["MONGO_URL"])
        db = mongo[os.environ["DB_NAME"]]
        try:
            # payment_orders.order_id unique
            idx = await db.payment_orders.index_information()
            found_unique = any(
                spec.get("unique") and any(k[0] == "order_id" for k in spec.get("key", []))
                for spec in idx.values()
            )
            assert found_unique, f"payment_orders.order_id must have unique index. Got: {idx}"

            # messaging_log exists (any index implies collection initialized)
            ml_idx = await db.messaging_log.index_information()
            assert ml_idx  # At minimum _id_ exists once collection has records OR indexes

            el_idx = await db.email_log.index_information()
            assert el_idx
        finally:
            mongo.close()
