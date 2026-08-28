from __future__ import annotations

import hashlib
from typing import Any

from nlp.extractor import extract_financial_info
from nlp.normalizer import normalize_extraction

def build_record_id(
    banka: str,
    baslik: str,
    url: str,
    metin: str = "",
) -> str:
    raw = f"{banka}|{baslik}|{url}|{metin[:200]}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]

def process_record(row: dict[str, Any]) -> dict:
    banka = str(row.get("banka", "") or "").strip()
    baslik = str(row.get("baslik", "") or "").strip()
    metin = str(row.get("metin", "") or "").strip()
    url = str(row.get("url", "") or "").strip()

    if not metin:
        raise ValueError("Kayıtta metin alanı boş.")

    extracted = extract_financial_info(
        text=metin,
        banka=banka or None,
        baslik=baslik or None,
    )
    normalized = normalize_extraction(extracted)

    record_id = build_record_id(banka, baslik, url, metin)

    return {
        "record_id": record_id,
        "banka": banka or extracted.get("banka"),
        "banka_id": str(row.get("banka_id", "") or "").strip(),
        "baslik": baslik,
        "metin": metin,
        "url": url,
        "kaynak": str(row.get("kaynak", "") or "").strip(),
        **normalized,
    }
