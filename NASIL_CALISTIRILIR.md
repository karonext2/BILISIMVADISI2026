# KARONEXT — Dashboard'a Nasıl Erişilir?

Bu proje bir **web uygulaması**dır (React frontend + FastAPI backend). Tek bir
dosyayı çift tıklayarak açılmaz — iki sunucunun çalışıyor olması ve tarayıcıdan
bir adrese gidilmesi gerekir.

---

## 1. Backend'i başlat

Proje klasöründe (KARONEXT_API içinde) bir terminal aç:

```powershell
.\.venv\Scripts\Activate.ps1
python run.py
```

Şunu görmelisin: `Uvicorn running on http://0.0.0.0:8000`

Backend API dokümanları: **http://localhost:8000/docs**

---

## 2. Frontend'i başlat

Backend çalışırken, **başka bir terminal** aç:

```powershell
cd frontend
npm run dev
```

Şunu görmelisin: `Local: http://localhost:5173/`

---

## 3. Dashboard'a eriş

Tarayıcını aç, adres çubuğuna şunu yaz:

**http://localhost:5173**

Bu kadar. Backend + frontend ikisi de açık kaldığı sürece dashboard çalışır.
Terminalleri kapatırsan sunucular durur, dashboard erişilemez hale gelir.

---

## Sık karşılaşılan sorunlar

- **"Bağlanılamıyor" hatası** → Backend veya frontend terminali kapanmış olabilir,
  1. ve 2. adımları tekrar çalıştır.
- **"Port zaten kullanımda" hatası** → Zaten bir kopyası çalışıyor demektir,
  yenisini başlatmana gerek yok, direkt tarayıcıdan http://localhost:5173 dene.
- **Veriler eski görünüyor** → Backend'i kapatıp (Ctrl+C) yeniden başlat
  (`python run.py`), veritabanı her açılışta yeniden okunur.
