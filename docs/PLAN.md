# KARONEXT — Geliştirme Planı (MVP: P0 + P1)

> **Durum (2026-08-28): Aşama 0–9 tamamlandı.** 60 test geçiyor, frontend + backend
> bağlı, EVREN LLM + RAG entegre, hesaplama motoru ve dashboard çalışıyor.
> MVP dışı maddeler (Docker, lokal safetensors, ~50 test, CI, eval/) bir sonraki iterasyon.


Tarih: 2026-08-28
Kararlar (kullanıcı onayı):
- **LLM/RAG sağlayıcısı:** `.env`'deki EVREN (`llm-fast`, `bge-m3-embed`, EVREN Qdrant) + sağlayıcı
  soyutlama katmanı (ileride lokal `.safetensors` modele geçilebilir).
- **Kapsam:** Önce uçtan uca çalışan MVP (kritik hatalar + veri katmanı + backend endpoint'leri +
  finansal hesaplama motoru + LangChain RAG/chatbot + React dashboard).
- **Konum:** Mevcut `KARONEXT_API/` klasörü içinde (büyük yeniden yapılandırma yok).
- **Süreç:** Her aşama sonunda PDF madde 54 formatında özet + onay bekleme.

Referans: `scratchpad/REVIEW_AI.md`, `scratchpad/REVIEW_SWE.md`, `scratchpad/CONTEXT.md`, PDF (56 madde).

---

## Hedef mimari (MVP)

```
data/raw/kaynak_469.csv
   │ scripts/01_extract.py   (opsiyonel — LLM ile yeniden çıkarım; MVP'de atlanır)
   ▼
data/processed/extracted_records.jsonl   (mevcut ara ürün, *_raw alanlar burada)
   │ scripts/02_build_db.py   (düzeltilmiş normalizer + Pydantic Record doğrulama)
   ▼
data/final/karonext.sqlite   ◄── TEK DOĞRU KAYNAK
   ├──► FastAPI  /api/v1/{banks,filters,campaigns,campaigns/{id},stats,calculate,compare}   (SQL, EVREN'siz)
   ├──► scripts/03_index.py  → chunk embed (EVREN) → EVREN Qdrant   (record_id + minimal payload)
   └──► LangChain retriever + chatbot  /api/v1/chat   (EVREN)
        ▼
   frontend/ (React + TS + Vite + Tailwind)  →  yalnızca /api/v1/* çağırır
```

Katılım bankacılığı terminolojisi (kâr payı, finansman), Türkçe UI, teknik terim yok,
"TAHMİNİ HESAPLAMA" etiketi, kaynak gösterimi, sıfır uydurma.

---

## Aşamalar

### Aşama 0 — Ortam & güvenlik  (P0)
- `.gitignore` (`.venv/`, `.env`, `__pycache__/`, `*.pyc`, `data/final/`, `node_modules/`, `frontend/dist/`).
- `.venv` sil, Python 3.13 ile temiz kur (sistem sürümü; LangChain/transformers 3.13 tekerlekleri
  doğrulanacak, sorun çıkarsa 3.11).
- `requirements.txt` genişlet: `numpy`, `langchain`, `langchain-core`, `langchain-openai`,
  `langchain-community`, `langchain-qdrant`, `httpx`, `python-multipart`, `pytest-asyncio`.
- `backend` için `core/config.py` → Pydantic `BaseSettings` (mevcut `config.py` sarmalanır).
- `scripts/check_connectivity.py` — EVREN `/models` + Qdrant `collection_exists` testi
  (anahtar `.env`'den, komut satırına yazılmaz). Sonuç bu dosyaya raporlanır.
- **Güvenlik notu:** `.env` anahtarları bu makinede/incelemede görülmüş sayılır; kullanıcı
  yarışma sonrası rotate etmeli. MVP'de mevcut anahtarlarla devam.

### Aşama 1 — Kırık NLP hattını onar  (P0)
- `nlp/normalizer.py`: `normalize_extraction` → `out = dict(raw)` başa, çift `finansman_orani` sil.
  Kenar durumlar: karışık birim vade (`6 ay - 2 yıl`), çoklu sayı taksit — birim-farkında ayrıştırma.
- `nlp/schemas.py` → `nlp/schemas.py` içinde **Pydantic** `FinansalCikarim` modeli (tek kaynak),
  `model_json_schema()` ile strict şema üretilir (elle senkron dict kalkar).
- `nlp/extractor.py`:
  - Prompt gövdesini `nlp/prompts/extraction_system.md` + `extraction_user.md` dosyalarına taşı;
    f-string kaldır, `metin`/`banka`/`baslik` güvenli enjeksiyon (`str.replace`/`Template`).
  - Prompt'u düz şemaya hizala: iç içe `{value, confidence}` ve ~900 satırlık şema bölümü silinir;
    "güven düşükse null" kuralı korunur, ayrı confidence alanı istenmez. `max_tokens` 6000.
  - Retry: başarısızlıkta prompt'u **kısalt**, uzatma.
- `nlp/classifier.py`: ikinci LLM çağrısı riskini not düş (kullanılmıyor).
- **Veri:** MVP'de 469 kaydı yeniden LLM'e sokmak yerine mevcut `extracted_records.jsonl`'daki
  `*_raw` alanları **düzeltilmiş normalizer**'dan geçir → kanonik alanlar üretilir (ücretsiz, hızlı).
  Tam yeniden çıkarım (`01_extract.py`) ayrı, opsiyonel bir aşama olarak sunulur.

### Aşama 2 — Tek veri katmanı: SQLite  (P0→P1)
- `schemas/record.py` — kanonik `Record` Pydantic modeli. Yeni türetilmiş alanlar:
  `urun_ailesi` (finansman|mevduat|kart|yatirim|diger), `kar_payi_turu` (aylik|yillik_tns|bilinmiyor),
  `kar_payi_orani_min/max`, `finansman_tutari_min/max`, `vade_min_ay/max_ay`, `aktif_mi`
  (bitiş tarihine göre), liste alanları gerçek dizi, `NaN`→`null`.
- `scripts/02_build_db.py` — `extracted_records.jsonl` → normalize+doğrula → `data/final/karonext.sqlite`
  (`records` tablosu + liste alanları JSON1). Geçmeyen kayıt → `errors.jsonl`.
- `data/repository.py` — SQLite'a **tek erişim noktası** (dashboard + ingest + chatbot burada birleşir;
  şartname KURAL 9). Filtre/sayfalama/aggregate SQL fonksiyonları.
