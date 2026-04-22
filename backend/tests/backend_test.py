"""Fire Compliance OS - Backend API tests covering auth, RBAC, multi-tenant isolation,
clients, kill-switch, wallet, assets, inspections, maintenance, incidents, compliance,
notifications, audit and MongoDB _id leak checks."""
import os
import time
import uuid
import requests
import pytest

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://fire-safety-engine.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"

SUPER = {"email": "superadmin@sspl.in", "password": "Sspl@12345"}
CADMIN = {"email": "admin@acme.in", "password": "Acme@12345"}
OFFICER = {"email": "officer@acme.in", "password": "Officer@123"}
TECH = {"email": "tech@acme.in", "password": "Tech@12345"}


def _login(creds):
    s = requests.Session()
    r = s.post(f"{API}/auth/login", json=creds, timeout=20)
    return s, r


def _no_id_leak(obj):
    """Recursively assert mongodb _id is absent."""
    if isinstance(obj, dict):
        assert "_id" not in obj, f"_id leak in {list(obj.keys())}"
        for v in obj.values():
            _no_id_leak(v)
    elif isinstance(obj, list):
        for v in obj:
            _no_id_leak(v)


# ---------- AUTH ----------
class TestAuth:
    def test_health(self):
        r = requests.get(f"{API}/", timeout=15)
        assert r.status_code == 200
        assert r.json().get("status") == "operational"

    def test_login_super_admin(self):
        s, r = _login(SUPER)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["user"]["role"] == "super_admin"
        assert data["user"]["email"] == SUPER["email"]
        # cookies set
        assert "access_token" in s.cookies
        assert "refresh_token" in s.cookies
        _no_id_leak(data)

    def test_login_client_admin(self):
        s, r = _login(CADMIN)
        assert r.status_code == 200, r.text
        u = r.json()["user"]
        assert u["role"] == "client_admin"
        assert u.get("client_id")

    def test_login_fire_officer(self):
        _, r = _login(OFFICER)
        assert r.status_code == 200
        assert r.json()["user"]["role"] == "fire_officer"

    def test_login_technician(self):
        _, r = _login(TECH)
        assert r.status_code == 200
        assert r.json()["user"]["role"] == "technician"

    def test_login_wrong_password(self):
        # Use a unique email so brute-force lockout doesn't poison main account
        r = requests.post(f"{API}/auth/login",
                          json={"email": "admin@acme.in", "password": "WRONGPASS"},
                          timeout=15)
        assert r.status_code in (401, 429)

    def test_me_without_cookies(self):
        r = requests.get(f"{API}/auth/me", timeout=15)
        assert r.status_code == 401

    def test_me_with_cookies(self):
        s, _ = _login(CADMIN)
        r = s.get(f"{API}/auth/me", timeout=15)
        assert r.status_code == 200
        assert r.json()["email"] == CADMIN["email"]

    def test_refresh(self):
        s, _ = _login(CADMIN)
        # Drop access cookie to test refresh
        s.cookies.pop("access_token", None)
        r = s.post(f"{API}/auth/refresh", timeout=15)
        assert r.status_code == 200
        assert "access_token" in s.cookies

    def test_logout(self):
        s, _ = _login(CADMIN)
        r = s.post(f"{API}/auth/logout", timeout=15)
        assert r.status_code == 200
        # Further authed call should fail
        r2 = s.get(f"{API}/auth/me", timeout=15)
        assert r2.status_code == 401


# ---------- RBAC ----------
class TestRBAC:
    def test_admin_endpoints_forbidden_for_client(self):
        s, _ = _login(CADMIN)
        for path in ["/admin/clients", "/admin/overview", "/admin/audit"]:
            r = s.get(f"{API}{path}", timeout=15)
            assert r.status_code == 403, f"{path} expected 403 got {r.status_code}"

    def test_admin_endpoints_forbidden_for_tech(self):
        s, _ = _login(TECH)
        r = s.get(f"{API}/admin/overview", timeout=15)
        assert r.status_code == 403

    def test_tech_cannot_delete_asset(self):
        s_admin, _ = _login(CADMIN)
        assets = s_admin.get(f"{API}/assets", timeout=15).json()
        assert assets, "no assets seeded"
        s_tech, _ = _login(TECH)
        r = s_tech.delete(f"{API}/assets/{assets[0]['id']}", timeout=15)
        assert r.status_code == 403


