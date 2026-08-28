"""Genel uçlar: bankalar, filtre değerleri, istatistik, sağlık."""

from __future__ import annotations

from fastapi import APIRouter

from api.schemas import (
    BankaListesi,
    FiltreDegerleri,
    Istatistik,
    SaglikDurumu,
)
from core.errors import VeriKatmaniHatasi
from data_layer import repository as repo

router = APIRouter()


@router.get("/banks", response_model=BankaListesi)
def bankalar():
    if not repo.veritabani_var_mi():
        raise VeriKatmaniHatasi()
    b = repo.banks()
    return {"bankalar": b, "toplam_banka": len(b)}


@router.get("/filters", response_model=FiltreDegerleri)
def filtreler():
    if not repo.veritabani_var_mi():
        raise VeriKatmaniHatasi()
    return repo.filter_values()


@router.get("/stats", response_model=Istatistik)
def istatistik():
    if not repo.veritabani_var_mi():
        raise VeriKatmaniHatasi()
    return repo.stats()


@router.get("/health", response_model=SaglikDurumu)
def saglik():
    bilesenler: dict[str, str] = {}
    kayit_sayisi = None

    try:
        if repo.veritabani_var_mi():
            kayit_sayisi = repo.stats()["toplam_kayit"]
            bilesenler["veri_katmani"] = "ok"
        else:
            bilesenler["veri_katmani"] = "error"
    except Exception:  # noqa: BLE001
        bilesenler["veri_katmani"] = "error"

    # LLM ve vektör DB durumu — bağlantı denemesi maliyetli olduğundan yalnızca
    # yapılandırma varlığı kontrol edilir (derin kontrol /health?deep=1 ile eklenebilir).
    from core.settings import settings

    bilesenler["llm"] = "yapilandirildi" if settings.evren_api_key else "eksik"
    bilesenler["vektor_db"] = "yapilandirildi" if settings.evren_qdrant_key else "eksik"

    durum = "ok" if bilesenler.get("veri_katmani") == "ok" else "degraded"
    return {"status": durum, "bilesenler": bilesenler, "kayit_sayisi": kayit_sayisi}
