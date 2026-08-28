# Veri Sözlüğü

## Ham CSV — `data/input/kaynak_469.csv` (469 satır)

| Sütun | Tip | Açıklama |
|---|---|---|
| `banka` | metin | Banka adı (10 farklı değer) |
| `banka_id` | metin | Banka kısa kodu (ör. `kuveytturk`) |
| `baslik` | metin | Sayfa / kampanya başlığı |
| `metin` | metin | Ürün/kampanya serbest metni (NLP girdisi) |
| `url` | metin | Kaynak sayfa adresi (bazı satırlarda boş) |
| `ana_etiket`, `alt_etiket`, `orijinal_kategori` | metin | Ön sınıflandırma etiketleri |
| `kaynak` | metin | Verinin derlendiği dosya/kaynak |

## Kanonik kayıt — `data/final/karonext.sqlite` tablosu `records`

`schemas/record.py` içindeki `Record` Pydantic modelinin bire bir karşılığı.

| Alan | Tip | Türetme / kaynak |
|---|---|---|
| `record_id` | metin (PK) | `sha256(banka\|baslik\|url\|metin[:200])[:24]` |
| `banka`, `banka_id`, `baslik`, `urun_adi` | metin | Ham CSV / çıkarım |
| `kampanya_turu` | metin (enum) | LLM çıkarımı — 10 sınıf |
| `urun_ailesi` | enum `finansman\|mevduat\|kart\|yatirim\|diger` | Kural tabanlı (`data_layer/derive.py`): kampanya türü → kâr payı türü sinyali (aylık %=finansman, yıllık %=mevduat) → başlık regex → metin regex |
| `kar_payi_orani_min` / `_max` | ondalık \| null | `normalize_percentage_range(kar_payi_orani_raw)` |
| `kar_payi_turu` | enum `aylik\|yillik\|bilinmiyor` | `kar_payi_orani_raw` içindeki "(Aylık)" / "(Yıllık TNS)" işareti |
| `kar_payi_orani_raw` | metin \| null | LLM — ham ifade (normalize edilmemiş) |
| `finansman_orani` | ondalık \| null | Ürün bedelinin finanse edilen % oranı |
| `finansman_tutari_min` / `_max` | ondalık \| null | `normalize_amount_range(finansman_tutari_raw)` |
| `finansman_tutari_raw` | metin \| null | LLM — ham ifade |
| `vade_min_ay` / `_max_ay` | tam sayı \| null | `normalize_term_range(vade_raw)` — gün→ay, yıl→ay, TL/% temizleme, 40 yıl üstü gürültü elemesi |
| `vade_raw` | metin \| null | LLM — ham ifade |
| `taksit_sayisi` | tam sayı \| null | `normalize_integer(taksit_sayisi_raw)` |
| `tahsis_ucreti_tl` / `_orani` | ondalık \| null | `normalize_fee(tahsis_ucreti_raw)` — TL ve % ayrı |
| `tahsis_ucreti_raw`, `masraf_bilgisi` | metin \| null | LLM |
| `odul_miktari_tl` / `_raw` | ondalık / metin \| null | LLM + normalize |
| `alisveris_puani` / `_raw`, `indirim_orani` / `_raw` | ondalık / metin \| null | LLM + normalize |
| `kampanya_baslangic_tarihi`, `kampanya_bitis_tarihi` | metin \| null | LLM — ham |
| `kampanya_bitis_iso` | metin `YYYY-MM-DD` \| null | `parse_tr_date` (31.08.2026 / 31 Ağustos 2026 / 31 Aralık→2026) |
| `aktif_mi` | bool | `kampanya_bitis_iso >= bugün` (tarih yoksa/çözülemezse `true`) |
| `hedef_kitle`, `kampanya_kosullari`, `avantajlar` | metin listesi | LLM (SQLite'ta JSON1) |
| `url`, `kaynak`, `metin` | metin \| null | Ham CSV |
| `veri_tarihi` | metin | Sabit `2026-08-27` (kaynak_469.csv dosya tarihi — madde 40, uydurulmadı) |

## RAG chunk metadata — EVREN Qdrant `karonext_products` (2914 nokta)

| Alan | Kaynak |
|---|---|
| `chunk_text` (içerik) | `scripts/chunk_dataset.py` — 800 kar. / 150 overlap |
| `meta.record_id` | chunk → SQLite kaydı bağlantısı |
| `meta.banka`, `meta.urun_ailesi`, `meta.kampanya_turu`, `meta.aktif_mi`, `meta.url` | SQLite'tan zenginleştirme (`scripts/03_index.py`) |

Payload minimaldir; retriever tam kaydı her zaman `record_id` ile SQLite'tan çeker
(tek doğru kaynak — şartname KURAL 9).

## Kâr payı ağını sınıflandırma

Bu veri kümesinde aylık % oranlar (~%2,9–%4,2) **finansman maliyet oranı**, yıllık %
oranlar (~%28–%46) **katılma hesabı getiri oranıdır**. Karşılaştırma motoru bunları
**aynı ölçekte kıyaslamaz** (`services/comparison.py`).
