# Mimari

```
┌─────────────┐     /api/v1/*      ┌──────────────────────────────────────┐
│  Frontend   │ ─────────────────► │  FastAPI  (api/main.py)               │
│ React+Vite  │   (Vite proxy)     │  ├─ v1/meta       GET banks/filters/  │
│ TS+Tailwind │                    │  │                  stats/health      │
│ 6 sayfa     │ ◄───────────────── │  ├─ v1/campaigns  GET list/detail    │
└─────────────┘   JSON + hata      │  ├─ v1/calculate  POST (saf motor)   │
                  zarfı            │  ├─ v1/compare    POST (aile farkında)│
                                   │  └─ v1/chat       POST (RAG+guardrail)│
                                   └──────┬───────────────┬───────────────┘
                                          │               │
                        ┌─────────────────▼──┐     ┌──────▼──────────────┐
                        │ data_layer         │     │ chatbot/chain.py    │
                        │ repository.py       │     │  (LCEL)             │
                        │  ► karonext.sqlite  │◄────┤  analiz→getir→      │
                        │  (TEK DOĞRU KAYNAK) │     │  hesapla/karşılaştır│
                        └─────────────────────┘     │  →yanıt→guardrail   │
                                  ▲                 └───┬────────────┬────┘
                                  │                     │            │
              ┌───────────────────┴──────┐    ┌─────────▼───┐  ┌────▼─────────┐
              │ calculations/finance.py  │    │ rag/        │  │ llm/base.py  │
              │  (anüite, saf, TAHMİNİ)  │    │ retriever   │  │ ChatOpenAI + │
              └──────────────────────────┘    │  +vectorstore│ │ Embeddings   │
                                              └──────┬──────┘  │  → EVREN     │
                                                     │         └──────┬───────┘
                                              ┌──────▼──────┐         │
                                              │ EVREN Qdrant│◄────────┘
                                              │ 2914 chunk  │  bge-m3-embed
                                              └─────────────┘
```

## İlkeler

1. **Tek doğru kaynak:** her yapılandırılmış kayıt `karonext.sqlite`'tan gelir.
   Qdrant yalnızca "hangi kayıt ilgili" sorusunu yanıtlar; içeriği SQLite verir.
2. **Sağlayıcı bağımsızlığı:** LLM/embedding erişimi `llm/base.py` arkasında.
   `LLM_BACKEND=local` kolu eklendiğinde üst katman değişmez.
3. **Deterministik çekirdek:** hesaplama ve karşılaştırma saf Python; LLM yalnızca
   dil işi yapar (soru anlama, yanıt yazma) ve sonuçları guardrail'den geçer.
4. **Hata izolasyonu:** kullanıcıya sabit Türkçe mesaj + `error_id`; teknik ayrıntı
   yalnızca maskeli log'a.
5. **Dış API opsiyonel:** listeleme/filtre/hesaplama EVREN'siz çalışır.

## Katmanlar

| Katman | Sorumluluk | Anahtar dosyalar |
|---|---|---|
| Sunum | React SPA, tip güvenli istemci | `frontend/src/` |
| API | HTTP, doğrulama, hata zarfı, response modelleri | `api/` |
| Servis | karşılaştırma, chatbot orkestrasyon | `services/`, `chatbot/` |
| Alan | hesaplama motoru, kanonik şema | `calculations/`, `schemas/` |
| Veri | SQLite repository, türetme | `data_layer/` |
| Bilgi çıkarımı | LLM extraction + normalizasyon | `nlp/` |
| Getirme | vektör deposu + retriever | `rag/`, `llm/` |
| Yapılandırma | ayarlar, log, hatalar | `core/` |
```
