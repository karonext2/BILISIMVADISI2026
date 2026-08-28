"""Banka ürün / kampanya karşılaştırma — SALT Python, deterministik.

Şartname madde 17 & 21-24, A9: mevduat getirisi (yüksek = iyi) ile finansman
maliyet oranı (düşük = iyi) AYNI ölçekte karşılaştırılmaz. Karşılaştırma yalnızca
tek ürün ailesi içinde anlamlıdır.
"""

from __future__ import annotations

import math
from typing import Any


def _num(record: dict, key: str) -> float | None:
    v = record.get(key)
    if v is None or v == "":
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(f) else f


def _kayit_ozet(r: dict) -> dict:
    return {
        "record_id": r.get("record_id"),
        "banka": r.get("banka"),
        "urun_adi": r.get("urun_adi") or r.get("baslik"),
        "urun_ailesi": r.get("urun_ailesi"),
        "kar_payi_orani_min": _num(r, "kar_payi_orani_min"),
        "kar_payi_orani_max": _num(r, "kar_payi_orani_max"),
        "kar_payi_turu": r.get("kar_payi_turu"),
        "vade_max_ay": _num(r, "vade_max_ay"),
        "finansman_tutari_max": _num(r, "finansman_tutari_max"),
        "tahsis_ucreti_tl": _num(r, "tahsis_ucreti_tl"),
        "tahsis_ucreti_raw": r.get("tahsis_ucreti_raw"),
        "odul_miktari_tl": _num(r, "odul_miktari_tl"),
        "alisveris_puani": _num(r, "alisveris_puani"),
        "masraf_bilgisi": r.get("masraf_bilgisi"),
        "url": r.get("url"),
    }


def _en(records: list[dict], key: str, en_buyuk: bool):
    adaylar = [(r, _num(r, key)) for r in records]
    adaylar = [(r, v) for r, v in adaylar if v is not None]
    if not adaylar:
        return None
    secim = max(adaylar, key=lambda x: x[1]) if en_buyuk else min(adaylar, key=lambda x: x[1])
    return secim  # (record, value)


def _en_dusuk_tahsis(records: list[dict]):
    adaylar = []
    for r in records:
        raw = str(r.get("tahsis_ucreti_raw") or "")
        v = _num(r, "tahsis_ucreti_tl")
        if v is None or "%" in raw:  # yüzde cinsinden ücretleri TL ile karşılaştırma
            continue
        adaylar.append((r, v))
    return min(adaylar, key=lambda x: x[1]) if adaylar else None


def _en_yuksek_odul(records: list[dict]):
    adaylar = []
    for r in records:
        nakit = _num(r, "odul_miktari_tl")
        puan = _num(r, "alisveris_puani")
        deger = max([x for x in (nakit, puan) if x is not None], default=None)
        if deger is not None:
            tur = "nakit" if (nakit is not None and deger == nakit) else "puan"
            adaylar.append((r, deger, tur))
    return max(adaylar, key=lambda x: x[1]) if adaylar else None


def _yuvarla(v):
    if isinstance(v, float):
        return int(v) if v.is_integer() else round(v, 2)
    return v


def _kriter(ad: str, secim, deger_adi: str, aciklama_kalibi: str) -> dict | None:
    if not secim:
        return None
    r, v = secim
    v = _yuvarla(v)
    return {
        "kriter": ad,
        "kazanan": {
            "record_id": r.get("record_id"),
            "banka": r.get("banka"),
            "urun_adi": r.get("urun_adi") or r.get("baslik"),
            deger_adi: v,
        },
        "aciklama": aciklama_kalibi.format(
            banka=r.get("banka"), urun=r.get("urun_adi") or r.get("baslik"), deger=v
        ),
    }


