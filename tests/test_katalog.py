"""Küratörlü karşılaştırma tablosu ile zenginleştirme testleri."""

from data_layer.katalog import enrich, eslesme, katalog


def test_katalog_yuklenir():
    k = katalog()
    assert len(k) >= 40  # 44 ürün satırı


def test_eslesme_urun_adiyla():
    hit = eslesme("Kuveyt Türk", "Cebimden İhtiyaç Finansmanı", None)
    assert hit is not None
    assert "%" in hit["kar_payi_orani_raw"]
    assert hit["urun_ailesi"] == "finansman"
    assert hit["urun_kategorisi"] == "İhtiyaç Finansmanı"


def test_enrich_bos_alanlari_doldurur():
    payload = {
        "banka": "Türkiye Finans",
        "urun_adi": "Auto Finansman",
        "baslik": "Auto Finansman",
        "kar_payi_orani_raw": None,
        "vade_raw": None,
        "finansman_tutari_raw": None,
        "avantajlar": [],
    }
    out = enrich(payload)
    assert out["kar_payi_orani_raw"] and "%" in out["kar_payi_orani_raw"]
    assert out["vade_raw"]
    assert out["urun_ailesi"] == "finansman"
    assert out["kuratorlu"] is True


def test_enrich_dolu_alanlara_dokunmaz():
    payload = {
        "banka": "TOM Bank",
        "urun_adi": "Günlük Kazandıran Hesap",
        "baslik": "",
        "kar_payi_orani_raw": "%99 ELDE VAR (LLM)",  # zaten dolu -> korunmalı
        "vade_raw": None,
        "finansman_tutari_raw": None,
        "avantajlar": [],
    }
    out = enrich(payload)
    assert out["kar_payi_orani_raw"] == "%99 ELDE VAR (LLM)"
    # vade tablodan gelmeli
    assert out["vade_raw"]


def test_enrich_eslesmezse_degistirmez():
    payload = {"banka": "Adil Katılım", "urun_adi": "Adil Katılım Misyonu", "baslik": "",
               "kar_payi_orani_raw": None, "avantajlar": []}
    out = enrich(dict(payload))
    assert out.get("kuratorlu") is not True
    assert out["kar_payi_orani_raw"] is None
