"""Elle veri ekleme mekanizması (data/input/manuel_veri.csv)."""

import pandas as pd

from data_layer.manuel import ALANLAR, enrich


def test_bos_manuel_dosya_zarar_vermez():
    payload = {"banka": "X", "urun_adi": "Y", "baslik": "", "kar_payi_orani_raw": None,
               "avantajlar": []}
    out = enrich(dict(payload))
    assert out == payload or out["kar_payi_orani_raw"] is None


def test_sablon_kolonlari_dogru(tmp_path):
    from scripts import manuel_sablon_olustur  # noqa: F401  (import edilebiliyor mu)
    assert "kar_payi_orani_raw" in ALANLAR
    assert "kampanya_bitis_tarihi" in ALANLAR


def test_enrich_uygular(monkeypatch, tmp_path):
    csv = tmp_path / "manuel_veri.csv"
    pd.DataFrame([{
        "banka": "Test Bank",
        "urun_adi_veya_baslik": "Süper Finansman",
        "kar_payi_orani_raw": "%2.50 (Aylık)",
        "vade_raw": "1 - 24 Ay",
        "avantajlar": "vade farksız; ücretsiz tahsis",
    }]).to_csv(csv, index=False)

    import data_layer.manuel as m
    monkeypatch.setattr(m, "DOSYA", csv)
    m._kayitlar.cache_clear()

    payload = {"banka": "Test Bank", "urun_adi": "Süper Finansman", "baslik": "",
               "kar_payi_orani_raw": None, "vade_raw": None, "avantajlar": ["mevcut"]}
    out = m.enrich(payload)
    assert out["kar_payi_orani_raw"] == "%2.50 (Aylık)"
    assert out["vade_raw"] == "1 - 24 Ay"
    assert "vade farksız" in out["avantajlar"] and "mevcut" in out["avantajlar"]
    assert out["kuratorlu"] is True
    m._kayitlar.cache_clear()
