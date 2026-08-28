export interface BankaOzet {
  banka: string;
  banka_id: string | null;
  kayit_sayisi: number;
  kampanya_sayisi: number;
}

export interface BankaListesi {
  bankalar: BankaOzet[];
  toplam_banka: number;
}

export interface Aralik {
  min: number | null;
  max: number | null;
}

export interface FiltreDegerleri {
  bankalar: string[];
  kampanya_turleri: string[];
  urun_aileleri: string[];
  vade_araligi_ay: Aralik;
  finansman_kar_payi_araligi: Aralik;
}

export interface KampanyaOzet {
  record_id: string;
  banka: string;
  urun_adi: string | null;
  baslik: string;
  kampanya_turu: string;
  urun_ailesi: string;
  kar_payi_orani_min: number | null;
  kar_payi_orani_max: number | null;
  kar_payi_turu: string;
  vade_min_ay: number | null;
  vade_max_ay: number | null;
  finansman_tutari_min: number | null;
  finansman_tutari_max: number | null;
  odul_miktari_tl: number | null;
  aktif_mi: boolean;
  url: string | null;
  kaynak: string | null;
}

export interface KampanyaListesi {
  page: number;
  size: number;
  toplam: number;
  toplam_sayfa: number;
  items: KampanyaOzet[];
}

export interface KaynakBilgisi {
  banka: string;
  url: string | null;
  kaynak: string | null;
  veri_tarihi: string;
}

export interface KampanyaDetay extends KampanyaOzet {
  kar_payi_orani_raw: string | null;
  finansman_orani: number | null;
  finansman_tutari_raw: string | null;
  vade_raw: string | null;
  taksit_sayisi: number | null;
  tahsis_ucreti_tl: number | null;
  tahsis_ucreti_orani: number | null;
  tahsis_ucreti_raw: string | null;
  masraf_bilgisi: string | null;
  odul_miktari_raw: string | null;
  alisveris_puani: number | null;
  alisveris_puani_raw: string | null;
  indirim_orani: number | null;
  indirim_orani_raw: string | null;
  kampanya_baslangic_tarihi: string | null;
  kampanya_bitis_tarihi: string | null;
  hedef_kitle: string[];
  kampanya_kosullari: string[];
  avantajlar: string[];
  metin: string;
  kaynak_bilgisi: KaynakBilgisi;
  hesaplama_yapilabilir_mi: boolean;
  hesaplama_eksik_alanlar: string[];
  hesaplama_on_degerler: {
    finansman_tutari: number | null;
    vade_ay: number | null;
    kar_payi_orani: number | null;
    oran_periyodu: string;
  } | null;
}

export interface SayimOgesi {
  tur?: string | null;
  banka?: string | null;
  aile?: string | null;
  adet: number;
}

export interface DagilimOzet {
  min: number | null;
  medyan: number | null;
  max: number | null;
  veri_olan_kayit: number;
}

export interface Istatistik {
  toplam_kayit: number;
  toplam_banka: number;
  toplam_kampanya: number;
  aktif_kampanya: number;
  finansal_veri_olan_kayit: number;
  kuratorlu_kayit: number;
  kampanya_turu_dagilimi: SayimOgesi[];
  banka_dagilimi: SayimOgesi[];
  urun_ailesi_dagilimi: SayimOgesi[];
  finansman_kar_payi: DagilimOzet;
  vade_dagilimi_ay: DagilimOzet;
  guncelleme_tarihi: string | null;
}

export interface TaksitSatiri {
  taksit_no: number;
  taksit_tutari: number;
  kar_payi: number;
  anapara: number;
  kalan_anapara: number;
}

export interface HesaplamaSonucu {
  girdiler: Record<string, unknown>;
  aylik_odeme: number;
  toplam_odeme: number;
  toplam_kar_payi: number;
  tahsis_ucreti_tl: number;
  toplam_maliyet: number;
  efektif_aylik_oran: number;
  odeme_plani: TaksitSatiri[] | null;
  etiket: string;
  formul: string;
  aciklama: string;
}

export interface KriterSonucu {
  kriter: string;
  kazanan: Record<string, unknown>;
  aciklama: string;
}

export interface KarsilastirmaSonucu {
  kayit_sayisi: number;
  urun_ailesi: string | null;
  uyari: string | null;
  kriterler: KriterSonucu[];
  kayitlar: Record<string, unknown>[];
  neden: string;
}

export interface Kaynak {
  record_id: string;
  banka: string | null;
  urun_adi: string | null;
  url: string | null;
  veri_tarihi: string | null;
}

export interface ChatCevap {
  yanit: string;
  kaynaklar: Kaynak[];
  hesaplama: HesaplamaSonucu | null;
  karsilastirma: KarsilastirmaSonucu | null;
  uyari: string | null;
}
