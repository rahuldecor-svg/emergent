"""Phase-4 backend tests: asset-master, qr single, qr sheet, regression."""
import os
import pytest
import requests

BASE = os.environ["REACT_APP_BACKEND_URL"].rstrip("/")
API = f"{BASE}/api"


def _login(email, password):
    s = requests.Session()
    r = s.post(f"{API}/auth/login", json={"email": email, "password": password}, timeout=20)
    assert r.status_code == 200, f"login failed for {email}: {r.status_code} {r.text}"
    return s


@pytest.fixture(scope="module")
def super_sess():
    return _login("superadmin@sspl.in", "Sspl@12345")


@pytest.fixture(scope="module")
def acme_sess():
    return _login("admin@acme.in", "Acme@12345")


@pytest.fixture(scope="module")
def demo_sess():
    s = requests.Session()
    r = s.post(f"{API}/demo/login", timeout=30)
    assert r.status_code == 200
    return s


@pytest.fixture(scope="module")
def acme_asset_id(acme_sess):
    # Find an existing acme asset, else create one
    r = acme_sess.get(f"{API}/assets", timeout=20)
    assert r.status_code == 200
    items = r.json() if isinstance(r.json(), list) else r.json().get("items", [])
    if items:
        return items[0]["id"]
    # create
    sites = acme_sess.get(f"{API}/sites", timeout=20).json()
    site_id = (sites if isinstance(sites, list) else sites.get("items", []))[0]["id"]
    r = acme_sess.post(f"{API}/assets", json={
        "name": "TEST_P4_QR_Asset", "category": "extinguisher",
        "sub_type": "ABC 9kg", "site_id": site_id,
    }, timeout=20)
    assert r.status_code in (200, 201), r.text
    return r.json()["id"]


# ── Task 1: asset-master ───────────────────────────────────────────────────
class TestAssetMaster:
    def test_unauth_401(self):
        r = requests.get(f"{API}/asset-master", timeout=20)
        assert r.status_code == 401

    def test_categories_and_templates(self, acme_sess):
        r = acme_sess.get(f"{API}/asset-master", timeout=20)
        assert r.status_code == 200
        data = r.json()
        assert "categories" in data
        cats = data["categories"]
        assert len(cats) == 7, f"expected 7 categories, got {len(cats)}"
        total_templates = 0
        for c in cats:
            assert "category" in c and "label" in c and "description" in c
            assert isinstance(c["templates"], list)
            for t in c["templates"]:
                assert "sub_type" in t and "description" in t
            total_templates += len(c["templates"])
        assert total_templates >= 20, f"expected >=20 templates total, got {total_templates}"


# ── Task 2: qr single ──────────────────────────────────────────────────────
class TestQrSingle:
    def test_pdf_returned(self, acme_sess, acme_asset_id):
        r = acme_sess.get(f"{API}/qr/asset/{acme_asset_id}", timeout=30)
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("application/pdf")
        assert "attachment" in r.headers.get("content-disposition", "")
        assert r.content[:4] == b"%PDF"

    def test_cross_tenant_404(self, demo_sess, acme_asset_id):
        r = demo_sess.get(f"{API}/qr/asset/{acme_asset_id}", timeout=20)
        assert r.status_code == 404

    def test_unauth_401(self, acme_asset_id):
        r = requests.get(f"{API}/qr/asset/{acme_asset_id}", timeout=20)
        assert r.status_code == 401


# ── Task 3: qr sheet ───────────────────────────────────────────────────────
class TestQrSheet:
    def test_layout_invalid(self, acme_sess, acme_asset_id):
        r = acme_sess.post(f"{API}/qr/sheet",
                           json={"asset_ids": [acme_asset_id], "layout": 7}, timeout=20)
        assert r.status_code == 400
        assert "layout" in r.json().get("detail", "").lower()

    def test_empty_ids(self, acme_sess):
        r = acme_sess.post(f"{API}/qr/sheet",
                           json={"asset_ids": [], "layout": 10}, timeout=20)
        assert r.status_code == 400
        assert "asset_ids" in r.json().get("detail", "").lower()

    def test_unknown_ids_404(self, acme_sess):
        r = acme_sess.post(f"{API}/qr/sheet",
                           json={"asset_ids": ["nope-1", "nope-2"], "layout": 10}, timeout=20)
        assert r.status_code == 404
        assert "no matching" in r.json().get("detail", "").lower()

    def test_cross_tenant_filtered(self, demo_sess, acme_asset_id):
        # demo_sess has its own assets — mix with acme id; demo should not
        # receive acme asset; if no own asset overlap, expect 404
        r = demo_sess.post(f"{API}/qr/sheet",
                           json={"asset_ids": [acme_asset_id], "layout": 10}, timeout=20)
        assert r.status_code == 404, r.text

    def test_layout_1_pdf(self, acme_sess, acme_asset_id):
        r = acme_sess.post(f"{API}/qr/sheet",
                           json={"asset_ids": [acme_asset_id], "layout": 1}, timeout=30)
        assert r.status_code == 200
        assert r.content[:4] == b"%PDF"
        assert r.headers["content-type"].startswith("application/pdf")

    def test_layout_10_grows_with_assets(self, acme_sess):
        # fetch up to 12 acme asset ids
        items = acme_sess.get(f"{API}/assets", timeout=20).json()
        items = items if isinstance(items, list) else items.get("items", [])
        ids_all = [a["id"] for a in items]
        if len(ids_all) < 2:
            pytest.skip("not enough assets to compare")
        small = ids_all[:1]
        big = ids_all[: min(12, len(ids_all))]
        r1 = acme_sess.post(f"{API}/qr/sheet",
                            json={"asset_ids": small, "layout": 10}, timeout=30)
        r2 = acme_sess.post(f"{API}/qr/sheet",
                            json={"asset_ids": big, "layout": 10}, timeout=30)
        assert r1.status_code == 200 and r2.status_code == 200
        assert len(r2.content) > len(r1.content), \
            f"expected pdf to grow with assets: {len(r1.content)} vs {len(r2.content)}"

    def test_layout_20_ok(self, acme_sess, acme_asset_id):
        r = acme_sess.post(f"{API}/qr/sheet",
                           json={"asset_ids": [acme_asset_id], "layout": 20}, timeout=30)
        assert r.status_code == 200
        assert r.content[:4] == b"%PDF"


# ── Task 4: startup health & regression touch ──────────────────────────────
class TestHealthRegression:
    def test_root(self):
        r = requests.get(f"{API}/", timeout=10)
        assert r.status_code == 200
        j = r.json()
        assert j.get("version") == "1.2.0"
        assert j.get("status") == "operational"

    def test_existing_endpoints_no_500(self, acme_sess):
        endpoints = [
            "/auth/me", "/sites", "/assets", "/wallet", "/notifications",
            "/compliance/summary", "/onboarding/status", "/support/requests",
        ]
        for ep in endpoints:
            r = acme_sess.get(f"{API}{ep}", timeout=20)
            assert r.status_code < 500, f"{ep} → {r.status_code} {r.text[:200]}"
