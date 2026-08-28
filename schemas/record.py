"""KARONEXT kanonik kayıt şeması.

`data/final/karonext.sqlite` içindeki `records` tablosunun tek doğru tanımıdır.
Dashboard, karşılaştırma ve RAG bu şemayı kullanır (şartname KURAL 9).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

URUN_AILELERI = ("finansman", "mevduat", "kart", "yatirim", "diger")
KAR_PAYI_TURLERI = ("aylik", "yillik", "bilinmiyor")

UrunAilesi = Literal["finansman", "mevduat", "kart", "yatirim", "diger"]
KarPayiTuru = Literal["aylik", "yillik", "bilinmiyor"]

# Veri setinin çekildiği tarih (kaynak_469.csv dosya tarihi). Şartname madde 40:
# tarihi uydurma, veri setindeki gerçek tarihi göster.
VERI_TARIHI = "2026-08-27"


class Record(BaseModel):
    """Tek bir banka ürünü / kampanyası."""

    model_config = {"extra": "forbid"}

    record_id: str
    banka: str
    banka_id: str = ""
    urun_adi: str | None = None
    baslik: str = ""
    kampanya_turu: str = "Kampanya Değil"
    urun_ailesi: UrunAilesi = "diger"
    urun_kategorisi: str | None = None  # küratörlü tablodan (Konut/Taşıt/İhtiyaç/KOBİ Finansmanı, Katılma Hesabı)
    kuratorlu: bool = False             # finansal alanlar karşılaştırma tablosuyla desteklendi mi

    # --- Kâr payı ---
    kar_payi_orani_min: float | None = None
    kar_payi_orani_max: float | None = None
    kar_payi_turu: KarPayiTuru = "bilinmiyor"
    kar_payi_orani_raw: str | None = None

    # --- Finansman ---
    finansman_orani: float | None = None  # ürün bedelinin finanse edilen % oranı
    finansman_tutari_min: float | None = None
    finansman_tutari_max: float | None = None
    finansman_tutari_raw: str | None = None

    # --- Vade / taksit ---
    vade_min_ay: int | None = None
    vade_max_ay: int | None = None
    vade_raw: str | None = None
    taksit_sayisi: int | None = None

    # --- Ücret / masraf ---
    tahsis_ucreti_tl: float | None = None
    tahsis_ucreti_orani: float | None = None
    tahsis_ucreti_raw: str | None = None
    masraf_bilgisi: str | None = None

    # --- Ödül / puan / indirim ---
    odul_miktari_tl: float | None = None
    odul_miktari_raw: str | None = None
    alisveris_puani: float | None = None
    alisveris_puani_raw: str | None = None
    indirim_orani: float | None = None
    indirim_orani_raw: str | None = None

    # --- Tarih ---
    kampanya_baslangic_tarihi: str | None = None
    kampanya_bitis_tarihi: str | None = None
    kampanya_bitis_iso: str | None = None  # YYYY-MM-DD (ayrıştırılabildiyse)
    aktif_mi: bool = True

    # --- Listeler ---
    hedef_kitle: list[str] = Field(default_factory=list)
    kampanya_kosullari: list[str] = Field(default_factory=list)
    avantajlar: list[str] = Field(default_factory=list)

    # --- Kaynak ---
    url: str | None = None
    kaynak: str | None = None
    metin: str = ""
    veri_tarihi: str = VERI_TARIHI

    @field_validator("kar_payi_orani_max")
    @classmethod
    def _max_ge_min(cls, v, info):
        mn = info.data.get("kar_payi_orani_min")
        if v is not None and mn is not None and v < mn:
            return mn
        return v

    @field_validator("vade_max_ay")
    @classmethod
    def _vade_max_ge_min(cls, v, info):
        mn = info.data.get("vade_min_ay")
        if v is not None and mn is not None and v < mn:
            return mn
        return v

    def hesaplama_yapilabilir_mi(self) -> tuple[bool, list[str]]:
        """Finansman hesaplama motoru için yeterli veri var mı?

        Not: motor elle giriş de kabul ettiği için bu yalnızca ön-doldurma
        amaçlıdır; eksik alan varsa kullanıcı elle girer.
        """
        eksik: list[str] = []
        if self.kar_payi_orani_min is None:
            eksik.append("kar_payi_orani")
        if self.vade_max_ay is None:
            eksik.append("vade_ay")
        if self.finansman_tutari_max is None and self.finansman_tutari_min is None:
            eksik.append("finansman_tutari")
        return (len(eksik) == 0, eksik)
