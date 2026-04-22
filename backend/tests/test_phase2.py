"""Phase-2 stabilization & revenue enablement tests.

Covers six tasks:
1. Wallet deduction (asset/inspection/user)
2. Grace mode (balance<=0 -> 402; reads still 200)
3. Low-balance + exhausted notifications
4. Email log-only fallback
5. Document upload/download + isolation + size limit
6. Logout token revocation (access + refresh)
7. Super admin /admin/overview revenue tiles
"""
import os
import io
import time
import pytest
import requests
from pymongo import MongoClient

BASE_URL = os.environ["REACT_APP_BACKEND_URL"].rstrip("/")
API = f"{BASE_URL}/api"

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]

SUPER = ("superadmin@sspl.in", "Sspl@12345")
ADMIN = ("admin@acme.in", "Acme@12345")
OFFICER = ("officer@acme.in", "Officer@123")
TECH = ("tech@acme.in", "Tech@12345")


# ---------- helpers ----------
def _login(email, password):
    s = requests.Session()
    r = s.post(f"{API}/auth/login", json={"email": email, "password": password}, timeout=20)
    assert r.status_code == 200, f"login {email}: {r.status_code} {r.text}"
    return s


@pytest.fixture(scope="session")
def mongo():
    cli = MongoClient(MONGO_URL)
    return cli[DB_NAME]


@pytest.fixture(scope="session")
def super_session():
    return _login(*SUPER)


@pytest.fixture(scope="session")
def acme_client_id(mongo):
    c = mongo.clients.find_one({"name": "Acme Industries"})
    assert c, "Acme not seeded"
    return c["id"]


def set_balance(mongo, cid, bal):
    mongo.clients.update_one({"id": cid}, {"$set": {"wallet_balance": float(bal)}})


def get_balance(mongo, cid):
    c = mongo.clients.find_one({"id": cid})
    return float(c.get("wallet_balance", 0))


def ensure_acme_site(admin_sess, mongo, acme_client_id):
    s = mongo.sites.find_one({"client_id": acme_client_id})
    if s:
        return s["id"]
    r = admin_sess.post(f"{API}/sites", json={"name": "TEST_Phase2_Site", "address": "x"})
    assert r.status_code == 200
    return r.json()["id"]


# ---------- 1. Wallet deduction on asset/inspection/user ----------
class TestWalletDeduction:
    def test_asset_charge_10(self, mongo, acme_client_id):
        set_balance(mongo, acme_client_id, 10000)
        s = _login(*ADMIN)
        site_id = ensure_acme_site(s, mongo, acme_client_id)
        before = get_balance(mongo, acme_client_id)
        r = s.post(f"{API}/assets", json={
            "site_id": site_id, "name": "TEST_P2_Asset_A",
            "category": "extinguisher", "expiry_date": "2027-01-01",
        })
        assert r.status_code == 200, r.text
        body = r.json()
        wc = body.get("wallet_charge")
        assert wc and wc["cost"] == 10
        assert wc["balance_after"] == round(before - 10, 2)
        assert "Asset" in wc["reason"]
        # Tx record
        tx = mongo.wallet_transactions.find_one({"reference": body["id"]})
        assert tx and tx["type"] == "usage" and tx["amount"] == -10
        assert tx["balance_after"] == round(before - 10, 2)
        assert "TEST_P2_Asset_A" in tx["reason"]

    def test_inspection_charge_5(self, mongo, acme_client_id):
        set_balance(mongo, acme_client_id, 10000)
        s = _login(*ADMIN)
        site_id = ensure_acme_site(s, mongo, acme_client_id)
        a = s.post(f"{API}/assets", json={
            "site_id": site_id, "name": "TEST_P2_Asset_Insp",
            "category": "extinguisher", "expiry_date": "2027-01-01"}).json()
        before = get_balance(mongo, acme_client_id)
        r = s.post(f"{API}/inspections", json={
            "asset_id": a["id"], "checklist": [{"q": "ok", "v": True}],
            "overall_result": "pass", "inspector_name": "T"})
        assert r.status_code == 200, r.text
        body = r.json()
        wc = body["wallet_charge"]
        assert wc["cost"] == 5
        assert wc["balance_after"] == round(before - 5, 2)
        tx = mongo.wallet_transactions.find_one({"reference": body["id"]})
        assert tx and tx["type"] == "usage" and tx["amount"] == -5
        assert "Inspection" in tx["reason"] and "TEST_P2_Asset_Insp" in tx["reason"]

    def test_user_charge_20(self, mongo, acme_client_id):
        set_balance(mongo, acme_client_id, 10000)
        s = _login(*ADMIN)
        before = get_balance(mongo, acme_client_id)
        email = f"test_p2_user_{int(time.time())}@acme.in"
        r = s.post(f"{API}/users", json={
            "email": email, "password": "Pass@1234",
            "name": "Test User", "role": "fire_officer"})
        assert r.status_code == 200, r.text
        body = r.json()
        wc = body["wallet_charge"]
        assert wc["cost"] == 20
        assert wc["balance_after"] == round(before - 20, 2)
        tx = mongo.wallet_transactions.find_one({"reference": body["id"]})
        assert tx and tx["amount"] == -20 and email in tx["reason"]


