"""Anlamsal getirme — chunk düzeyinde arama, kayıt düzeyinde sonuç.

- Sunucu tarafı (Qdrant) banka / ürün ailesi filtresi.
- Skor eşiği (alakasız chunk'ları chatbot'a "kaynak" diye göndermemek için).
- record_id'ye göre tekilleştirme; tam kayıt SQLite'tan (tek veri katmanı).
"""

from __future__ import annotations

from qdrant_client.models import FieldCondition, Filter, MatchAny, MatchValue

from core.settings import settings
from data_layer import repository as repo
from rag.vectorstore import METADATA_KEY, get_vectorstore

VARSAYILAN_SKOR_ESIGI = 0.35


def _qdrant_filter(
    bankalar: list[str] | None,
    urun_ailesi: str | None,
    yalnizca_aktif: bool,
) -> Filter | None:
    kosullar = []
    if bankalar:
        kosullar.append(
            FieldCondition(key=f"{METADATA_KEY}.banka", match=MatchAny(any=list(bankalar)))
        )
    if urun_ailesi:
        kosullar.append(
            FieldCondition(key=f"{METADATA_KEY}.urun_ailesi", match=MatchValue(value=urun_ailesi))
        )
    if yalnizca_aktif:
        kosullar.append(
            FieldCondition(key=f"{METADATA_KEY}.aktif_mi", match=MatchValue(value=True))
        )
    return Filter(must=kosullar) if kosullar else None


def retrieve(
    query: str,
    top_k: int | None = None,
    bankalar: list[str] | None = None,
    urun_ailesi: str | None = None,
    yalnizca_aktif: bool = False,
    skor_esigi: float = VARSAYILAN_SKOR_ESIGI,
) -> list[dict]:
    if not query or not str(query).strip():
        return []

    top_k = top_k or settings.default_top_k
    fetch_k = max(top_k * 6, 24)

    vs = get_vectorstore()
    q_filter = _qdrant_filter(bankalar, urun_ailesi, yalnizca_aktif)

    try:
        vurus = vs.similarity_search_with_score(query.strip(), k=fetch_k, filter=q_filter)
    except Exception:  # noqa: BLE001 — vektör servisi erişilemezse boş dön
        return []

    # record_id'ye göre en iyi skoru tut + eşleşen chunk metnini sakla
    en_iyi: dict[str, dict] = {}
    for doc, score in vurus:
        if score < skor_esigi:
            continue
        rid = doc.metadata.get("record_id")
        if not rid:
            continue
        if rid not in en_iyi or score > en_iyi[rid]["score"]:
            en_iyi[rid] = {"score": float(score), "parca": doc.page_content}

    sirali = sorted(en_iyi.items(), key=lambda x: x[1]["score"], reverse=True)[:top_k]

    sonuc: list[dict] = []
    for rid, bilgi in sirali:
        kayit = repo.get_campaign(rid)
        if not kayit:
            continue
        kayit = dict(kayit)
        kayit["_skor"] = round(bilgi["score"], 4)
        kayit["_eslesen_parca"] = bilgi["parca"]
        sonuc.append(kayit)
    return sonuc
