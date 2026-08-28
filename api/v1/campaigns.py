"""Kampanya / finansman listeleme + detay — hepsi SQLite'tan (EVREN'siz)."""

from __future__ import annotations

from fastapi import APIRouter, Query

from api.schemas import KampanyaDetay, KampanyaListesi, KaynakBilgisi
from core.errors import VeriBulunamadi, VeriKatmaniHatasi
from data_layer import repository as repo
from schemas.record import Record

router = APIRouter()


def _db_kontrol() -> None:
    if not repo.veritabani_var_mi():
        raise VeriKatmaniHatasi("karonext.sqlite yok")


@router.get("/campaigns", response_model=KampanyaListesi)
def kampanyalar(
    banka: list[str] | None = Query(None),
    kampanya_turu: list[str] | None = Query(None),
    urun_ailesi: list[str] | None = Query(None),
    aktif_mi: bool | None = Query(None),
    has_kar_payi: bool | None = Query(None),
    has_finansal_veri: bool | None = Query(None),
    vade_min: int | None = Query(None, ge=0, le=480),
    vade_max: int | None = Query(None, ge=0, le=480),
    kar_payi_min: float | None = Query(None, ge=0),
    kar_payi_max: float | None = Query(None, ge=0),
    q: str | None = Query(None, max_length=120),
    sort: str = Query("banka"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    _db_kontrol()
    filtreler = {
        "banka": banka,
        "kampanya_turu": kampanya_turu,
        "urun_ailesi": urun_ailesi,
        "aktif_mi": aktif_mi,
        "has_kar_payi": has_kar_payi,
        "has_finansal_veri": has_finansal_veri,
        "vade_min": vade_min,
        "vade_max": vade_max,
        "kar_payi_min": kar_payi_min,
        "kar_payi_max": kar_payi_max,
        "q": q,
    }
    return repo.list_campaigns(filtreler, sort=sort, page=page, size=size)


@router.get("/campaigns/{record_id}", response_model=KampanyaDetay)
def kampanya_detay(record_id: str):
    _db_kontrol()
    kayit = repo.get_campaign(record_id)
    if not kayit:
        raise VeriBulunamadi()

    rec = Record.model_validate(kayit)
    yapilabilir, eksik = rec.hesaplama_yapilabilir_mi()

    on_degerler = {
        "finansman_tutari": rec.finansman_tutari_max or rec.finansman_tutari_min,
        "vade_ay": rec.vade_max_ay,
        "kar_payi_orani": rec.kar_payi_orani_min,
        "oran_periyodu": "aylik" if rec.kar_payi_turu == "aylik" else "yillik",
    }

    return KampanyaDetay(
        **kayit,
        kaynak_bilgisi=KaynakBilgisi(
            banka=rec.banka, url=rec.url, kaynak=rec.kaynak, veri_tarihi=rec.veri_tarihi
        ),
        hesaplama_yapilabilir_mi=yapilabilir,
        hesaplama_eksik_alanlar=eksik,
        hesaplama_on_degerler=on_degerler,
    )
