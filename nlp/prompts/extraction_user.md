Aşağıdaki metinden finansal bilgi çıkarımı yap.

Çıkarılacak alanlar (hepsi zorunlu; değer yoksa null veya boş liste):
- banka: metnin ait olduğu banka (aşağıda BANKA verildiyse onu kullan)
- urun_adi: ürün / kampanya adı
- kampanya_turu: enum değerlerinden biri
- kar_payi_orani_raw, finansman_tutari_raw, finansman_orani_raw, vade_raw,
  taksit_sayisi_raw, tahsis_ucreti_raw, masraf_bilgisi, odul_miktari_raw,
  indirim_orani_raw, alisveris_puani_raw: metindeki HAM ifade (normalize etme)
- kampanya_baslangic_tarihi, kampanya_bitis_tarihi: kampanya geçerlilik tarihleri
- hedef_kitle, kampanya_kosullari, avantajlar: kısa madde listeleri

Kurallar sistem mesajındadır. Metinde açıkça yazmayan hiçbir sayıyı, oranı, vadeyi,
tutarı, tarihi veya ücreti uydurma.

--- BANKA ---
{{BANKA}}

--- KAMPANYA / ÜRÜN BAŞLIĞI ---
{{BASLIK}}

--- METİN ---
{{METIN}}