- `config.PROCESSED_CSV` kaldırılır.

### Aşama 3 — Backend: dashboard endpoint'leri + hata yönetimi  (P1)
- `core/errors.py` — domain exception'lar + global `@app.exception_handler`; kullanıcıya sabit
  Türkçe mesaj + `error_id`; ayrıntı yalnızca structured log'a (secret maskeleme).
  `RequestValidationError` Türkçeleştirilir. Hata zarfı: `{"hata": true, "mesaj": "...", "error_id": "..."}`.
- `api/v1` router'ları (hepsi SQLite'tan, EVREN'siz):
  - `GET /api/v1/banks` — bankalar + kayıt/kampanya sayıları
  - `GET /api/v1/filters` — filtre değer kümeleri (banka, kampanya türü, ürün ailesi, vade/kâr payı aralığı)
  - `GET /api/v1/campaigns` — sayfalı/filtreli/sıralı listeleme
  - `GET /api/v1/campaigns/{record_id}` — detay + kaynak + `hesaplama_yapilabilir_mi` + eksik alanlar
  - `GET /api/v1/stats` — özet kartlar + dağılım grafikleri + `guncelleme_tarihi` (veriden)
- Tüm response'lar Pydantic `response_model` ile sabit (teknik sızıntı önleme).
- `GET /api/v1/health` — bileşen bazlı (`veri_katmani`, `llm`, `vektor_db`).
- CORS whitelist (`CORS_ORIGINS` env), `allow_methods=["GET","POST"]`. Input `max_length`.

### Aşama 4 — Finansal hesaplama motoru  (P1)
- `calculations/finance.py` — **saf** fonksiyonlar (I/O yok, LLM yok):
  `aylik_taksit(P,n,r)`, `odeme_plani(P,n,r)`, `yillik_to_aylik(r)`, `hesapla(req)`.
  Yöntem: **Murabaha eşit taksitli (anüite)** — `A = P·r·(1+r)^n / ((1+r)^n − 1)`, `r=0` → `P/n`.
- `calculations/schemas.py` — `CalculateRequest` / `CalculateResponse`.
- `POST /api/v1/calculate` — elle giriş; opsiyonel `kaynak_record_id` ile ön-doldurma izi.
  Yanıtta zorunlu `etiket: "TAHMİNİ HESAPLAMA"`, `formul`, sabit `aciklama` (KKDF/BSMV/sigorta/
  ekspertiz hariç; bankanın resmi teklifi değildir).
- `docs/FORMULAS.md` — formül + varsayımlar + kapsam dışı (şartname madde 14-21).

### Aşama 5 — Karşılaştırma  (P1)
- `services/comparison.py` revize: `urun_ailesi`'ne göre filtre; mevduat (getiri, yüksek=iyi) ile
  finansman (maliyet, düşük=iyi) **ayrı**; farklı aile seçilirse `uyari`.
- `POST /api/v1/compare` — `{record_idler: [...], urun_ailesi?}`; en düşük kâr payı / en uzun vade /
  en düşük tahsis / en yüksek ödül + "neden bu sonuç" açıklaması (gerçek veriden).

### Aşama 6 — LangChain RAG  (P1)
- `llm/base.py` (`LLMProvider` Protocol) + `llm/evren.py` (`ChatOpenAI(base_url=EVREN)`).
  İleride `llm/local.py`.