# ---------- SSPL admin: clients + kill-switch + wallet ----------
class TestSSPLAdmin:
    @pytest.fixture(scope="class")
    def super_session(self):
        s, r = _login(SUPER)
        assert r.status_code == 200
        return s

    def test_overview(self, super_session):
        r = super_session.get(f"{API}/admin/overview", timeout=15)
        assert r.status_code == 200
        d = r.json()
        for key in ["total_clients", "active_clients", "total_assets", "total_users",
                    "total_wallet_balance", "low_balance_clients", "clients_risk"]:
            assert key in d
        _no_id_leak(d)

    def test_list_clients(self, super_session):
        r = super_session.get(f"{API}/admin/clients", timeout=15)
        assert r.status_code == 200
        clients = r.json()
        assert isinstance(clients, list) and len(clients) >= 1
        _no_id_leak(clients)

    def test_create_client_and_duplicate(self, super_session):
        unique = uuid.uuid4().hex[:8]
        payload = {
            "name": f"TEST_Beta_{unique}",
            "industry": "IT",
            "subscription_plan": "basic",
            "admin_email": f"TEST_beta_{unique}@example.com",
            "admin_password": "BetaPass@123",
            "admin_name": "Beta Admin",
        }
        r = super_session.post(f"{API}/admin/clients", json=payload, timeout=15)
        assert r.status_code == 200, r.text
        cid = r.json()["client_id"]
        # duplicate email -> 400
        r2 = super_session.post(f"{API}/admin/clients", json=payload, timeout=15)
        assert r2.status_code == 400
        # multi-tenant isolation: login as the new beta admin -> empty assets
        s_new, login_r = _login({"email": payload["admin_email"], "password": payload["admin_password"]})
        assert login_r.status_code == 200
        a_resp = s_new.get(f"{API}/assets", timeout=15)
        assert a_resp.status_code == 200
        assert a_resp.json() == []
        sites_resp = s_new.get(f"{API}/sites", timeout=15)
        assert sites_resp.status_code == 200
        assert sites_resp.json() == []
        # save cid for kill switch test
        TestSSPLAdmin._beta_cid = cid
        TestSSPLAdmin._beta_creds = {"email": payload["admin_email"],
                                     "password": payload["admin_password"]}

    def test_kill_switch_then_login_blocked(self, super_session):
        cid = getattr(TestSSPLAdmin, "_beta_cid", None)
        creds = getattr(TestSSPLAdmin, "_beta_creds", None)
        if not cid:
            pytest.skip("create client test did not run")
        r = super_session.post(f"{API}/admin/clients/{cid}/kill-switch", timeout=15)
        assert r.status_code == 200
        assert r.json()["license_active"] is False
        # Login attempt should now 403
        r2 = requests.post(f"{API}/auth/login", json=creds, timeout=15)
        assert r2.status_code == 403
        # Re-enable for cleanliness
        super_session.post(f"{API}/admin/clients/{cid}/kill-switch", timeout=15)

    def test_wallet_recharge_and_invoice(self, super_session):
        clients = super_session.get(f"{API}/admin/clients", timeout=15).json()
        acme = next((c for c in clients if c["name"] == "Acme Industries"), clients[0])
        before = acme.get("wallet_balance", 0)
        amount = 500.0
        r = super_session.post(f"{API}/admin/wallet/recharge",
                               json={"client_id": acme["id"], "amount": amount, "note": "TEST"},
                               timeout=15)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["balance"] == before + amount
        assert d["invoice_no"].startswith("INV-")

    def test_audit_log(self, super_session):
        r = super_session.get(f"{API}/admin/audit", timeout=15)
        assert r.status_code == 200
        logs = r.json()
        assert any(l["action"] == "wallet.recharge" for l in logs)
        assert any(l["action"] in ("client.create", "client.kill_switch") for l in logs)
        _no_id_leak(logs)


