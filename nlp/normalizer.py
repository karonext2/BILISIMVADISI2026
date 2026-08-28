from __future__ import annotations

import re
from typing import Any


# =========================================================
# TEMEL YARDIMCILAR
# =========================================================

def _clean(value: Any) -> str:
    if value is None:
        return ""

    return str(value).strip()


def _contains_tl_currency(value: Any) -> bool:
    """
    Gerçek TL / ₺ para birimi ifadesi var mı kontrol eder.

    'limitleri' gibi kelimelerin içindeki tesadüfi 'tl'
    harflerini para birimi olarak değerlendirmez.
    """
    s = _clean(value)

    if not s:
        return False

    return bool(
        re.search(
            r"(?<![A-Za-zÇĞİÖŞÜçğıöşü])TL(?![A-Za-zÇĞİÖŞÜçğıöşü])",
            s,
            flags=re.IGNORECASE,
        )
        or "₺" in s
        or re.search(
            r"\bTürk\s+Liras[ıi]\b",
            s,
            flags=re.IGNORECASE,
        )
    )


def _parse_number_token(token: str) -> float | None:
    """
    Türkçe ve İngilizce sayı biçimlerini destekler.

    500         -> 500
    1.500       -> 1500
    1.500.000   -> 1500000
    1.500,50    -> 1500.50
    157.50      -> 157.50
    3,79        -> 3.79
    """
    token = token.strip()
    token = re.sub(r"\s+", "", token)

    if not token:
        return None

    try:
        # Hem nokta hem virgül varsa
        if "." in token and "," in token:

            # Türkçe: 1.500,50
            if token.rfind(",") > token.rfind("."):
                token = token.replace(".", "")
                token = token.replace(",", ".")

            # İngilizce: 1,500.50
            else:
                token = token.replace(",", "")

        elif "," in token:
            parts = token.split(",")

            # 1,500 gibi binlik ayırıcı ihtimali
            if (
                len(parts) == 2
                and len(parts[1]) == 3
                and len(parts[0]) >= 1
            ):
                token = "".join(parts)
            else:
                token = token.replace(",", ".")

        elif "." in token:
            parts = token.split(".")

            # 1.500.000
            if len(parts) > 2:
                token = "".join(parts)

            # 1.500 -> çoğu Türkçe finans metninde 1500
            elif (
                len(parts) == 2
                and len(parts[1]) == 3
            ):
                token = "".join(parts)

        return float(token)

    except ValueError:
        return None


def _extract_numbers(value: Any) -> list[float]:
    s = _clean(value)

    if not s:
        return []

    matches = re.findall(
        r"\d+(?:[.,]\d+)*",
        s,
    )

    values = []

    for match in matches:
        number = _parse_number_token(match)

        if number is not None:
            values.append(number)

    return values


# =========================================================
# YÜZDE / KÂR PAYI
# =========================================================

def normalize_percentage(value: Any) -> float | None:
    """
    %2,05       -> 2.05
    % 2.05      -> 2.05
    %3.79-%4.19 -> 3.79
    """

    values = _extract_numbers(value)

    return values[0] if values else None


def normalize_percentage_range(
    value: Any,
) -> tuple[float | None, float | None]:

    values = _extract_numbers(value)

    if not values:
        return None, None

    if len(values) == 1:
        return values[0], values[0]

    return min(values), max(values)


# =========================================================
# TL TUTARLARI
# =========================================================

def normalize_amount_tl(value: Any) -> float | None:
    """
    TL/₺ tutarlarını normalize eder.

    500 TL -> 500
    1.500 TL -> 1500
    140.000 TL'ye kadar -> 140000

    %80 gibi oranları TL tutarı olarak değerlendirmez.
    """

    s = _clean(value)

    if not s:
        return None

    # Yüzde var ama gerçek para birimi yoksa TL değildir.
    if "%" in s and not _contains_tl_currency(s):
        return None

    values = _extract_numbers(s)

    return values[0] if values else None


def normalize_amount_range(
    value: Any,
) -> tuple[float | None, float | None]:
    """
    Para aralıklarını min/max olarak döndürür.

    1.000 TL - 250.000 TL
    -> (1000, 250000)

    140.000 TL'ye kadar
    -> (140000, 140000)

    BDDK Limitleri / %80'e Kadar
    -> (None, None)
    """

    s = _clean(value)

    if not s:
        return None, None

    # %80 gibi oranları para tutarı sanma.
    if "%" in s and not _contains_tl_currency(s):
        return None, None

    values = _extract_numbers(s)

    if not values:
        return None, None

    if len(values) == 1:
        return values[0], values[0]

    return min(values), max(values)


# =========================================================
# INTEGER
# =========================================================

def normalize_integer(value: Any) -> int | None:
    """
    12 taksit -> 12
    1 - 12 taksit -> 12
    """

    s = _clean(value)

    if not s:
        return None

    values = [
        int(v)
        for v in re.findall(r"\d+", s)
    ]

    if not values:
        return None

    return max(values)


# =========================================================
# VADE
# =========================================================