- `rag/embeddings.py` — EVREN `bge-m3-embed` (OpenAI-uyumlu embeddings) LangChain `Embeddings` sarmalayıcı.
- `rag/vectorstore.py` — `QdrantVectorStore` (EVREN Qdrant, team prefix).
- `scripts/03_index.py` — `data/processed/chunks/` (2914 chunk) → embed → Qdrant upsert
  (payload: `record_id`, `banka`, `urun_ailesi`, `kampanya_turu`). `rag/embedding.py`'deki
  "chunk'ları tek vektöre ortala" mantığı kaldırılır (chunk-başına indeksleme).
- `rag/retriever.py` — `vectorstore.as_retriever(search_type="mmr", filter=<banka server-side>)`
  + score eşiği; sonuç `record_id`'ye dedup → `repository`'den tam kayıt.

### Aşama 7 — LangChain Chatbot  (P1)
- `chatbot/chain.py` — LCEL: `soru → (banka/tür/parametre çıkarımı) → retrieve → [gerekiyorsa] hesapla
  → yanıt → guardrail → kaynak`.
- Tool'lar: `retrieve_products`, `compare_products` (→ Aşama 5), `estimate_installment` (→ Aşama 4,
  çıktı "TAHMİNİ" etiketli).
- `chatbot/guardrails.py` — boş retrieval kısa devre ("Elimdeki verilerde bu bilgi yok"),
  yanıttaki `%`/`TL`/`ay` sayılarını context ile doğrula, `uyari` alanını doldur, teknik terim filtresi,
  "faiz"→"kâr payı" kontrolü.
- `POST /api/v1/chat` yeni sözleşme: `{yanit, kaynaklar:[{banka,urun_adi,url}], hesaplama?, uyari?}`.
  Ham `retrieved` blob'u kaldırılır. Dashboard filtre bağlamı opsiyonel `filtre` alanıyla geçirilir (madde 34).

### Aşama 8 — React Dashboard  (P1→P2)
- `frontend/` — Vite + React + TypeScript + Tailwind. `src/api/client.ts` tek fetch katmanı.
  Dev'de Vite proxy `/api → :8000`.
- Sayfalar (PDF madde 37):
  1. **Ana Sayfa** — başlık + açıklama + 4 ana işlem + `GET /stats` özet kartları (dinamik) + dağılım grafikleri.
  2. **Kampanyalar** — `FilterBar` (banka, tür, ürün ailesi, vade, kâr payı, aktif) + `CampaignTable`/kart ızgarası + sayfalama.
  3. **Kampanya Detayı** — tüm alanlar; veri yoksa "Belirtilmemiş"; "Kaynak" bölümü (banka, URL, veri tarihi); "Bu kampanya için hesapla" butonu.
  4. **Finansman Hesaplama** — **elle girilebilir** tutar/vade/kâr payı (slider + sayı input, ikisi senkron), oran periyodu seçimi, opsiyonel tahsis ücreti; "Hesapla" → aylık ödeme / toplam ödeme / toplam kâr payı + ödeme planı tablosu; sarı "TAHMİNİ HESAPLAMA — bankanın resmi teklifi değildir" kutusu.
  5. **Karşılaştırma** — kampanya seç (2+), tablo (kriter × kampanya), "neden bu sonuç".
  6. **Katılım Bankacılığı Asistanı** — sohbet; kaynak kartları; hesaplama sonucu gömülü; aktif dashboard filtresini bağlam olarak gönderir.
- Türkçe karakterler, katılım terminolojisi, teknik terim yok, responsive (mobil karşılaştırma tablosu kaydırmalı), kullanıcı teknik hata görmez.

### Aşama 9 — README + temel testler + demo
- `README.md` (PDF madde 52 başlıkları): amaç, kurulum, klasör yapısı, veri sözlüğü, model/LLM,
  dashboard/chatbot/RAG/hesaplama çalıştırma, testler, demo senaryoları (PDF madde 51, 10 senaryo).
- `tests/` — normalizer kenar durumları, `finance.py` (referans değerler + "TAHMİNİ" etiketi),
  comparison (aile ayrımı), `/calculate` ve `/campaigns` API sözleşmesi, chatbot grounding (mock).
- `docs/DATA_DICTIONARY.md`, `docs/ARCHITECTURE.md`.

---

## MVP dışı (sonraki iterasyon)
Docker + `docker-compose.local.yml` tam on-premise profil; lokal `.safetensors` model
(`models/loader.py`); lokal `bge-m3` + lokal Qdrant; cross-encoder reranker; LangGraph durum makinesi;
~50 testlik tam suit + CI (`ruff`, `mypy`, `pip-audit`, coverage eşiği); `eval/` (gold çıkarım seti,
retrieval Recall@k/MRR, halüsinasyon probe, `ragas`); tam klasör restructure (`backend/ frontend/`);
tam 469 kayıt LLM ile yeniden çıkarım.

---

## Aşama sonu onay formatı (PDF madde 54)
Her aşama sonunda: Ne yaptık? · Hangi dosyalar değişti? · Hangi veriyi kullandık? ·
Şartnameye katkısı · Puana katkısı · Sonraki aşama.
