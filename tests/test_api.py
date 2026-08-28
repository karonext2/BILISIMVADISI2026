"""API sözleşme testleri (TestClient). karonext.sqlite gerektirir."""

import pytest
from fastapi.testclient import TestClient

from api.main import app
from data_layer import repository as repo

pytestmark = pytest.mark.skipif(
    not repo.veritabani_var_mi(), reason="karonext.sqlite yok"
)

client = TestClient(app)


def test_health():
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["bilesenler"]["veri_katmani"] == "ok"


def test_banks_toplam():
    r = client.get("/api/v1/banks")
    assert r.status_code == 200
    d = r.json()
    assert d["toplam_banka"] == 10
    assert 350 < sum(b["kayit_sayisi"] for b in d["bankalar"]) < 469  # yatirim ailesi dashboard'dan gizli


def test_stats_dinamik():
    r = client.get("/api/v1/stats")
    assert r.status_code == 200
    assert 350 < r.json()["toplam_kayit"] < 469  # yatirim gizli
    assert r.json()["guncelleme_tarihi"]


def test_campaigns_filtre_kesisimi():
    r = client.get(
        "/api/v1/campaigns",
        params={"urun_ailesi": "finansman", "aktif_mi": True, "size": 10},
    )
    assert r.status_code == 200
    for it in r.json()["items"]:
        assert it["urun_ailesi"] == "finansman"
        assert it["aktif_mi"] is True


def test_campaigns_sayfalama_meta():
    r = client.get("/api/v1/campaigns", params={"page": 2, "size": 10})
    d = r.json()
    assert d["page"] == 2 and d["size"] == 10
    assert d["toplam_sayfa"] == (d["toplam"] + 9) // 10


def test_campaign_detay_ve_kaynak():
    lst = client.get("/api/v1/campaigns", params={"size": 1}).json()
    rid = lst["items"][0]["record_id"]
    r = client.get(f"/api/v1/campaigns/{rid}")
    assert r.status_code == 200
    d = r.json()
    assert d["kaynak_bilgisi"]["veri_tarihi"]
    assert "hesaplama_yapilabilir_mi" in d


def test_bilinmeyen_id_404_zarf():
    r = client.get("/api/v1/campaigns/OLMAYAN_ID")
    assert r.status_code == 404
    j = r.json()
    assert j["hata"] is True and j["error_id"] and "mesaj" in j


def test_gecersiz_parametre_422_teknik_sizinti_yok():
    r = client.get("/api/v1/campaigns", params={"vade_min": 99999})
    assert r.status_code == 422
    govde = r.text.lower()
    for yasak in ("traceback", "evren", "qdrant", "sqlite", "pydantic"):
        assert yasak not in govde


def test_compare_secili_kayitlar():
    ids = [
        it["record_id"]
        for it in client.get(
            "/api/v1/campaigns", params={"urun_ailesi": "finansman", "size": 3}
        ).json()["items"]
    ]
    r = client.post("/api/v1/compare", json={"record_idler": ids})
    assert r.status_code == 200
    d = r.json()
    assert d["kayit_sayisi"] == len(ids)
    assert "neden" in d


def test_compare_tek_id_422():
    r = client.post("/api/v1/compare", json={"record_idler": ["x"]})
    assert r.status_code == 422