# ---------- 2. Grace mode ----------
class TestGraceMode:
    def test_grace_blocks_writes_allows_reads(self, mongo, acme_client_id):
        set_balance(mongo, acme_client_id, 0)
        s = _login(*ADMIN)
        site_id = ensure_acme_site(s, mongo, acme_client_id)
        # writes blocked
        r1 = s.post(f"{API}/assets", json={
            "site_id": site_id, "name": "TEST_NOOP", "category": "extinguisher"})
        assert r1.status_code == 402
        assert "Wallet exhausted" in r1.json()["detail"]
        assert "read-only" in r1.json()["detail"]
        # asset id required for inspection -- pick any acme asset; create dummy via mongo to be safe
        a = mongo.assets.find_one({"client_id": acme_client_id})
        if a:
            r2 = s.post(f"{API}/inspections", json={
                "asset_id": a["id"], "checklist": [], "overall_result": "pass",
                "inspector_name": "x"})
            assert r2.status_code == 402
        r3 = s.post(f"{API}/users", json={
            "email": f"blocked_{int(time.time())}@acme.in", "password": "x12345",
            "name": "x", "role": "fire_officer"})
        assert r3.status_code == 402
        # reads still ok
        for ep in ["/assets", "/inspections", "/users", "/sites", "/wallet"]:
            rr = s.get(f"{API}{ep}")
            assert rr.status_code == 200, f"{ep} -> {rr.status_code}"


# ---------- 3. Low + exhausted notifications ----------
class TestLowBalanceNotifications:
    def test_low_threshold_notification(self, mongo, acme_client_id):
        set_balance(mongo, acme_client_id, 520)
        # Mark existing wallet_low notifications as read to identify new ones via timestamp
        from datetime import datetime, timezone
        marker = datetime.now(timezone.utc).isoformat()
        s = _login(*ADMIN)
        site_id = ensure_acme_site(s, mongo, acme_client_id)
        # 3 assets: 520 -> 510 -> 500 -> 490 (crosses threshold on the third)
        for i in range(3):
            r = s.post(f"{API}/assets", json={
                "site_id": site_id, "name": f"TEST_LOW_{i}_{int(time.time())}",
                "category": "extinguisher"})
            assert r.status_code == 200, r.text
        # Now check notifications collection for wallet_low generated post-marker
        n = mongo.notifications.find_one({
            "kind": "wallet_low", "created_at": {"$gte": marker}})
        assert n, "wallet_low notification not generated"

    def test_exhausted_notification(self, mongo, acme_client_id):
        set_balance(mongo, acme_client_id, 5)
        from datetime import datetime, timezone
        marker = datetime.now(timezone.utc).isoformat()
        s = _login(*ADMIN)
        site_id = ensure_acme_site(s, mongo, acme_client_id)
        r = s.post(f"{API}/assets", json={
            "site_id": site_id, "name": f"TEST_EXH_{int(time.time())}",
            "category": "extinguisher"})
        # 5 - 10 = -5 -> still proceeds because balance>0 at start
        assert r.status_code == 200, r.text
        bal = get_balance(mongo, acme_client_id)
        assert bal < 0
        n = mongo.notifications.find_one({
            "kind": "wallet_exhausted", "created_at": {"$gte": marker}})
        assert n, "wallet_exhausted notification not generated"


