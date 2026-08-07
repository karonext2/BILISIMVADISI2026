# Bankacilik-NLP

## Proje Hakkında

Bu proje, Türkiye'deki katılım bankalarının ürün ve kampanya sayfalarından veri toplamak amacıyla geliştirilmiştir.

Web scraping işlemleri Python kullanılarak gerçekleştirilmiştir. Toplanan veriler JSON ve CSV formatlarında kaydedilmiş, temel veri temizleme işlemleri uygulanmıştır.

---

## Kullanılan Teknolojiler

- Python 3
- Requests
- BeautifulSoup4
- Pandas
- JSON

---

## Proje Yapısı

```
Bankacilik-NLP
│
├── scraper/
│   ├── utils.py
│   ├── bank_scraper.py
│   ├── kuveytturk.py
│   └── link_toplayici.py
│
├── raw/
│   └── kuveytturk.json
│
├── clean/
│   ├── clean_data.py
│   └── kuveytturk.csv
│
├── reports/
│   └── hata_raporu.txt
│
├── requirements.txt
├── README.md
└── main.py
```

---

## Kullanılan Kütüphaneler

Kurulum için:

```bash
pip install -r requirements.txt
```

---

## Çalıştırma

Link toplama:

```bash
py scraper\link_toplayici.py
```

Veri toplama:

```bash
py scraper\kuveytturk.py
```

Veri temizleme:

```bash
py clean\clean_data.py
```

---

## Üretilen Dosyalar

### Ham Veri

- raw/kuveytturk.json

### Temiz Veri

- clean/kuveytturk.csv

### Hata Raporu

- reports/hata_raporu.txt

---

## Toplanan Veriler

- Banka Adı
- Ürün/Kampanya
- Kategori
- URL
- Sayfa Başlığı
- Sayfa İçeriği
- Telefon Bilgisi
- E-posta Bilgisi
- Erişim Tarihi

---

## Kullanılan Yöntem

- Requests ile web sayfaları indirildi.
- BeautifulSoup ile HTML içerikleri ayrıştırıldı.
- Pandas ile CSV dosyaları oluşturuldu.
- JSON formatında ham veri kaydedildi.
- Gereksiz boşluklar temizlendi.
- Telefon ve e-posta bilgileri düzenli ifadeler (Regex) kullanılarak çıkarıldı.

---

## Geliştirici

Bilgisayar Programcılığı - Web Scraping ve Veri Toplama Projesi
