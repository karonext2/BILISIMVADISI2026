# Kampanya NLP Classification Starter

Bu klasör, kampanya metinlerini 6 kategoriye ayıran başlangıç modelidir.

Kategoriler:
- konut_finansmani
- tasit_finansmani
- ihtiyac_finansmani
- kredi_karti
- katilma_hesabi
- yatirim

## 1. Kurulum

Proje klasöründe terminal aç:

```bash
pip install -r requirements.txt
```

## 2. Modeli eğit

```bash
python nlp/train.py
```

Başarılı olursa:

```text
models/campaign_classifier.joblib
```

oluşur.

## 3. Modeli terminalden test et

```bash
python nlp/predict.py
```

Örnek:

```text
Kampanya metni: Sıfır araç alımlarında 48 aya kadar finansman fırsatı
```

## 4. HTML ile bağlamak için API'yi aç

```bash
cd nlp
uvicorn api:app --reload --port 8000
```

Sonra API:
- GET http://127.0.0.1:8000/
- POST http://127.0.0.1:8000/classify

Örnek POST JSON:

```json
{
  "metin": "Market alışverişlerinde kartınıza yüzde 20 indirim"
}
```

## Önemli

`data/kampanyalar.csv` başlangıç amaçlı sentetik/örnek veri içerir.
Yarışma için gerçek scraper verileriyle genişletilmeli ve ayrı bir gerçek test seti tutulmalıdır.
Sentetik veri üzerindeki yüksek skor, gerçek dünya başarısı olarak raporlanmamalıdır.

## 5. Entegre HTML'i çalıştır

Paket içindeki `index_ml.html`, mevcut arayüzün ML modele bağlanmış sürümüdür.

Önce API'yi aç:

```bash
cd nlp
uvicorn api:app --reload --port 8000
```

Sonra `index_ml.html` dosyasını tarayıcıda aç.

Akış:

```text
Kampanya metni
   -> TF-IDF + Logistic Regression ile kategori tahmini
   -> Regex ile oran/tutar/vade/tarih çıkarımı
   -> Katılım bankacılığı ontolojisi
   -> JSON çıktı
```

API kapalıysa arayüz otomatik olarak eski `kategori()` rule-based yöntemine geri döner.
