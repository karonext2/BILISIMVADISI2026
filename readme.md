# KARONEXT — Katılım Bankacılığı Platformu

**Finansman • Kampanya • Karşılaştırma • Tahmini Hesaplama • Yapay Zekâ Asistanı**

TEKNOFEST Yapay Zekâ Dil Ajanları Yarışması — 2. Senaryo (Katılım Bankacılığı
Finansal Metin Analizi) için geliştirilmiştir.

---

## 1. Projenin amacı

Türkiye'deki 10 katılım bankasının resmî kaynaklarından derlenen finansman, ürün,
kampanya, kâr payı, vade, tutar, masraf, ödül ve tarih bilgilerini yapay zekâ / NLP
yöntemleriyle işleyerek kullanıcıya anlaşılır biçimde sunan bir platform.

Sistem yalnızca veri listelemez: **veriyi anlar → filtreler → karşılaştırır → uygun
durumda tahmini hesaplama yapar → sonucu açıklar → kaynağını gösterir → doğal dille
sorulan soruları yanıtlar.**

Temel ilke: **sıfır uydurma.** Oran, vade, tutar, masraf, ödül, tarih ve hesaplama
formülü asla üretilmez; veri yoksa "belirtilmemiş / kaynaklarda yok" denir.

---

## 2. Gereksinimler

- Python 3.11+ (test edildi: 3.13)
- Node.js 20+ / npm 10+
- EVREN erişimi: LLM API (`llm-fast`), embedding (`bge-m3-embed`), Qdrant — `.env`

---

## 3. Kurulum

```powershell
# --- Backend ---
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

Copy-Item .env.example .env       # sonra .env içine takım anahtarlarını girin

# --- Frontend ---
cd frontend
npm install
cd ..
```

`.env` git'e **yüklenmez** (`.gitignore`). Anahtarlar yalnızca ortam üzerinden verilir.

---

## 4. Klasör yapısı

```
KARONEXT_API/
├── api/                  FastAPI — v1 router'ları + hata yönetimi
│   ├── v1/               campaigns, calculate, compare, chat, meta
│   ├── schemas.py        response modelleri (teknik sızıntı önleme)
│   └── main.py
├── core/                 settings (BaseSettings), errors, logging (+ sır maskeleme)
├── data_layer/           SQLite tek erişim noktası
│   ├── db.py  derive.py  repository.py
├── schemas/record.py     KANONİK kayıt şeması (Pydantic)
├── nlp/                  extractor, normalizer, classifier, processor
│   └── prompts/          extraction_system.md, extraction_user.md
├── rag/                  vectorstore (QdrantVectorStore), retriever
├── llm/base.py           sağlayıcı soyutlaması (ChatOpenAI / OpenAIEmbeddings → EVREN)
├── calculations/         finance.py (saf anüite fonksiyonları), schemas.py
├── chatbot/              chain.py (LCEL), guardrails.py, prompts.py
├── services/             comparison.py, pipeline.py
├── scripts/
│   ├── check_connectivity.py   EVREN + Qdrant testi
│   ├── chunk_dataset.py        JSON → 800/150 karakter chunk'lar
│   ├── 02_build_db.py          jsonl → karonext.sqlite
│   └── 03_index.py             chunk'lar → EVREN Qdrant
├── data/
│   ├── input/kaynak_469.csv           ham veri (469 satır, 10 banka)
│   ├── processed/extracted_records.jsonl   NLP çıkarım ara ürünü (denetim izi)
│   ├── processed/chunks/                    RAG chunk'ları (2914)
│   └── final/karonext.sqlite                ► TEK DOĞRU KAYNAK (git dışı, üretilebilir)
├── frontend/            React + TS + Vite + Tailwind (6 sayfa)
├── docs/               PLAN.md, FORMULAS.md, DATA_DICTIONARY.md, ARCHITECTURE.md, DEMO.md
└── tests/              51 test
```

---

## 5. CSV veri seti

`data/input/kaynak_469.csv` — 469 satır, 9 sütun (`banka, banka_id, baslik, metin,
url, ana_etiket, alt_etiket, orijinal_kategori, kaynak`), UTF-8. 10 banka:
Albaraka Türk (95), Kuveyt Türk (95), Ziraat Katılım (74), Dünya Katılım (51),
Vakıf Katılım (36), Türkiye Finans (35), Adil Katılım (29), Türkiye Emlak Katılım (24),
Hayat Finans (23), TOM Bank (7).

Alan sözlüğü: **`docs/DATA_DICTIONARY.md`**

---

## 6. Model / LLM

- **Çıkarım (NLP):** EVREN `llm-fast` + strict JSON şema (`nlp/schemas.py`).
  Metinden `*_raw` finansal alanları çıkarır; `nlp/normalizer.py` sayısala çevirir.
- **Embedding:** EVREN `bge-m3-embed` (1024 boyut) — RAG.
- **Sağlayıcı soyutlaması:** `llm/base.py`. `LLM_BACKEND` / `EMBEDDING_BACKEND`
  anahtarları hazır; lokal `.safetensors` modele geçiş için yalnızca `local` kolu
  eklenecek (kod geri kalanı değişmez). Dış API **zorunlu bağımlılık değildir**.

---

## 7. Veri hattı (idempotent, tek yönlü)

