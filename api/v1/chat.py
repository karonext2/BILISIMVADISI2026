"""Katılım Bankacılığı Asistanı ucu — POST /api/v1/chat, POST /api/v1/search."""

from __future__ import annotations

from fastapi import APIRouter

from api.schemas import (
    AramaIstegi,
    AramaSonucu,
    ChatCevap,
    ChatIstegi,
)
from core.errors import UpstreamHatasi, VeriKatmaniHatasi
from core.logging import logger
from data_layer import repository as repo
from rag.retriever import retrieve

router = APIRouter()


@router.post("/chat", response_model=ChatCevap)
def chat(req: ChatIstegi):
    if not repo.veritabani_var_mi():
        raise VeriKatmaniHatasi()
    from chatbot.chain import cevapla

    try:
        return cevapla(
            soru=req.soru,
            top_k=req.top_k,
            bankalar=req.bankalar,
            urun_ailesi=req.urun_ailesi,
            kayit_idleri=req.kayit_idleri,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("chat hatası")
        raise UpstreamHatasi(str(exc)) from exc


@router.post("/search", response_model=AramaSonucu)
def search(req: AramaIstegi):
    if not repo.veritabani_var_mi():
        raise VeriKatmaniHatasi()
    try:
        kayitlar = retrieve(
            req.query, top_k=req.top_k, bankalar=req.bankalar, urun_ailesi=req.urun_ailesi
        )
    except Exception as exc:  # noqa: BLE001
        raise UpstreamHatasi(str(exc)) from exc

    return {
        "sonuclar": [
            {
                "record_id": k["record_id"],
                "banka": k.get("banka"),
                "urun_adi": k.get("urun_adi") or k.get("baslik"),
                "urun_ailesi": k.get("urun_ailesi"),
                "kampanya_turu": k.get("kampanya_turu"),
                "kar_payi_orani_raw": k.get("kar_payi_orani_raw"),
                "vade_raw": k.get("vade_raw"),
                "url": k.get("url"),
                "skor": k.get("_skor"),
            }
            for k in kayitlar
        ]
    }
