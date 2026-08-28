"""Elle küratörlenmiş karşılaştırma tablosu — güvenilir yapılandırılmış ürün verisi.

Kaynak: data/input/karsilastirma_tablosu.csv (44 ürün satırı, 10 banka).
Bu tablo, LLM çıkarımının eksik bıraktığı finansal alanları DETERMİNİSTİK olarak
doldurmak için kullanılır (uydurma değil — insan tarafından derlenmiş kaynak).
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import pandas as pd

TABLO_YOLU = Path(__file__).resolve().parent.parent / "data" / "input" / "karsilastirma_tablosu.csv"

_KATEGORI_AILE = {
    "Katılma Hesabı": "mevduat",
    "Konut Finansmanı": "finansman",
    "Taşıt Finansmanı": "finansman",
    "İhtiyaç Finansmanı": "finansman",
    "KOBİ / Ticari Finansman": "finansman",
}

# Sayısal olmayan oran ifadeleri — bunlar raw olarak saklanır, normalize edilmez
_SAYISAL_ORAN_RE = re.compile(r"%\s*\d")


def _norm(s) -> str:
    return "".join(c.lower() for c in str(s or "") if c.isalnum())


@lru_cache(maxsize=1)
def _tablo() -> pd.DataFrame:
    df = pd.read_csv(TABLO_YOLU, header=3)
    df.columns = ["banka", "kategori", "urun", "oran", "vade", "tutar", "avantaj"]
    return df.dropna(subset=["banka", "urun"]).reset_index(drop=True)


@lru_cache(maxsize=1)
def katalog() -> dict[tuple[str, str], dict]:
    """(banka_norm, urun_norm) -> {kar_payi_orani_raw, vade_raw, finansman_tutari_raw,
    avantaj, urun_kategorisi, urun_ailesi}"""
    out: dict[tuple[str, str], dict] = {}
    for _, r in _tablo().iterrows():
        oran = str(r["oran"]).strip()
        out[(_norm(r["banka"]), _norm(r["urun"]))] = {
            "kar_payi_orani_raw": oran if oran and oran.lower() != "nan" else None,
            "vade_raw": _tmp(r["vade"]),
            "finansman_tutari_raw": _tmp(r["tutar"]),
            "avantaj": _tmp(r["avantaj"]),
            "urun_kategorisi": str(r["kategori"]).strip(),
            "urun_ailesi": _KATEGORI_AILE.get(str(r["kategori"]).strip(), "diger"),
        }
    return out


def _tmp(v) -> str | None:
    s = str(v).strip()
    return s if s and s.lower() != "nan" else None


def eslesme(banka: str | None, urun_adi: str | None, baslik: str | None) -> dict | None:
    k = katalog()
    for ad in (urun_adi, baslik):
        hit = k.get((_norm(banka), _norm(ad)))
        if hit:
            return hit
    return None


def enrich(payload: dict) -> dict:
    """Kayıt payload'ındaki BOŞ finansal alanları katalogdan doldurur.

    Dolu alanlara dokunmaz (LLM çıkarımı korunur). Katalog eşleşmesi varsa
    ürün ailesini ve kategoriyi kataloğa göre günceller (daha güvenilir).
    """
    hit = eslesme(payload.get("banka"), payload.get("urun_adi"), payload.get("baslik"))
    if not hit:
        return payload

    for alan in ("kar_payi_orani_raw", "vade_raw", "finansman_tutari_raw"):
        if not payload.get(alan) and hit.get(alan):
            payload[alan] = hit[alan]

    if hit.get("avantaj"):
        av = list(payload.get("avantajlar") or [])
        if hit["avantaj"] not in av:
            av.append(hit["avantaj"])
        payload["avantajlar"] = av

    payload["urun_kategorisi"] = hit["urun_kategorisi"]
    payload["urun_ailesi"] = hit["urun_ailesi"]
    payload["kuratorlu"] = True
    return payload