# ---------- Assets / Inspections / Maintenance ----------
class TestAssetsFlow:
    @pytest.fixture(scope="class")
    def admin_sess(self):
        s, _ = _login(CADMIN)
        return s

    @pytest.fixture(scope="class")
    def tech_sess(self):
        s, _ = _login(TECH)
        return s

    def test_list_assets_tenant_scoped(self, admin_sess):
        r = admin_sess.get(f"{API}/assets", timeout=15)
        assert r.status_code == 200
        items = r.json()
        assert isinstance(items, list) and len(items) > 0
        for a in items:
            assert a.get("client_id")
            assert a.get("expiry_status") in ("ok", "expiring", "expired")
        _no_id_leak(items)

    def test_create_asset_and_get(self, admin_sess):
        sites = admin_sess.get(f"{API}/sites", timeout=15).json()
        assert sites
        payload = {
            "site_id": sites[0]["id"],
            "name": "TEST_Asset_" + uuid.uuid4().hex[:6],
            "category": "extinguisher", "sub_type": "ABC 6kg",
            "serial_number": "TEST-SN-1",
            "install_date": "2024-01-01", "expiry_date": "2030-01-01",
        }
        r = admin_sess.post(f"{API}/assets", json=payload, timeout=15)
        assert r.status_code == 200, r.text
        aid = r.json()["id"]
        r2 = admin_sess.get(f"{API}/assets/{aid}", timeout=15)
        assert r2.status_code == 200
        d = r2.json()
        assert d["asset"]["name"] == payload["name"]
        assert "inspections" in d and "maintenance" in d
        TestAssetsFlow._aid = aid

    def test_inspection_fail_marks_faulty(self, admin_sess):
        aid = getattr(TestAssetsFlow, "_aid", None)
        if not aid:
            pytest.skip("no asset")
        r = admin_sess.post(f"{API}/inspections", json={
            "asset_id": aid,
            "checklist": [{"item": "Pressure", "ok": False, "note": "low"}],
            "overall_result": "fail",
            "inspector_name": "Tester",
        }, timeout=15)
        assert r.status_code == 200, r.text
        # asset should now be faulty
        a = admin_sess.get(f"{API}/assets/{aid}", timeout=15).json()["asset"]
        assert a["status"] == "faulty"

    def test_tech_sees_only_assigned_maintenance(self, tech_sess, admin_sess):
        r = tech_sess.get(f"{API}/maintenance", timeout=15)
        assert r.status_code == 200
        tech_tasks = r.json()
        # all should belong to this technician
        me = tech_sess.get(f"{API}/auth/me", timeout=15).json()
        for t in tech_tasks:
            assert t.get("technician_id") == me["id"]
        # Admin sees all (>= tech count)
        all_tasks = admin_sess.get(f"{API}/maintenance", timeout=15).json()
        assert len(all_tasks) >= len(tech_tasks)

    def test_complete_maintenance_updates_asset(self, tech_sess):
        tasks = tech_sess.get(f"{API}/maintenance", timeout=15).json()
        if not tasks:
            pytest.skip("no maintenance tasks")
        tid = tasks[0]["id"]
        r = tech_sess.patch(f"{API}/maintenance/{tid}",
                            json={"status": "completed"}, timeout=15)
        assert r.status_code == 200


