"""Chatbot entegrasyon testleri — EVREN + dolu Qdrant gerektirir. Erişilemezse atlanır."""

import pytest
from fastapi.testclient import TestClient

from api.main import app
from core.settings import settings
from data_layer import repository as repo

try:
    from rag.qdrant_client import get_qdrant_client

    _sayim = get_qdrant_client().count(settings.qdrant_collection).count
except Exception:  # noqa: BLE001
    _sayim = 0

pytestmark = pytest.mark.skipif(
    _sayim < 100 or not repo.veritabani_var_mi(),
    reason="EVREN/Qdrant erişilemez veya veritabanı yok",
)

client = TestClient(app)


def test_chat_bilgi_sorusu_kaynakli():
    r = client.post("/api/v1/chat", json={"soru": "Konut finansmanında en uzun vade hangi bankada?"})
    assert r.status_code == 200
    d = r.json()
    assert d["yanit"]
    assert len(d["kaynaklar"]) >= 1
    assert all("banka" in k for k in d["kaynaklar"])


def test_chat_teknik_terim_sizmaz():
    r = client.post("/api/v1/chat", json={"soru": "Taşıt finansmanı oranları nedir?"})
    metin = r.json()["yanit"].lower()
    for yasak in ("embedding", "vektör", "qdrant", "prompt", "chunk"):
        assert yasak not in metin
    assert "faiz " not in metin  # katılım terminolojisi


def test_chat_hesaplama_tahmini_etiketli():
    r = client.post(
        "/api/v1/chat",
        json={"soru": "300000 TL finansmanı 24 ayda %3 aylık kâr payı ile alırsam aylık ödemem ne olur?"},
    )
    d = r.json()
    assert d["hesaplama"] is not None
    assert d["hesaplama"]["etiket"] == "TAHMİNİ HESAPLAMA"


def test_chat_veride_olmayan_bilgi_uydurulmaz_ve_kaynak_temiz():
    r = client.post(
        "/api/v1/chat",
        json={"soru": "Mars Bankası'nın kripto para faiz oranı nedir?"},
    )
    d = r.json()
    metin = d["yanit"].lower()
    reddetti = any(k in metin for k in ("bulun", "yer almıyor", "yer almamakta", "mevcut değil"))
    assert reddetti
    # "bulunamadı" yanıtında alakasız kaynak kartı gösterilmemeli
    assert d["kaynaklar"] == []


def test_chat_cok_bankali_karsilastirma_ikisini_de_getirir():
    r = client.post(
        "/api/v1/chat",
        json={"soru": "Kuveyt Türk ile Türkiye Finans'ı konut finansmanında karşılaştır."},
    )
    d = r.json()
    bankalar = {k["banka"] for k in d["kaynaklar"]}
    # her iki banka da kaynaklarda görünmeli (senaryo 7)
    assert {"Kuveyt Türk", "Türkiye Finans"}.issubset(bankalar)
