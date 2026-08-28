"""API response modelleri — teknik alan sızıntısını önlemek için sabittir."""

from __future__ import annotations

from pydantic import BaseModel, Field


class HataZarfi(BaseModel):
    hata: bool = True
    mesaj: str
    error_id: str


# --- /banks ---
class BankaOzet(BaseModel):
    banka: str
    banka_id: str | None = None
    kayit_sayisi: int
    kampanya_sayisi: int


class BankaListesi(BaseModel):
    bankalar: list[BankaOzet]
    toplam_banka: int


# --- /filters ---
class Aralik(BaseModel):
    min: float | int | None = None
    max: float | int | None = None


class FiltreDegerleri(BaseModel):
    bankalar: list[str]
    kampanya_turleri: list[str]
    urun_aileleri: list[str]
    vade_araligi_ay: Aralik
    finansman_kar_payi_araligi: Aralik


# --- /campaigns (liste) ---
class KampanyaOzet(BaseModel):
    record_id: str
    banka: str
    urun_adi: str | None = None
    baslik: str
    kampanya_turu: str
    urun_ailesi: str
    kar_payi_orani_min: float | None = None
    kar_payi_orani_max: float | None = None
    kar_payi_turu: str
    vade_min_ay: int | None = None
    vade_max_ay: int | None = None
    finansman_tutari_min: float | None = None
    finansman_tutari_max: float | None = None
    odul_miktari_tl: float | None = None
    aktif_mi: bool
    url: str | None = None
    kaynak: str | None = None


class KampanyaListesi(BaseModel):
    page: int
    size: int
    toplam: int
    toplam_sayfa: int
    items: list[KampanyaOzet]


# --- /campaigns/{id} (detay) ---
class KaynakBilgisi(BaseModel):
    banka: str
    url: str | None = None
    kaynak: str | None = None
    veri_tarihi: str


class KampanyaDetay(BaseModel):
    record_id: str
    banka: str
    urun_adi: str | None = None
    baslik: str
    kampanya_turu: str
    urun_ailesi: str

    kar_payi_orani_min: float | None = None
    kar_payi_orani_max: float | None = None
    kar_payi_turu: str
    kar_payi_orani_raw: str | None = None

    finansman_orani: float | None = None
    finansman_tutari_min: float | None = None
    finansman_tutari_max: float | None = None
    finansman_tutari_raw: str | None = None

    vade_min_ay: int | None = None
    vade_max_ay: int | None = None
    vade_raw: str | None = None
    taksit_sayisi: int | None = None

    tahsis_ucreti_tl: float | None = None
    tahsis_ucreti_orani: float | None = None
    tahsis_ucreti_raw: str | None = None
    masraf_bilgisi: str | None = None

    odul_miktari_tl: float | None = None
    odul_miktari_raw: str | None = None
    alisveris_puani: float | None = None
    alisveris_puani_raw: str | None = None
    indirim_orani: float | None = None
    indirim_orani_raw: str | None = None

    kampanya_baslangic_tarihi: str | None = None
    kampanya_bitis_tarihi: str | None = None
    aktif_mi: bool

    hedef_kitle: list[str] = []
    kampanya_kosullari: list[str] = []
    avantajlar: list[str] = []

    metin: str
    kaynak_bilgisi: KaynakBilgisi

    hesaplama_yapilabilir_mi: bool
    hesaplama_eksik_alanlar: list[str] = []
    hesaplama_on_degerler: dict | None = None


# --- /stats ---
class SayimOgesi(BaseModel):
    tur: str | None = None
    banka: str | None = None
    aile: str | None = None
    adet: int


class DagilimOzet(BaseModel):
    min: float | None = None
    medyan: float | None = None
    max: float | None = None
    veri_olan_kayit: int


class Istatistik(BaseModel):
    toplam_kayit: int
    toplam_banka: int
    toplam_kampanya: int
    aktif_kampanya: int
    finansal_veri_olan_kayit: int
    kuratorlu_kayit: int
    kampanya_turu_dagilimi: list[SayimOgesi]
    banka_dagilimi: list[SayimOgesi]
    urun_ailesi_dagilimi: list[SayimOgesi]
    finansman_kar_payi: DagilimOzet
    vade_dagilimi_ay: DagilimOzet
    guncelleme_tarihi: str | None = None


# --- /health ---
class SaglikDurumu(BaseModel):
    status: str
    bilesenler: dict[str, str]
    kayit_sayisi: int | None = None


# --- /compare ---
class KarsilastirmaIstegi(BaseModel):
    record_idler: list[str] = Field(..., min_length=2, max_length=8)
    urun_ailesi: str | None = None


class KriterSonucu(BaseModel):
    kriter: str
    kazanan: dict
    aciklama: str


class KarsilastirmaSonucu(BaseModel):
    kayit_sayisi: int
    urun_ailesi: str | None = None
    uyari: str | None = None
    kriterler: list[KriterSonucu]
    kayitlar: list[dict]
    neden: str


# --- /chat ---
class ChatIstegi(BaseModel):
    soru: str = Field(..., min_length=2, max_length=500)
    top_k: int = Field(5, ge=1, le=12)
    bankalar: list[str] | None = None           # dashboard aktif filtre bağlamı (madde 34)
    urun_ailesi: str | None = None
    kayit_idleri: list[str] | None = None        # dashboard'da seçili kayıtlar


class Kaynak(BaseModel):
    record_id: str
    banka: str | None = None
    urun_adi: str | None = None
    url: str | None = None
    veri_tarihi: str | None = None


class ChatCevap(BaseModel):
    yanit: str
    kaynaklar: list[Kaynak]
    hesaplama: dict | None = None
    karsilastirma: dict | None = None
    uyari: str | None = None


# --- /search ---
class AramaIstegi(BaseModel):
    query: str = Field(..., min_length=2, max_length=200)
    top_k: int = Field(5, ge=1, le=20)
    bankalar: list[str] | None = None
    urun_ailesi: str | None = None


class AramaOgesi(BaseModel):
    record_id: str
    banka: str | None = None
    urun_adi: str | None = None
    urun_ailesi: str | None = None
    kampanya_turu: str | None = None
    kar_payi_orani_raw: str | None = None
    vade_raw: str | None = None
    url: str | None = None
    skor: float | None = None


class AramaSonucu(BaseModel):
    sonuclar: list[AramaOgesi]
