"""Ham çıkarım kayıtlarından kanonik türetilmiş alanları üretir.

Hiçbir şey uydurulmaz: yalnızca metinde/alanlarda açıkça olan bilgiden
kural tabanlı sınıflandırma ve tarih ayrıştırma yapılır.
"""

from __future__ import annotations

import re
from datetime import date

# ---------------------------------------------------------------------------
# ÜRÜN AİLESİ
# ---------------------------------------------------------------------------

_FINANSMAN_TURLERI = {
    "Konut Finansmanı Kampanyası",
    "Taşıt Finansmanı Kampanyası",
    "İhtiyaç Finansmanı Kampanyası",
    "Finansman Kampanyası",
}
_KART_TURLERI = {"Kart Kampanyası", "Alışveriş Puanı Kampanyası"}
_YATIRIM_TURLERI = {"Yatırım Ürünü Kampanyası"}

_MEVDUAT_RE = re.compile(
    r"katılma hes|vadeli hes|vadeli katılma|birikim hes|altın hes|gümüş hes|"
    r"döviz hes|tl katılma|katılma hesabı|getiri|\btns\b|katılım hesabı|"
    r"kazandıran hesap|değerlendiren hesap|çeyiz hes|çeyiz hesabı|altın kesem|"
    r"\bkesem\b|birikim hesabı|standart katılma|klasik katılma",
    re.IGNORECASE,
)
_FINANSMAN_RE = re.compile(
    r"finansman|murabaha|leasing|\bkredi\b|destek paket|ev sahibi|araç sahibi|"
    r"taşıt kredi|konut kredi|ihtiyaç kredi",
    re.IGNORECASE,
)
_KART_RE = re.compile(
    r"\bkart\b|worldcard|troy|bankkart|kredi kartı|axess|bonus card|"
    r"sağlam kart|ödeme kartı|prepaid",
    re.IGNORECASE,
)
_YATIRIM_RE = re.compile(
    r"\bfon\b|yatırım|sukuk|hisse|kıymetli maden|altın gram|portföy|"
    r"sermaye piyas|hazine ürün|katılım endeks",
    re.IGNORECASE,
)


def urun_ailesi(record: dict, kar_payi_turu: str) -> str:
    # 1) Kampanya türü açık aile veriyorsa onu kullan
    kt = str(record.get("kampanya_turu") or "")
    if kt in _FINANSMAN_TURLERI:
        return "finansman"
    if kt in _KART_TURLERI:
        return "kart"
    if kt in _YATIRIM_TURLERI:
        return "yatirim"

    # 2) Kâr payı türü çok güçlü sinyal (bu veri setinde):
    #    aylık % oran = finansman maliyet oranı, yıllık % = mevduat/katılma getirisi
    has_rate = record.get("kar_payi_orani_min") is not None
    if has_rate and kar_payi_turu == "yillik":
        return "mevduat"
    if has_rate and kar_payi_turu == "aylik":
        return "finansman"

    # 3) Başlık/ürün adı temiz metindir — metin (pazarlama gövdesi) gürültülü,
    #    o yüzden önce yalnızca başlık + ürün adına bak
    baslik_blob = " ".join(
        str(record.get(k) or "") for k in ("urun_adi", "baslik")
    ).lower()
    for rx, aile in (
        (_MEVDUAT_RE, "mevduat"),
        (_FINANSMAN_RE, "finansman"),
        (_KART_RE, "kart"),
        (_YATIRIM_RE, "yatirim"),
    ):
        if rx.search(baslik_blob):
            return aile

    # 4) Son çare: tam metne bak
    metin = str(record.get("metin") or "").lower()
    for rx, aile in (
        (_MEVDUAT_RE, "mevduat"),
        (_FINANSMAN_RE, "finansman"),
        (_KART_RE, "kart"),
        (_YATIRIM_RE, "yatirim"),
    ):
        if rx.search(metin):
            return aile

    return "diger"


# ---------------------------------------------------------------------------
# KÂR PAYI TÜRÜ
# ---------------------------------------------------------------------------

_ORAN_TUTAR_RE = re.compile(r"%\s*\d")
_TL_RE = re.compile(r"\d[\d.]*\s*(?:tl|₺)", re.IGNORECASE)


def finansman_orani_duzelt(
    mevcut_oran: float | None,
    finansman_tutari_raw: str | None,
) -> float | None:
    """'Ekspertiz Değerinin %80'i' gibi ifadeler finansman TUTARI değil ORANIDIR.

    Eski çıkarımda bu oranlar yanlışlıkla finansman_tutari_raw alanına düşmüş.
    Alan bir TL tutarı içermiyor ama % içeriyorsa oranı buradan türet.
    """
    if mevcut_oran is not None:
        return mevcut_oran
    s = (finansman_tutari_raw or "").strip()
    if s and _ORAN_TUTAR_RE.search(s) and not _TL_RE.search(s):
        m = re.findall(r"%\s*(\d+(?:[.,]\d+)?)", s)
        if m:
            return float(m[-1].replace(",", "."))  # aralıkta üst sınırı al
    return mevcut_oran


def kar_payi_turu(raw: str | None) -> str:
    if not raw:
        return "bilinmiyor"
    s = str(raw).lower()
    if "aylık" in s or "aylik" in s:
        return "aylik"
    if "yıllık" in s or "yillik" in s or "tns" in s or "brüt" in s or "yıllik" in s:
        return "yillik"
    return "bilinmiyor"


# ---------------------------------------------------------------------------
# TARİH AYRIŞTIRMA
# ---------------------------------------------------------------------------

_AYLAR = {
    "ocak": 1, "şubat": 2, "subat": 2, "mart": 3, "nisan": 4, "mayıs": 5,
    "mayis": 5, "haziran": 6, "temmuz": 7, "ağustos": 8, "agustos": 8,
    "eylül": 9, "eylul": 9, "ekim": 10, "kasım": 11, "kasim": 11,
    "aralık": 12, "aralik": 12,
}


def parse_tr_date(value: str | None, varsayilan_yil: int = 2026) -> str | None:
    """Türkçe tarih ifadesini YYYY-MM-DD'ye çevirir. Çözemezse None."""
    if not value:
        return None
    s = str(value).strip().lower()

    # 31.08.2026 / 31/08/2026 / 31-08-2026
    m = re.search(r"\b(\d{1,2})[./-](\d{1,2})[./-](\d{2,4})\b", s)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if y < 100:
            y += 2000
        return _safe_iso(y, mo, d)

    # 31 Ağustos 2026 / 31 Aralık (yıl yok -> varsayılan)
    m = re.search(r"\b(\d{1,2})\s+([a-zçğıöşü]+)\s*(\d{4})?", s)
    if m and m.group(2) in _AYLAR:
        d = int(m.group(1))
        mo = _AYLAR[m.group(2)]
        y = int(m.group(3)) if m.group(3) else varsayilan_yil
        return _safe_iso(y, mo, d)

    return None


def _safe_iso(y: int, mo: int, d: int) -> str | None:
    try:
        return date(y, mo, d).isoformat()
    except ValueError:
        return None


def aktif_mi(bitis_iso: str | None, bugun: date | None = None) -> bool:
    """Bitiş tarihi geçmişse pasif; tarih yoksa/çözülemezse aktif kabul edilir."""
    if not bitis_iso:
        return True
    bugun = bugun or date.today()
    try:
        return date.fromisoformat(bitis_iso) >= bugun
    except ValueError:
        return True