# ---------- 4. Email log-only fallback ----------
class TestEmailFallback:
    def test_resend_key_empty(self):
        from dotenv import dotenv_values
        v = dotenv_values("/app/backend/.env")
        assert (v.get("RESEND_API_KEY") or "").strip('"').strip() == "", \
            "RESEND_API_KEY must be empty for log-only fallback test"

    def test_inspection_fail_logs_email(self, mongo, acme_client_id):
        set_balance(mongo, acme_client_id, 10000)
        s = _login(*ADMIN)
        site_id = ensure_acme_site(s, mongo, acme_client_id)
        a = s.post(f"{API}/assets", json={
            "site_id": site_id, "name": "TEST_EMAIL_FAIL",
            "category": "extinguisher"}).json()
        # Capture log size before
        log_path = "/var/log/supervisor/backend.err.log"
        before_size = os.path.getsize(log_path) if os.path.exists(log_path) else 0
        # Trigger fail inspection
        r = s.post(f"{API}/inspections", json={
            "asset_id": a["id"], "checklist": [{"q": "x", "v": False}],
            "overall_result": "fail", "inspector_name": "Insp", "notes": "bad"})
        assert r.status_code == 200, r.text
        time.sleep(1)
        after = b""
        for p in ["/var/log/supervisor/backend.err.log", "/var/log/supervisor/backend.out.log"]:
            if os.path.exists(p):
                with open(p, "rb") as f:
                    f.seek(max(0, before_size - 1024))
                    after += f.read()
        assert b"[EMAIL:log-only]" in after
        assert b"Inspection FAILED" in after


# ---------- 5. Document upload/download/isolation/size ----------
class TestDocuments:
    def test_upload_list_download(self, mongo, acme_client_id):
        s = _login(*ADMIN)
        content = b"hello-fire-os-phase2-document-bytes"
        files = {"file": ("test_doc.txt", io.BytesIO(content), "text/plain")}
        data = {"title": "TEST_P2_Doc", "doc_type": "noc"}
        r = s.post(f"{API}/documents/upload", files=files, data=data)
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["file_name"] == "test_doc.txt"
        assert body["file_size"] == len(content)
        assert body["file_path"].startswith(f"/app/backend/uploads/{acme_client_id}")
        doc_id = body["id"]
        # GET list
        lst = s.get(f"{API}/documents").json()
        assert any(d["id"] == doc_id for d in lst)
        # download
        dl = s.get(f"{API}/documents/file/{doc_id}")
        assert dl.status_code == 200
        assert dl.content == content
        return doc_id

    def test_isolation_other_tenant_404(self, mongo, super_session, acme_client_id):
        # Upload an acme doc
        s = _login(*ADMIN)
        files = {"file": ("iso.txt", io.BytesIO(b"acme-iso"), "text/plain")}
        r = s.post(f"{API}/documents/upload",
                   files=files, data={"title": "TEST_ISO", "doc_type": "noc"})
        acme_doc_id = r.json()["id"]
        # Create a Beta tenant + admin via super_admin
        beta_email = f"beta_admin_p2_{int(time.time())}@beta.in"
        cr = super_session.post(f"{API}/admin/clients", json={
            "name": f"TEST_BetaP2_{int(time.time())}", "industry": "x",
            "subscription_plan": "basic",
            "admin_email": beta_email, "admin_password": "Beta@12345",
            "admin_name": "Beta Admin"})
        assert cr.status_code == 200
        # Beta tries to download acme doc
        bs = _login(beta_email, "Beta@12345")
        r2 = bs.get(f"{API}/documents/file/{acme_doc_id}")
        assert r2.status_code == 404

    def test_size_limit_413(self):
        s = _login(*ADMIN)
        big = b"x" * (26 * 1024 * 1024)  # 26 MB
        files = {"file": ("big.bin", io.BytesIO(big), "application/octet-stream")}
        r = s.post(f"{API}/documents/upload",
                   files=files, data={"title": "TEST_BIG", "doc_type": "other"},
                   timeout=120)
        assert r.status_code == 413, f"got {r.status_code}: {r.text[:200]}"


