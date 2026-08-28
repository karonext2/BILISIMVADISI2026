"""Finansal hesaplama motoru testleri (docs/FORMULAS.md referansı)."""

import math

import pytest
from fastapi.testclient import TestClient

from api.main import app
from calculations.finance import aylik_taksit, hesapla, odeme_plani, yillik_to_aylik
from calculations.schemas import CalculateRequest


def test_anuite_referans_deger():
    # P=100.000, n=12, aylık %1  ->  A ≈ 8884.88
    A = aylik_taksit(100_000, 12, 0.01)
    assert A == pytest.approx(8884.88, abs=0.01)


def test_sifir_oran():
    assert aylik_taksit(120_000, 12, 0.0) == pytest.approx(10_000.0)


def test_tek_taksit():
    assert aylik_taksit(100_000, 1, 0.03) == pytest.approx(103_000.0)


def test_yillik_donusum():
    assert yillik_to_aylik(36.0) == pytest.approx(3.0)


def test_toplam_kar_payi_tutarli():
    r = hesapla(CalculateRequest(finansman_tutari=500_000, vade_ay=36, kar_payi_orani=2.99))
    # aylık ödeme 2 haneye yuvarlandığı için 36 ay üzerinde ~cent düzeyinde sapma normal
    assert r.toplam_kar_payi == pytest.approx(r.aylik_odeme * 36 - 500_000, abs=0.5)
    assert r.toplam_odeme == pytest.approx(r.toplam_kar_payi + 500_000, abs=0.01)


def test_odeme_plani_anapara_toplami_ve_kalan_sifir():
    P, n, r = 500_000, 24, 0.025
    plan = odeme_plani(P, n, r)
    assert sum(s.anapara for s in plan) == pytest.approx(P, abs=0.05)
    assert plan[-1].kalan_anapara == pytest.approx(0.0, abs=0.01)
    assert len(plan) == n


def test_tahsis_ucreti_toplam_maliyete_ekleniyor():
    r = hesapla(
        CalculateRequest(
            finansman_tutari=200_000, vade_ay=12, kar_payi_orani=3.0,
            tahsis_ucreti_orani=0.5,
        )
    )
    assert r.tahsis_ucreti_tl == pytest.approx(1000.0)
    assert r.toplam_maliyet == pytest.approx(r.toplam_odeme + 1000.0, abs=0.01)


def test_her_yanitta_tahmini_etiketi():
    r = hesapla(CalculateRequest(finansman_tutari=150_000, vade_ay=6, kar_payi_orani=4.0))
    assert r.etiket == "TAHMİNİ HESAPLAMA"
    assert "resmi" in r.aciklama.lower()
    assert r.formul == "murabaha_esit_taksit_anuite"


def test_buyuk_deger_tasma_yok():
    r = hesapla(CalculateRequest(finansman_tutari=1e9, vade_ay=120, kar_payi_orani=3.5))
    assert math.isfinite(r.aylik_odeme) and r.aylik_odeme > 0


client = TestClient(app)


def test_api_calculate_gecerli():
    r = client.post(
        "/api/v1/calculate",
        json={"finansman_tutari": 500000, "vade_ay": 60, "kar_payi_orani": 1.89},
    )
    assert r.status_code == 200
    d = r.json()
    assert d["etiket"] == "TAHMİNİ HESAPLAMA"
    assert len(d["odeme_plani"]) == 60


def test_api_calculate_gecersiz_422():
    r = client.post(
        "/api/v1/calculate",
        json={"finansman_tutari": -5, "vade_ay": 0, "kar_payi_orani": 2},
    )
    assert r.status_code == 422
    assert r.json()["hata"] is True
