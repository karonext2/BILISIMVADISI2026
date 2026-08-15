from __future__ import annotations

import re
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "raw_kampanyalar.csv"
OUTPUT = ROOT / "etiketleme_kontrol.csv"


def normalize(s: str) -> str:
    s = str(s or "").lower()
    s = re.sub(r"\s+", " ", s).strip()
    return s


def oneri_uret(baslik: str, url: str):
    t = normalize(baslik)
    u = normalize(url)
    x = f"{t} {u}"

    # 1) Eğitimden tamamen çıkarılabilecek genel/liste/kurumsal sayfalar
    haric_patterns = [
        r"yatırımcı ilişkileri",
        r"yatirimci-iliskileri",
        r"hesaplama araçları",
        r"hesaplama-arac",
        r"döviz çevirici",
        r"doviz-cevir",
        r"e-devlet",
        r"iletişim",
        r"iletisim",
        r"insan kaynakları",
        r"insan-kaynaklari",
        r"kariyer",
        r"hakkımızda",
        r"hakkimizda",
    ]
    if any(re.search(p, x) for p in haric_patterns):
        return "", "haric", "Genel/kurumsal sayfa"

    # Genel kategori liste sayfaları: tek bir sınıfa eğitim örneği yapılmasın.
    generic_titles = [
        "finansmanlar",
        "finansman ürünleri",
        "finansman urunleri",
        "hesaplar",
        "kartlar",
        "kampanyalar",
        "kampanya",
    ]
    title_core = t.split("|")[0].strip()
    if title_core in generic_titles:
        return "", "haric", "Genel liste sayfası"

    # 2) Güçlü kategori kuralları — sadece başlık/URL üzerinden
    if re.search(r"konut finans|konut-finans|gayrimenkul finans", x):
        return "konut_finansmani", "otomatik", "Konut finansmanı ifadesi"

    if re.search(r"taşıt finans|tasit finans|taşıt-finans|tasit-finans|araç finans|arac finans", x):
        return "tasit_finansmani", "otomatik", "Taşıt/araç finansmanı ifadesi"

    if re.search(r"ihtiyaç finans|ihtiyac finans|ihtiyaç-finans|ihtiyac-finans", x):
        return "ihtiyac_finansmani", "otomatik", "İhtiyaç finansmanı ifadesi"

    if re.search(r"katılma hesab|katilma hesab|katılım hesab|katilim hesab", x):
        return "katilma_hesabi", "otomatik", "Katılma hesabı ifadesi"

    # Kart sayfası/kampanyası
    if re.search(r"\bkart\b|kartı|karti|kredi kart", x):
        return "kredi_karti", "otomatik", "Kart ifadesi"

    # Yatırım ürünleri
    if re.search(
        r"sukuk|kira sertifika|yatırım fon|yatirim fon|"
        r"altın hesab|altin hesab|gümüş|gumus|yatırım hesab|yatirim hesab",
        x
    ):
        return "yatirim", "otomatik", "Yatırım ürünü ifadesi"

    # 3) Mevcut 6 sınıfa uymayan ama gerçek sayfa olanlar:
    # Modelin her şeyi zorla 6 sınıftan birine atamaması için 'diger' öneriyoruz.
    diger_patterns = [
        r"proje finansmanı",
        r"proje-finans",
        r"iş finansmanı",
        r"is-finans",
        r"ticari finans",
        r"kurumsal finans",
        r"arsa finans",
        r"işyeri finans",
        r"isyeri finans",
        r"banka hesabı aç",
        r"müşterimiz olun",
        r"musterimiz-olun",
        r"haber",
        r"duyuru",
        r"rehber",
    ]
    if any(re.search(p, x) for p in diger_patterns):
        return "diger", "otomatik", "Mevcut 6 ana sınıfın dışında"

    # Kararsız örnekler elle kontrol edilecek.
    return "", "kontrol", "Başlık/URL tek başına yeterli değil"


def main():
    if not INPUT.exists():
        raise FileNotFoundError(f"Dosya bulunamadı: {INPUT}")

    df = pd.read_csv(INPUT)

    gerekli = {"banka", "banka_id", "baslik", "metin", "url"}
    eksik = gerekli - set(df.columns)
    if eksik:
        raise ValueError(f"Eksik sütunlar: {sorted(eksik)}")

    # Aynı URL/metin tekrarlarını kaldır.
    df = df.drop_duplicates(subset=["url"]).copy()
    df = df.drop_duplicates(subset=["metin"]).copy()

    # Çok kısa metinleri eğitim adayı yapma.
    df["metin"] = df["metin"].fillna("").astype(str)
    df["metin_uzunlugu"] = df["metin"].str.len()

    sonuc = df.apply(
        lambda r: oneri_uret(r.get("baslik", ""), r.get("url", "")),
        axis=1,
        result_type="expand",
    )
    sonuc.columns = ["onerilen_kategori", "durum", "etiket_notu"]

    df = pd.concat([df, sonuc], axis=1)

    df.loc[df["metin_uzunlugu"] < 150, ["onerilen_kategori", "durum", "etiket_notu"]] = [
        "", "haric", "Metin çok kısa"
    ]

    # Kullanıcının daha kolay kontrol etmesi için sıralama.
    durum_order = pd.Categorical(
        df["durum"],
        categories=["kontrol", "otomatik", "haric"],
        ordered=True,
    )
    df = df.assign(_durum_order=durum_order)
    df = df.sort_values(["_durum_order", "banka", "baslik"], na_position="last")
    df = df.drop(columns=["_durum_order"])

    df.to_csv(OUTPUT, index=False, encoding="utf-8-sig")

    print("\n=== ETİKETLEME ÖZETİ ===")
    print(f"Toplam satır: {len(df)}")
    print("\nDurum:")
    print(df["durum"].value_counts())
    print("\nOtomatik kategori önerileri:")
    print(
        df.loc[df["durum"] == "otomatik", "onerilen_kategori"]
        .value_counts()
    )
    print(f"\nDosya oluşturuldu: {OUTPUT}")
    print("\n'kontrol' satırlarını Excel'de gözden geçir.")
    print("'haric' satırları model eğitimine alınmayacak.")


if __name__ == "__main__":
    main()