# ---------- 6. Logout token revocation ----------
class TestLogoutRevocation:
    def test_access_token_revoked(self, mongo):
        s = _login(*ADMIN)
        # me works
        assert s.get(f"{API}/auth/me").status_code == 200
        access_cookie = s.cookies.get("access_token")
        refresh_cookie = s.cookies.get("refresh_token")
        # logout
        r = s.post(f"{API}/auth/logout")
        assert r.status_code == 200
        # use the OLD access_token cookie via fresh session
        s2 = requests.Session()
        s2.cookies.set("access_token", access_cookie,
                       domain=BASE_URL.split("://", 1)[1])
        r2 = s2.get(f"{API}/auth/me")
        assert r2.status_code == 401
        assert "Session revoked" in r2.json().get("detail", "")
        # refresh also revoked
        s3 = requests.Session()
        s3.cookies.set("refresh_token", refresh_cookie,
                       domain=BASE_URL.split("://", 1)[1])
        r3 = s3.post(f"{API}/auth/refresh")
        assert r3.status_code == 401
        # DB has the JTIs
        import jwt as _jwt
        payload = _jwt.decode(access_cookie, options={"verify_signature": False})
        rev = mongo.revoked_tokens.find_one({"jti": payload["jti"]})
        assert rev and rev.get("expires_at")


# ---------- 7. Super admin overview revenue ----------
class TestAdminOverview:
    def test_overview_shape(self, super_session, mongo):
        r = super_session.get(f"{API}/admin/overview")
        assert r.status_code == 200, r.text
        d = r.json()
        for k in ["total_revenue", "total_usage", "total_transactions",
                  "total_credit_transactions", "total_usage_transactions",
                  "wallets_by_client", "recent_transactions"]:
            assert k in d, f"missing {k}"
        assert isinstance(d["wallets_by_client"], list)
        assert isinstance(d["recent_transactions"], list)
        assert len(d["recent_transactions"]) <= 10
        for t in d["recent_transactions"]:
            assert "client_name" in t and "type" in t and "amount" in t
        # Cross-check totals against mongo
        credit = list(mongo.wallet_transactions.aggregate(
            [{"$match": {"type": "credit"}}, {"$group": {"_id": None, "s": {"$sum": "$amount"}, "c": {"$sum": 1}}}]))
        usage = list(mongo.wallet_transactions.aggregate(
            [{"$match": {"type": "usage"}}, {"$group": {"_id": None, "s": {"$sum": "$amount"}, "c": {"$sum": 1}}}]))
        exp_rev = float(credit[0]["s"]) if credit else 0.0
        exp_usage = abs(float(usage[0]["s"])) if usage else 0.0
        assert abs(d["total_revenue"] - exp_rev) < 0.01
        assert abs(d["total_usage"] - exp_usage) < 0.01


# ---------- Reset Acme balance after test run ----------
@pytest.fixture(autouse=True, scope="module")
def _reset_balance_after():
    yield
    cli = MongoClient(MONGO_URL)
    cli[DB_NAME].clients.update_one({"name": "Acme Industries"},
                                    {"$set": {"wallet_balance": 10000.0}})