def compare(records: list[dict], urun_ailesi: str | None = None) -> dict:
    """Verilen kayıtları karşılaştırır. `records` boş/tekse anlamlı sonuç dönmez."""
    aileler = {r.get("urun_ailesi") for r in records if r.get("urun_ailesi")}
    tek_aile = urun_ailesi or (next(iter(aileler)) if len(aileler) == 1 else None)

    uyari = None
    if len(aileler) > 1:
        uyari = (
            "Seçilen ürünler farklı ailelerde ("
            + ", ".join(sorted(a for a in aileler if a))
            + "). Kâr payı / getiri karşılaştırması yapılmadı; "
            "mevduat getirisi ile finansman maliyeti aynı ölçekte kıyaslanamaz."
        )

    kriterler: list[dict] = []

    # --- Kâr payı / getiri (yalnızca tek aile) ---
    if tek_aile == "finansman":
        secim = _en(records, "kar_payi_orani_min", en_buyuk=False)
        k = _kriter(
            "En düşük kâr payı oranı", secim, "kar_payi_orani",
            "{banka} — {urun}: %{deger} ile en düşük aylık kâr payı oranına sahip.",
        )
        if k:
            kriterler.append(k)
    elif tek_aile in ("mevduat", "yatirim"):
        secim = _en(records, "kar_payi_orani_max", en_buyuk=True)
        k = _kriter(
            "En yüksek getiri oranı", secim, "getiri_orani",
            "{banka} — {urun}: %{deger} ile en yüksek getiri oranına sahip.",
        )
        if k:
            kriterler.append(k)

    # --- Vade (uzun = iyi, finansman için) ---
    secim = _en(records, "vade_max_ay", en_buyuk=True)
    k = _kriter(
        "En uzun vade", secim, "vade_ay",
        "{banka} — {urun}: {deger} aya kadar vade ile en uzun ödeme süresini sunuyor.",
    )
    if k:
        kriterler.append(k)

    # --- Tahsis ücreti (düşük = iyi) ---
    secim = _en_dusuk_tahsis(records)
    k = _kriter(
        "En düşük tahsis ücreti", secim, "tahsis_ucreti_tl",
        "{banka} — {urun}: {deger} TL ile en düşük tahsis ücretine sahip.",
    )
    if k:
        kriterler.append(k)

    # --- Ödül (yüksek = iyi) ---
    odul = _en_yuksek_odul(records)
    if odul:
        r, deger, tur = odul
        kriterler.append(
            {
                "kriter": "En yüksek ödül",
                "kazanan": {
                    "record_id": r.get("record_id"),
                    "banka": r.get("banka"),
                    "urun_adi": r.get("urun_adi") or r.get("baslik"),
                    "odul_degeri": deger,
                    "odul_turu": tur,
                },
                "aciklama": (
                    f"{r.get('banka')} — {r.get('urun_adi') or r.get('baslik')}: "
                    f"{deger:g} {'TL nakit ödül' if tur == 'nakit' else 'puan'} ile en yüksek ödülü sunuyor."
                ),
            }
        )

    neden = _neden_metni(kriterler, uyari)

    return {
        "kayit_sayisi": len(records),
        "urun_ailesi": tek_aile,
        "uyari": uyari,
        "kriterler": kriterler,
        "kayitlar": [_kayit_ozet(r) for r in records],
        "neden": neden,
    }


def _neden_metni(kriterler: list[dict], uyari: str | None) -> str:
    if not kriterler:
        return (
            "Seçilen kayıtlarda karşılaştırılabilir sayısal veri (kâr payı, vade, "
            "ücret, ödül) bulunamadı."
        )
    parcalar = [f"{k['kriter'].lower()}: {k['kazanan']['banka']}" for k in kriterler]
    metin = "Öne çıkanlar — " + "; ".join(parcalar) + "."
    if uyari:
        metin += " " + uyari
    return metin


# --- Geriye dönük uyumluluk (eski /compare pipeline'ı) ---
def compare_records(records: list[dict[str, Any]]) -> dict:
    return compare(records)
