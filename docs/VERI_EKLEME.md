# Eksik Kampanya / Ürün Verisi Nasıl Eklenir

"Belirtilmemiş" görünen alanları elle doldurmak için **tek bir CSV** dosyası
kullanılır. LLM'e ihtiyaç yoktur.

---

## 1. Şablonu oluştur

```powershell
python scripts/manuel_sablon_olustur.py
```

Bu, `data/input/manuel_veri.csv` dosyasını **eksik verili kayıtlarla ön-doldurulmuş**
olarak üretir. Her satırda:

| Kolon | Ne |
|---|---|
| `banka` | (dolu) eşleştirme için |
| `urun_adi_veya_baslik` | (dolu) eşleştirme için — ürün adı yoksa başlık |
| `_kaynak_url` | (dolu, sadece bilgi) o kaydın web adresi |
| `_metin_ozeti` | (dolu, sadece bilgi) kaynak metnin ilk 300 karakteri |
| `kar_payi_orani_raw` … | **(BOŞ — senin dolduracağın alanlar)** |

Seçenekler:
- `--tumu` → menü/kurumsal sayfalar dahil her boş kayıt
- `--uzerine-yaz` → mevcut CSV'yi sıfırla

---

## 2. CSV'yi Excel'de doldur

`data/input/manuel_veri.csv` dosyasını Excel / LibreOffice ile aç.

- Bildiğin alanları yaz, **bilmediğin/geçersiz alanları BOŞ bırak** (boş = "dokunma").
- `_metin_ozeti` kolonuna bakarak kaynak metinden değeri kopyalayabilirsin.
- Emin değilsen o hücreyi doldurma — sahte veri girme (şartname madde 44).

### Doldurulabilir kolonlar

| Kolon | Örnek değer | Not |
|---|---|---|
| `kar_payi_orani_raw` | `%3.49 - %3.89 (Aylık)` | ham ifade — sistem sayıya çevirir |
| `vade_raw` | `12 - 120 Ay` | `Gün` de olur, aya çevrilir |
| `finansman_tutari_raw` | `1.000 TL - 500.000 TL` | veya `Ekspertiz Değerinin %80'i` |
| `tahsis_ucreti_raw` | `%0.5` veya `575 TL` | |
| `masraf_bilgisi` | `Dosya Masrafsız` | |
| `odul_miktari_raw` | `2.000 TL nakit iade` | |
| `alisveris_puani_raw` | `7.500 Worldpuan` | |
| `indirim_orani_raw` | `%10` | |
| `kampanya_baslangic_tarihi` | `01.08.2026` | |
| `kampanya_bitis_tarihi` | `31.12.2026` | `aktif_mi` buradan hesaplanır |
| `urun_ailesi` | `finansman` / `mevduat` / `kart` / `yatirim` / `diger` | sınıflandırma düzeltmesi |
| `kampanya_turu` | `Konut Finansmanı Kampanyası` | |
| `hedef_kitle` | `yeni müşteriler; maaş müşterileri` | **`;` ile ayır** |
| `kampanya_kosullari` | `mobil uygulamadan katılım; minimum 10.000 TL harcama` | **`;` ile ayır** |
| `avantajlar` | `vade farksız; ücretsiz tahsis` | **`;` ile ayır** |

> Elle girdiğin değer, LLM çıkarımını **ezer** (bilinçli yazdığın kabul edilir).

---

## 3. Veriyi yeniden üret

```powershell
python scripts/02_build_db.py        # CSV -> SQLite (dashboard hemen görür)
python scripts/chunk_dataset.py      # chunk'ları yenile
python scripts/03_index.py --recreate # asistanın da yeni veriyi kullanması için
```

`02_build_db.py` yeterli ise dashboard'da değişiklik anında görünür (backend'i
yeniden başlatmaya gerek yok). Asistanın (chatbot) yeni veriyi kullanması için
`chunk_dataset.py` + `03_index.py` de gerekir.

---

## Eşleştirme nasıl çalışır?

`banka` + `urun_adi_veya_baslik` alanları, kayıttaki `banka` + (`urun_adi` **veya**
`baslik`) ile büyük/küçük harf ve noktalama göz ardı edilerek eşleştirilir.
Eşleşme yoksa o satır atlanır (hata vermez) — `errors_build.jsonl`'a bakma gereği yok,
ama eşleşmeyen satırları kontrol etmek istersen:

```powershell
python -c "from data_layer.manuel import _kayitlar; print(len(_kayitlar()), 'satır yüklendi')"
```

---

## İki veri kaynağı var

| Dosya | Amaç | Öncelik |
|---|---|---|
| `data/input/karsilastirma_tablosu.csv` | 44 ana ürün — **boş** alanları doldurur | LLM çıkarımını ezmez |
| `data/input/manuel_veri.csv` | senin elle girdiğin düzeltmeler | **LLM'i ve tabloyu ezer** |
