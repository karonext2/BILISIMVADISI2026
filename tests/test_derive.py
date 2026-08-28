from datetime import date

from data_layer.derive import aktif_mi, kar_payi_turu, parse_tr_date, urun_ailesi


def test_kar_payi_turu():
    assert kar_payi_turu("%3.79 - %4.19 (Aylık)") == "aylik"
    assert kar_payi_turu("%44.00 (Yıllık TNS)") == "yillik"
    assert kar_payi_turu("Havuz Performansına Bağlı") == "bilinmiyor"
    assert kar_payi_turu(None) == "bilinmiyor"


def test_parse_tr_date():
    assert parse_tr_date("31.08.2026") == "2026-08-31"
    assert parse_tr_date("31 Ağustos 2026") == "2026-08-31"
    assert parse_tr_date("31 Aralık") == "2026-12-31"  # yıl yok -> varsayılan 2026
    assert parse_tr_date("01/07/2026") == "2026-07-01"
    assert parse_tr_date("belirsiz") is None
    assert parse_tr_date(None) is None


def test_aktif_mi():
    bugun = date(2026, 8, 28)
    assert aktif_mi("2026-12-31", bugun) is True
    assert aktif_mi("2025-01-01", bugun) is False
    assert aktif_mi(None, bugun) is True  # tarih yoksa aktif kabul
    assert aktif_mi("bozuk", bugun) is True


def test_urun_ailesi_kampanya_turunden():
    assert urun_ailesi({"kampanya_turu": "Konut Finansmanı Kampanyası"}, "bilinmiyor") == "finansman"
    assert urun_ailesi({"kampanya_turu": "Kart Kampanyası"}, "bilinmiyor") == "kart"


def test_urun_ailesi_kar_payi_turu_sinyali():
    # yıllık % oran -> katılma hesabı (mevduat)
    r = {"kampanya_turu": "Kampanya Değil", "kar_payi_orani_min": 42.0,
         "urun_adi": "Üretenle Kazan", "baslik": "", "metin": "finansman kelimesi geçen pazarlama metni"}
    assert urun_ailesi(r, "yillik") == "mevduat"
    # aylık % oran -> finansman
    r2 = {"kampanya_turu": "Kampanya Değil", "kar_payi_orani_min": 3.1,
          "urun_adi": "İlk Evim", "baslik": "", "metin": ""}
    assert urun_ailesi(r2, "aylik") == "finansman"


def test_urun_ailesi_baslik_metinden_once():
    r = {"kampanya_turu": "Kampanya Değil", "kar_payi_orani_min": None,
         "urun_adi": "Çeyiz Hesabı", "baslik": "Çeyiz Hesabı",
         "metin": "bu üründe finansman avantajları vardır"}
    # başlık 'çeyiz hesabı' -> mevduat (metindeki 'finansman' kelimesine kanmaz)
    assert urun_ailesi(r, "bilinmiyor") == "mevduat"
