"""Elle girilen ek/düzeltme verisi — data/input/manuel_veri.csv

Kullanıcı bir kaydın eksik alanlarını bu CSV'ye yazar; `02_build_db.py` her kaydı
(banka + ürün adı / başlık) ile eşleştirir ve DOLU hücreleri uygular.
Boş hücre = "bu alana dokunma". Elle girilen değer, LLM çıkarımını EZER (kullanıcı
bilinçli yazmıştır).
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd

DOSYA = Path(__file__).resolve().parent.parent / "data" / "input" / "manuel_veri.csv"

# CSV'de doldurulabilecek alanlar (eşleştirme kolonları hariç)
ALANLAR = [
    "kar_payi_orani_raw",
    "vade_raw",
    "finansman_tutari_raw",
    "tahsis_ucreti_raw",
    "masraf_bilgisi",
    "odul_miktari_raw",
    "alisveris_puani_raw",
    "indirim_orani_raw",
    "kampanya_baslangic_tarihi",
    "kampanya_bitis_tarihi",
    "urun_ailesi",
    "kampanya_turu",
]
# Liste alanları — CSV'de ";" ile ayrılır
LISTE_ALANLARI = ["hedef_kitle", "kampanya_kosullari", "avantajlar"]


def _norm(s) -> str:
    return "".join(c.lower() for c in str(s or "") if c.isalnum())


def _tmp(v):
    s = str(v).strip()
    return s if s and s.lower() != "nan" else None


@lru_cache(maxsize=1)
def _kayitlar() -> dict[tuple[str, str], dict]:
    if not DOSYA.exists():
        return {}
    df = pd.read_csv(DOSYA, dtype=str).fillna("")
    out: dict[tuple[str, str], dict] = {}
    for _, r in df.iterrows():
        banka = _tmp(r.get("banka"))
        anahtar = _tmp(r.get("urun_adi_veya_baslik"))
        if not banka or not anahtar:
            continue
        veri: dict = {}
        for a in ALANLAR:
            val = _tmp(r.get(a))
            if val is not None:
                veri[a] = val
        for a in LISTE_ALANLARI:
            val = _tmp(r.get(a))
            if val is not None:
                veri[a] = [p.strip() for p in val.split(";") if p.strip()]
        if veri:
            out[(_norm(banka), _norm(anahtar))] = veri
    return out


def enrich(payload: dict) -> dict:
    """payload'a elle girilen değerleri uygular (varsa). EZER."""
    kayitlar = _kayitlar()
    if not kayitlar:
        return payload
    for ad in (payload.get("urun_adi"), payload.get("baslik")):
        veri = kayitlar.get((_norm(payload.get("banka")), _norm(ad)))
        if not veri:
            continue
        for k, v in veri.items():
            if k in LISTE_ALANLARI:
                mevcut = list(payload.get(k) or [])
                payload[k] = list(dict.fromkeys(mevcut + v))
            else:
                payload[k] = v
        payload["kuratorlu"] = True
        return payload
    return payload
