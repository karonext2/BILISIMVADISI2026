# Katılım Bankacılığı Odaklı NLP ve Finansal Analiz Projesi
**TEKNOFEST Yapay Zekâ Dil Ajanları Kategorisi**

---

## 1. Proje ve Veriseti Amacı
Bu veriseti; katılım bankacılığı (faizsiz bankacılık) alanındaki doğal dil işleme (NLP), bilgi çıkarma (information extraction) ve niyet/özellik (intent/entity extraction) tespiti görevlerini test etmek, değerlendirmek ve geliştirmek amacıyla özel olarak tasarlanmıştır. Geleneksel faizli bankacılık terminolojisinden farklı olan İslami finans prensiplerinin (Murabaha, Sukuk, Kâr-Zarar Ortaklığı vb.) dil ajanları tarafından doğru yorumlanmasını sağlar.

---

## 2. Manuel Etiketleme Alanları (Features) ve Anlamları
Test setinde yer alan ve model eğitimi/değerlendirmesinde etiketlenecek sütunlar ve açıklamaları:

* **ID:** Kaydın benzersiz tanımlayıcısı (1 - 20 arası).
* **Banka:** Ürünün veya kampanyanın ait olduğu katılım bankası (Kuveyt Türk, Albaraka Türk, Türkiye Finans, Vakıf Katılım, Ziraat Katılım, Emlak Katılım).
* **Ürün / Kampanya Adı:** Bankanın resmi dijital veya şube kanallarında sunduğu ürün/kampanya adı.
* **Kâr Payı Oranı:** Ürünün faizsiz finansman yapısındaki getiri veya maliyet oranını belirtir (%0, kâr payı, murabaha marjı, değişken havuz getirisi vb.).
* **Finansman Tutarı:** Ürünün alt/üst limitlerini veya harcama gereksinimini ifade eder (örn. Min. 1.000 TL, 140.000 TL'ye kadar).
* **Vade:** Kampanya veya finansmanın geri ödeme ya da geçerlilik süresini gösterir (örn. 3 Ay, 36 Aya Varan).
* **Masraf:** Dosya masrafı, komisyon veya ek ücret durumunu özetler (örn. Yok, Dosya Masrafsız).
* **Ödül:** Kampanyanın müşteriye sağladığı maddi/manevi avantajı (bonus, mil, indirim, kâr payı, taksit avantajı) açıklar.
* **Kampanya Süresi:** Teklifin geçerlilik aralığını belirtir (örn. Dönemsel, Yıl Boyu / Sürekli).
* **Hedef Müşteri:** Ürünün hitap ettiği kitleyi tanımlar (örn. Sağlık Profesyonelleri, Seyahat Severler).
* **Kampanya Koşulları:** Yararlanmak için yerine getirilmesi gereken ön şartları listeler.

---

## 3. TEKNOFEST Yarışmasında Kullanım Senaryoları
* **Dil Ajanları Mimarisi:** Kullanıcıların bankacılık ürünleriyle ilgili karmaşık sorgularına faizsiz finans ilkelerine uygun akıllı yanıtlar üretilmesi.
* **Varlık Çıkarımı (NER):** Kullanıcı metinleri içerisinden vade, tutar, kâr payı oranı ve kampanya koşullarının otomatik olarak parse edilmesi.
* **RAG (Retrieval-Augmented Generation):** Doğru bağlam eşleme ve katılım bankacılığı ürün karşılaştırma algoritmaları için altın veri seti (golden dataset) olarak kullanılması.

---

## 4. Veriseti Yapısı ve Kullanım
* **Dosya Formatı:** `Katilim_Bankaciligi_Test_Seti.xlsx`
* **Kapsam:** 20 adet seçilmiş gerçek katılım bankacılığı ürünü ve kampanyası.
* **Versiyon:** v1.0 (2026)