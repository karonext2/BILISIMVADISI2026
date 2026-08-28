# Jüri Demo Senaryoları

Ön koşul: backend (`python run.py`) + frontend (`cd frontend && npm run dev`) çalışıyor,
`karonext.sqlite` oluşturulmuş ve Qdrant indekslenmiş.

---

### Senaryo 1 — Dashboard açılışı (dinamik sayılar)
**Adım:** `http://localhost:5173` aç.
**Beklenen:** Özet kartlar veri kümesinden anlık hesaplanır: Toplam Banka **10**,
Toplam Kayıt **469**, Toplam Kampanya **108**, Aktif Kampanya (bugüne göre),
"Son Veri Güncelleme: 27 Ağustos 2026". Ürün ailesi ve banka dağılım barları görünür.
Hiçbir sayı sabit değildir.

### Senaryo 2 — Konut finansmanı filtresi
**Adım:** "Finansman & Kampanyalar" → Ürün ailesi: *Finansman*, Ara: `konut`.
**Beklenen:** Yalnızca konut finansmanı ürünleri listelenir (Albaraka Türk, Vakıf
Katılım, Ziraat Katılım, Türkiye Finans …). Sıralama "Kâr payı (artan)" seçilince en
düşük orandan sıralanır.

### Senaryo 3 — İki banka karşılaştırma
**Adım:** "Karşılaştırma" → `konut finansmanı` ara → iki farklı bankanın ürününü seç →
"Karşılaştır".
**Beklenen:** Kriter × ürün tablosu (Kâr payı / Vade / Tahsis ücreti / Ödül / Finansman
tutarı). "Kriter Bazında Öne Çıkanlar" + **"Neden bu sonuç?"** açıklaması gerçek veriden
üretilir. Farklı ürün aileleri seçilirse kâr payı kıyaslanmaz + uyarı gösterilir.

### Senaryo 4 — Hesaplama motoru
**Adım:** "Finansman Hesaplama" → Tutar **500.000 TL**, Vade **60 ay**, Kâr Payı
**%1,89** (aylık) → "Hesapla".
**Beklenen:** Tahmini Aylık Ödeme ≈ **14.003,46 TL**, Toplam Geri Ödeme ve Toplam Kâr
Payı gösterilir. Sarı **"Tahmini Hesaplama — bankanın resmi teklifi değildir"** kutusu +
açılır ödeme planı tablosu (60 taksit, son taksitte kalan 0).

### Senaryo 5 — Vade değişince sonuç değişir
**Adım:** Aynı ekranda vade kaydırıcısını **36 ay**'a çek → "Hesapla".
**Beklenen:** Aylık ödeme artar, toplam kâr payı azalır. Değerler elle de girilebilir
(slider ve sayı input senkron).

### Senaryo 6 — "En düşük kâr payı hangi bankada?"
**Adım:** "Asistan" → *"En düşük kâr payı hangi bankada konut finansmanında?"*
**Beklenen:** Vakıf Katılım (Konut Finansmanı Paketi, %2,99–%3,38 aylık) öne çıkar;
diğer bankaların oranları listelenir; oran verisi olmayanlar "belirtilmemiş" denir.
Altında kaynak kartları + veri tarihi + güncel bilgiyi bankadan teyit uyarısı.

### Senaryo 7 — Banka karşılaştırma sorusu (doğal dil)
**Adım:** "Asistan" → *"Kuveyt Türk ile Türkiye Finans'ı konut finansmanında karşılaştır."*
**Beklenen:** İki bankanın getirilen kayıtları üzerinden kriter bazlı karşılaştırma +
"neden bu sonuç" + kaynaklar.

### Senaryo 8 — Ürün oranı sorusu
**Adım:** "Asistan" → *"Albaraka Türk'ün taşıt finansmanı oranı nedir?"*
**Beklenen:** Kayıtta oran varsa ham ifadeyle verilir + kaynak; yoksa "bu bilgi
elimdeki kaynaklarda yer almıyor" denir. Uydurulmaz.

### Senaryo 9 — Kaynak gösterimi
**Adım:** Herhangi bir asistan yanıtındaki kaynak kartına tıkla.
**Beklenen:** İlgili kampanya detay sayfası açılır; "Kaynak" bölümünde banka, veri
tarihi ve orijinal URL bulunur.

### Senaryo 10 — Veride olmayan bilgi
**Adım:** "Asistan" → *"Mars Bankası'nın kripto para kâr payı oranı nedir?"*
**Beklenen:** *"Bu bilgi mevcut veri kaynaklarında bulunamadı"* benzeri yanıt; sahte
banka/oran üretilmez, kaynak listesi boş.

### Ek — Hesaplama motoru + Asistan birlikte
**Adım:** "Asistan" → *"500.000 TL konut finansmanını 60 ayda hangi oranla, aylık kaç
TL öderim?"*
**Beklenen:** Asistan getirilen bir finansman kaydının oranını **kaynağını belirterek**
kullanır, hesaplama motorunu çağırır, sonucu **"tahmini"** ve **"bankanın resmi teklifi
değildir"** notuyla verir.
