"""Banka karşılaştırma ucu — POST /api/v1/compare.

Kullanıcı belirli kayıtları seçer; karşılaştırma yapılandırılmış tam veri
üzerinde (SQLite) yapılır, vektör aramaya bağlı değildir (A10).
"""

from __future__ import annotations

from fastapi import APIRouter

from api.schemas import KarsilastirmaIstegi, KarsilastirmaSonucu
from core.errors import GecersizIstek, VeriKatmaniHatasi
from data_layer import repository as repo
from services.comparison import compare

router = APIRouter()


@router.post("/compare", response_model=KarsilastirmaSonucu)
def karsilastir(req: KarsilastirmaIstegi):
    if not repo.veritabani_var_mi():
        raise VeriKatmaniHatasi()

    kayitlar = repo.records_for_ids(req.record_idler)
    if len(kayitlar) < 2:
        raise GecersizIstek(
            kullanici_mesaji="Karşılaştırmak için en az iki geçerli kayıt seçin."
        )
    return compare(kayitlar, urun_ailesi=req.urun_ailesi)