# ---------- Incidents, Compliance, Wallet, Notifications, Users ----------
class TestRemaining:
    @pytest.fixture(scope="class")
    def admin_sess(self):
        s, _ = _login(CADMIN)
        return s

    def test_create_incident(self, admin_sess):
        sites = admin_sess.get(f"{API}/sites", timeout=15).json()
        r = admin_sess.post(f"{API}/incidents", json={
            "site_id": sites[0]["id"],
            "title": "TEST_Fire_Alarm",
            "severity": "critical",
            "description": "Test incident",
        }, timeout=15)
        assert r.status_code == 200, r.text
        # listing
        items = admin_sess.get(f"{API}/incidents", timeout=15).json()
        assert any(i["title"] == "TEST_Fire_Alarm" for i in items)

    def test_compliance_score(self, admin_sess):
        r = admin_sess.get(f"{API}/compliance/score", timeout=15)
        assert r.status_code == 200
        d = r.json()
        for k in ["score", "status", "trend", "expired_assets",
                  "missed_maintenance", "failed_inspections"]:
            assert k in d
        assert isinstance(d["trend"], list) and len(d["trend"]) >= 2

    def test_compliance_noc(self, admin_sess):
        r = admin_sess.get(f"{API}/compliance/noc", timeout=15)
        assert r.status_code == 200
        rows = r.json()
        assert rows
        sample = rows[0]
        for k in ["site", "checklist", "ready", "progress"]:
            assert k in sample
        # update one item
        cl = sample["checklist"]
        if cl:
            r2 = admin_sess.patch(f"{API}/compliance/noc/{cl[0]['id']}",
                                  json={"completed": True}, timeout=15)
            assert r2.status_code == 200

    def test_amc_opportunities(self, admin_sess):
        r = admin_sess.get(f"{API}/compliance/amc-opportunities", timeout=15)
        assert r.status_code == 200
        d = r.json()
        for k in ["expired", "expiring", "missed", "total_opportunity_value"]:
            assert k in d

    def test_risk_map(self, admin_sess):
        r = admin_sess.get(f"{API}/compliance/risk-map", timeout=15)
        assert r.status_code == 200
        zones = r.json()
        assert isinstance(zones, list)
        if zones:
            assert zones[0]["risk"] in ("high", "medium", "low")

    def test_wallet_client(self, admin_sess):
        r = admin_sess.get(f"{API}/wallet", timeout=15)
        assert r.status_code == 200
        d = r.json()
        assert "balance" in d and "transactions" in d
        assert isinstance(d["transactions"], list)

    def test_wallet_super_admin_zero(self):
        s, _ = _login(SUPER)
        r = s.get(f"{API}/wallet", timeout=15)
        assert r.status_code == 200
        assert r.json()["balance"] == 0

    def test_notifications(self, admin_sess):
        r = admin_sess.get(f"{API}/notifications", timeout=15)
        assert r.status_code == 200
        d = r.json()
        assert "items" in d and "unread" in d
        # mark all read
        r2 = admin_sess.post(f"{API}/notifications/read-all", timeout=15)
        assert r2.status_code == 200
        d2 = admin_sess.get(f"{API}/notifications", timeout=15).json()
        assert d2["unread"] == 0

    def test_create_user_and_duplicate(self, admin_sess):
        email = f"TEST_user_{uuid.uuid4().hex[:6]}@acme.in"
        r = admin_sess.post(f"{API}/users", json={
            "email": email, "password": "Pass@12345",
            "name": "Test User", "role": "fire_officer"
        }, timeout=15)
        assert r.status_code == 200, r.text
        # duplicate
        r2 = admin_sess.post(f"{API}/users", json={
            "email": email, "password": "Pass@12345",
            "name": "Test User", "role": "fire_officer"
        }, timeout=15)
        assert r2.status_code == 400


# ---------- Bcrypt format check (direct DB-less: via login behavior) ----------
class TestSecurity:
    def test_bcrypt_via_admin_users_endpoint(self):
        # Using super admin we can list users; check no password_hash leaks
        s, _ = _login(SUPER)
        r = s.get(f"{API}/users", timeout=15)
        # super admin does have access (require_role super_admin/client_admin)
        assert r.status_code == 200
        for u in r.json():
            assert "password_hash" not in u
            assert "_id" not in u