```
data/input/kaynak_469.csv              data/input/karsilastirma_tablosu.csv
   │  (opsiyonel) process_dataset.py       (44 satır, elle küratörlenmiş)
   ▼                                            │
data/processed/extracted_records.jsonl         │
   │  python scripts/02_build_db.py  ◄──────────┘  (BOŞ finansal alanları tablodan doldurur)
   ▼
data/final/karonext.sqlite   ◄── dashboard + karşılaştırma + RAG buradan okur
   │  python scripts/chunk_dataset.py                       # SQLite'tan ~2910 chunk
   │  python scripts/03_index.py --recreate                 # embed → EVREN Qdrant
   ▼
EVREN Qdrant  (~2910 nokta)
```

`data/input/karsilastirma_tablosu.csv` — 10 banka × 5 ürün kategorisi için elle
derlenmiş oran/vade/tutar/avantaj tablosu. `02_build_db.py` her kaydı bu tabloyla
eşleştirir (banka + ürün adı) ve LLM çıkarımının **boş bıraktığı** finansal alanları
buradan doldurur (dolu alanlara dokunmaz). 44 kayıt `kuratorlu=1` işaretlenir.

Hızlı başlangıç (veri zaten çıkarılmış):

```powershell
python scripts/check_connectivity.py     # 3/3 bileşen erişilebilir mi?
python scripts/02_build_db.py            # karonext.sqlite oluştur
python scripts/chunk_dataset.py          # chunk'lar
python scripts/03_index.py --recreate    # Qdrant'a yükle
```

---

## 8. Çalıştırma

```powershell
# Backend  ->  http://localhost:8000/docs
python run.py
#   veya: uvicorn api.main:app --host 0.0.0.0 --port 8000

# Frontend ->  http://localhost:5173
cd frontend
npm run dev
```

Frontend yalnızca `/api/v1/*` çağırır; EVREN/Qdrant anahtarını asla görmez
(Vite dev proxy `/api → :8000`).

---

## 9. API uçları (`/api/v1`)

| Uç | Açıklama | Kaynak |
|---|---|---|
| `GET /banks` | bankalar + kayıt/kampanya sayıları | SQLite |
| `GET /filters` | filtre değer kümeleri | SQLite |
| `GET /campaigns` | filtreli/sıralı/sayfalı listeleme | SQLite |
| `GET /campaigns/{id}` | detay + kaynak + hesaplama ön-değerleri | SQLite |
| `GET /stats` | özet kartlar + dağılımlar (dinamik) | SQLite |
| `POST /calculate` | tahmini finansman hesaplama motoru | saf matematik |
| `POST /compare` | seçili kayıtları karşılaştır (aile farkında) | SQLite |
| `POST /chat` | Katılım Bankacılığı Asistanı (RAG + tool) | EVREN + SQLite |
| `POST /search` | anlamsal ürün araması | EVREN Qdrant |
| `GET /health` | bileşen bazlı durum | — |

Listeleme uçları EVREN'e bağlanmaz → yapay zekâ servisi çökse bile dashboard çalışır.
Tüm hatalar tek zarf: `{ "hata": true, "mesaj": "<Türkçe>", "error_id": "..." }`.

---

## 10. Finansal hesaplama motoru

- **Yöntem:** Murabaha eşit taksitli (anüite) — tam formül ve varsayımlar:
  **`docs/FORMULAS.md`**
- Her sonuç **`"TAHMİNİ HESAPLAMA"`** etiketli; bankanın resmi teklifi/hesaplayıcısı
  ile karıştırılmaz (KURAL 11). KKDF/BSMV, sigorta, ekspertiz dahil değildir.
- Frontend'de tutar / vade / kâr payı **elle girilebilir** (slider + sayı input senkron);
  bir kampanyadan gelindiyse alanlar ön-doldurulur ama düzenlenebilir kalır.

---

## 11. Chatbot / RAG

Akış: `soru → analiz (niyet + banka + parametre) → RAG getirme (sunucu tarafı Qdrant
filtresi + skor eşiği) → gerekiyorsa hesapla / karşılaştır → yanıt (grounded) →
guardrail → kaynak`.

Guardrail'ler: boş sonuç kısa devre, yanıttaki sayıların bağlamda doğrulanması,
`faiz → kâr payı`, teknik terim süzgeci. Yanıt sözleşmesi:
`{yanit, kaynaklar[], hesaplama?, karsilastirma?, uyari?}`.

---

## 12. Testler

```powershell
pytest -q          # 51 test (EVREN erişilemezse ilgili entegrasyon testleri atlanır)
```

Kapsam: normalizer kenar durumları, hesaplama motoru (referans değerler + "TAHMİNİ"
etiketi), karşılaştırma (aile ayrımı), repository, API sözleşmesi (404/422 zarfı,
teknik sızıntı yok), retriever (sunucu tarafı filtre), chatbot grounding + halüsinasyon.

---

## 13. Demo senaryoları

**`docs/DEMO.md`** — 10 jüri senaryosu (dashboard açılışı, konut finansmanı filtresi,
banka karşılaştırma, hesaplama motoru, vade değişimi, "en düşük kâr payı", banka
karşılaştırma sorusu, ürün oranı sorusu, kaynak gösterimi, veride olmayan bilgi).

---

## 14. Bilinen sınırlar (MVP)

- NLP çıkarımı orijinal veri kümesiyle yapıldığından yalnızca ~40 kayıtta sayısal
  kâr payı oranı var. `scripts/process_dataset.py` ile tam yeniden çıkarım kapsamı
  artırır (469 LLM çağrısı).
- On-premise tam profil (lokal `.safetensors` model + lokal Qdrant + Docker) sonraki
  iterasyona bırakıldı; `llm/base.py` soyutlaması hazır.
- `~5` kayıtta ürün ailesi/oran ayrıştırması sınırda (pazarlama metni gürültüsü).

Ayrıntılı yol haritası: **`docs/PLAN.md`**
