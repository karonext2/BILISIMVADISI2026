from services.comparison import compare


def _kazanan(out, kriter):
    for k in out["kriterler"]:
        if k["kriter"] == kriter:
            return k["kazanan"]["banka"]
    return None


def test_finansman_karsilastirma():
    rows = [
        {"record_id": "A", "banka": "A Bankası", "urun_ailesi": "finansman",
         "kar_payi_orani_min": 3.10, "kar_payi_orani_max": 3.10, "vade_max_ay": 120,
         "odul_miktari_tl": None, "tahsis_ucreti_tl": 0, "tahsis_ucreti_raw": None},
        {"record_id": "C", "banka": "C Bankası", "urun_ailesi": "finansman",
         "kar_payi_orani_min": 2.87, "kar_payi_orani_max": 2.99, "vade_max_ay": 96,
         "odul_miktari_tl": 5000, "tahsis_ucreti_tl": None, "tahsis_ucreti_raw": None},
    ]
    out = compare(rows)
    assert out["urun_ailesi"] == "finansman"
    assert out["uyari"] is None
    assert _kazanan(out, "En düşük kâr payı oranı") == "C Bankası"
    assert _kazanan(out, "En uzun vade") == "A Bankası"
    assert _kazanan(out, "En düşük tahsis ücreti") == "A Bankası"
    assert _kazanan(out, "En yüksek ödül") == "C Bankası"


def test_karisik_aile_uyari_verir_ve_kar_payi_kiyaslamaz():
    rows = [
        {"record_id": "F", "banka": "F", "urun_ailesi": "finansman",
         "kar_payi_orani_min": 3.0, "kar_payi_orani_max": 3.0, "vade_max_ay": 60},
        {"record_id": "M", "banka": "M", "urun_ailesi": "mevduat",
         "kar_payi_orani_min": 42.0, "kar_payi_orani_max": 45.0, "vade_max_ay": 12},
    ]
    out = compare(rows)
    assert out["uyari"] is not None
    kriterler = {k["kriter"] for k in out["kriterler"]}
    assert "En düşük kâr payı oranı" not in kriterler
    assert "En yüksek getiri oranı" not in kriterler


def test_mevduat_en_yuksek_getiri():
    rows = [
        {"record_id": "X", "banka": "X", "urun_ailesi": "mevduat",
         "kar_payi_orani_min": 30.0, "kar_payi_orani_max": 34.0, "vade_max_ay": 3},
        {"record_id": "Y", "banka": "Y", "urun_ailesi": "mevduat",
         "kar_payi_orani_min": 40.0, "kar_payi_orani_max": 46.0, "vade_max_ay": 6},
    ]
    out = compare(rows)
    assert _kazanan(out, "En yüksek getiri oranı") == "Y"


def test_bos_ve_veri_yok():
    out = compare([])
    assert out["kayit_sayisi"] == 0
    assert out["kriterler"] == []
    assert "bulunamadı" in out["neden"]

    out2 = compare([{"record_id": "Z", "banka": "Z", "urun_ailesi": "finansman"}])
    assert out2["kriterler"] == []