def normalize_term_range(
    value: Any,
) -> tuple[int | None, int | None]:
    """
    1 - 36 Ay -> (1, 36)
    120 aya kadar -> (120, 120)
    1 - 10 yıl -> (12, 120)
    10 yıl -> (120, 120)
    6 ay - 2 yıl -> (6, 24)   (her sayı kendi birimiyle)
    32 - 365 Gün -> (1, 12)   (gün ay'a çevrilir)
    "... 800.000 TL için 24 ay ..." -> yalnızca 'ay' ile etiketli sayılar
    """

    s = _clean(value).lower()

    if not s:
        return None, None

    # TL tutarlarını ve yüzdeleri temizle ki '800.000 TL' -> 800 ay olmasın
    s = re.sub(r"%\s*\d[\d.,]*", " ", s)
    s = re.sub(r"\d[\d.,]*\s*(?:tl|₺|lira)\b", " ", s)
    s = re.sub(r"\b\d{1,3}(?:[.,]\d{3})+\b", " ", s)  # binlik ayraçlı büyük sayılar

    # Baskın birim: metinde 'ay' varsa ay, yoksa 'gün' varsa gün, yoksa 'yıl' varsa yıl
    if re.search(r"\bay\b|aya\b|ayl", s):
        baskin = "ay"
    elif re.search(r"gün|gun", s):
        baskin = "gun"
    elif re.search(r"yıl|yil|sene", s):
        baskin = "yil"
    else:
        baskin = "ay"

    def _to_month(sayi: int, birim: str) -> int | None:
        if birim in ("yıl", "yil", "sene"):
            return sayi * 12
        if birim in ("gün", "gun"):
            return max(1, round(sayi / 30))
        return sayi  # ay

    aylar: list[int] = []
    for match in re.finditer(r"(\d+)\s*(yıl|yil|sene|gün|gun|ay)?", s):
        sayi = int(match.group(1))
        birim = match.group(2) or baskin
        deger = _to_month(sayi, birim)
        # Aşırı değerleri (40 yıldan uzun) veri gürültüsü say
        if deger is not None and 0 <= deger <= 480:
            aylar.append(deger)

    aylar = [a for a in aylar if a > 0] or aylar
    if not aylar:
        return None, None

    if len(aylar) == 1:
        return aylar[0], aylar[0]

    return min(aylar), max(aylar)


def normalize_term_months(value: Any) -> int | None:
    """
    Eski sistemle uyumluluk için maksimum vadeyi verir.

    1 - 36 Ay -> 36
    120 aya kadar -> 120
    10 yıl -> 120
    """

    _, maximum = normalize_term_range(value)

    return maximum


# =========================================================
# TAHSİS ÜCRETİ
# =========================================================

def normalize_fee(
    value: Any,
) -> tuple[float | None, float | None]:
    """
    Tahsis ücretini TL ve yüzde olarak ayırır.

    157.50 TL -> (157.5, None)
    %0.5      -> (None, 0.5)
    """

    s = _clean(value)

    if not s:
        return None, None

    if "%" in s:
        return None, normalize_percentage(s)

    return normalize_amount_tl(s), None


# =========================================================
# ANA NORMALIZATION
# =========================================================

def normalize_extraction(raw: dict) -> dict:
    out = dict(raw)

    # -----------------------------------------------------
    # KÂR PAYI
    # -----------------------------------------------------

    rate_min, rate_max = normalize_percentage_range(
        raw.get("kar_payi_orani_raw")
    )

    out["kar_payi_orani_min"] = rate_min
    out["kar_payi_orani_max"] = rate_max

    # Eski kodlarla uyumluluk
    out["kar_payi_orani"] = rate_min

    # -----------------------------------------------------
    # FİNANSMAN ORANI
    # -----------------------------------------------------

    out["finansman_orani"] = normalize_percentage(
    raw.get("finansman_orani_raw")
)

    # -----------------------------------------------------
    # FİNANSMAN TUTARI
    # -----------------------------------------------------

    amount_min, amount_max = normalize_amount_range(
        raw.get("finansman_tutari_raw")
    )

    out["finansman_tutari_min"] = amount_min
    out["finansman_tutari_max"] = amount_max

    # Eski alan için maksimum finansman tutarı
    out["finansman_tutari_tl"] = amount_max

    # -----------------------------------------------------
    # VADE
    # -----------------------------------------------------

    term_min, term_max = normalize_term_range(
        raw.get("vade_raw")
    )

    out["vade_min_ay"] = term_min
    out["vade_max_ay"] = term_max

    # Eski alan
    out["vade_ay"] = term_max

    # -----------------------------------------------------
    # TAKSİT
    # -----------------------------------------------------

    out["taksit_sayisi"] = normalize_integer(
        raw.get("taksit_sayisi_raw")
    )

    # -----------------------------------------------------
    # TAHSİS ÜCRETİ
    # -----------------------------------------------------

    fee_tl, fee_rate = normalize_fee(
        raw.get("tahsis_ucreti_raw")
    )

    out["tahsis_ucreti_tl"] = fee_tl
    out["tahsis_ucreti_orani"] = fee_rate

    # -----------------------------------------------------
    # ÖDÜL
    # -----------------------------------------------------

    out["odul_miktari_tl"] = normalize_amount_tl(
        raw.get("odul_miktari_raw")
    )

    # -----------------------------------------------------
    # İNDİRİM
    # -----------------------------------------------------

    out["indirim_orani"] = normalize_percentage(
        raw.get("indirim_orani_raw")
    )

    # -----------------------------------------------------
    # ALIŞVERİŞ PUANI
    # -----------------------------------------------------

    out["alisveris_puani"] = normalize_amount_tl(
        raw.get("alisveris_puani_raw")
    )

    return out