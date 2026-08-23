# 10 Bankalık Katılım Bankacılığı Scraper

## İçerdiği bankalar

1. Adil Katılım
2. Albaraka Türk
3. Dünya Katılım
4. Hayat Finans
5. Kuveyt Türk
6. T.O.M. Bank
7. Türkiye Emlak Katılım
8. Türkiye Finans
9. Vakıf Katılım
10. Ziraat Katılım

## Projeye ekleme

ZIP'teki:

```text
scraper/
scraper_requirements.txt
```

dosyalarını `nlp_classification_starter` klasörünün içine kopyala.

Örnek:

```text
nlp_classification_starter/
├── data/
├── models/
├── nlp/
├── scraper/
│   ├── banks_config.py
│   ├── utils.py
│   └── collect_dataset.py
├── index_ml.html
├── requirements.txt
└── scraper_requirements.txt
```

## Kurulum

Proje kökünde:

```powershell
py -m pip install -r scraper_requirements.txt
```

## Çalıştırma

```powershell
py scraper\collect_dataset.py
```

Bittiğinde proje kökünde:

```text
raw_kampanyalar.csv
```

oluşur.

## Çıktı sütunları

```text
banka
banka_id
baslik
metin
url
```

## Not

Bazı banka siteleri requests/BeautifulSoup isteklerini engelleyebilir,
JavaScript ile içerik yükleyebilir veya ana sayfada kampanya linklerini
doğrudan göstermeyebilir.

Bu durumda terminalde:
- 403 / 429 hatası,
- "Aday link sayısı: 0",
- veya beklenenden çok az kayıt

görülebilir.

Böyle bir durumda mevcut kodu silme. Sorun çıkan bankalar için sonraki
adımda Playwright fallback eklenebilir.