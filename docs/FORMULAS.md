# Finansal Hesaplama Motoru — Formül Dokümantasyonu

Şartname madde 14-21 ve KURAL 5 (hesaplama formülü uydurma yasağı) gereği, motorun
kullandığı yöntem burada açıkça tanımlanır. Motor kodu: `calculations/finance.py`
(saf fonksiyonlar, I/O yok).

## Yöntem: Murabaha eşit taksitli (anüite) ödeme planı

Katılım bankacılığında bireysel finansman (konut / taşıt / ihtiyaç) fiilen **sabit kâr
payı oranı ile eşit taksitli** işler. Ödeme planının matematiği kredi anüitesiyle
aynıdır; yalnızca terminoloji farklıdır ("faiz" değil **kâr payı**).

### Tanımlar

| Sembol | Anlam |
|---|---|
| `P` | Finansman tutarı (anapara), TL |
| `n` | Vade / taksit sayısı (ay) |
| `i` | Kâr payı oranı (%) — kullanıcı girişi |
| `r` | Aylık kâr payı oranı (ondalık) = `i / 100` (giriş aylıksa) |

Giriş **yıllık** ise: `r_aylık = (i / 12) / 100` — bankaların standart **basit bölme**
uygulaması. (Bileşik dönüşüm `(1+i)^(1/12)-1` kullanılmaz; bu, sektör pratiğiyle
uyumlu olması için bilinçli bir tercihtir ve burada belgelenmiştir.)

### Aylık taksit (eşit taksit)

`r > 0` için:

```
A = P · r · (1 + r)^n / ( (1 + r)^n − 1 )
```

`r = 0` özel durumu:

```
A = P / n
```

### Türetilen değerler

```
toplam_odeme     = A · n
toplam_kar_payi  = A · n − P
tahsis_ucreti    = tahsis_ucreti_tl        (verildiyse)
                 = P · tahsis_ucreti_orani / 100   (oran verildiyse)
toplam_maliyet   = toplam_odeme + tahsis_ucreti
```

### Ödeme planı (t = 1 … n)

Başlangıç kalan anapara `B₀ = P`:

```
kar_payi_t   = B_{t−1} · r
anapara_t    = A − kar_payi_t
B_t          = B_{t−1} − anapara_t
```

Son taksitte (`t = n`) yuvarlama artığını önlemek için `anapara_n = B_{n−1}` alınır ve
`B_n = 0` garanti edilir.

## Kapsam DIŞI (motor bunları hesaplamaz — yalnızca açıklamada belirtir)

- KKDF / BSMV (katılım finansmanında çoğunlukla yok, ama üründen bağımsız garanti edilemez)
- Hayat sigortası, DASK / konut sigortası
- Ekspertiz ücreti, ipotek / rehin tesis masrafı
- Peşinat / peşin ödeme

## Etiketleme kuralı (şartname madde 19, KURAL 11)

Her `CalculateResponse`:

- `etiket = "TAHMİNİ HESAPLAMA"` (zorunlu)
- `formul = "murabaha_esit_taksit_anuite"`
- `aciklama` = sabit metin: sonucun tahmini olduğu, bankanın resmi teklifi/hesaplayıcısı
  olmadığı, hangi masrafların dahil olmadığı.

Bu sonuç, kaynak veri setinden gelen resmî bir örnek ödeme planıyla **hiçbir zaman
aynı görünümde karıştırılmaz**. Kullanıcı isterse ilgili bankanın resmî finansman
hesaplama aracına yönlendirilir.

## Veri kaynağı (şartname madde 18)

Hesaplama parametreleri şu sırayla gelir:

1. **Kullanıcı elle girer** (birincil — hesaplama ekranı tüm alanları düzenlenebilir sunar).
2. Bir kampanya detayından gelindiyse, o kaydın veri setindeki değerleri forma
   **ön-doldurulur** (`GET /api/v1/campaigns/{id}` → `hesaplama_on_degerler`), ama yine
   düzenlenebilir kalır.

Motor, veri setinde bulunmayan hiçbir oranı/tutarı/vadeyi kendiliğinden **üretmez**.
