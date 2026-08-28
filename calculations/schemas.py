"""Finansal hesaplama motoru — istek / yanıt modelleri."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

ETIKET = "TAHMİNİ HESAPLAMA"
FORMUL = "murabaha_esit_taksit_anuite"
ACIKLAMA = (
    "Bu sonuç, eşit taksitli (anüite) yöntemle hesaplanmış TAHMİNİ bir değerdir. "
    "Bankanın resmi finansman teklifi veya kendi hesaplama aracının sonucu değildir; "
    "farklılık gösterebilir. KKDF/BSMV, hayat/DASK sigortası, ekspertiz ve ipotek tesis "
    "gibi masraflar bu hesaba dahil değildir. Kesin bilgi için ilgili bankaya başvurun."
)


class CalculateRequest(BaseModel):
    finansman_tutari: float = Field(..., gt=0, le=1e9, description="Anapara (TL)")
    vade_ay: int = Field(..., ge=1, le=360, description="Vade / taksit sayısı (ay)")
    kar_payi_orani: float = Field(..., ge=0, le=100, description="Kâr payı oranı (%)")
    oran_periyodu: Literal["aylik", "yillik"] = "aylik"
    tahsis_ucreti_tl: float | None = Field(None, ge=0, le=1e8)
    tahsis_ucreti_orani: float | None = Field(None, ge=0, le=100)
    odeme_plani_dahil_et: bool = True
    kaynak_record_id: str | None = None


class TaksitSatiri(BaseModel):
    taksit_no: int
    taksit_tutari: float
    kar_payi: float
    anapara: float
    kalan_anapara: float


class CalculateResponse(BaseModel):
    girdiler: dict
    aylik_odeme: float
    toplam_odeme: float
    toplam_kar_payi: float
    tahsis_ucreti_tl: float
    toplam_maliyet: float
    efektif_aylik_oran: float
    odeme_plani: list[TaksitSatiri] | None = None
    etiket: str = ETIKET
    formul: str = FORMUL
    aciklama: str = ACIKLAMA
