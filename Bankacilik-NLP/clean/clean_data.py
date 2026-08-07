import json
import pandas as pd
import re

# JSON dosyasını oku
with open("raw/kuveytturk.json", "r", encoding="utf-8") as f:
    veriler = json.load(f)

temiz_veriler = []

for veri in veriler:

    icerik = veri["icerik"]

    # Fazla boşlukları temizle
    icerik = re.sub(r"\s+", " ", icerik).strip()

    # Telefon numarası bul
    telefon = ""

    telefonlar = re.findall(
        r"(?:\+90\s?)?(?:0\s?)?\d{3}[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}",
        icerik
    )

    if telefonlar:
        telefon = telefonlar[0]

    # E-posta bul
    email = ""

    mailler = re.findall(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        icerik
    )

    if mailler:
        email = mailler[0]

    # Kategori belirle
    kategori = "Diğer"

    url = veri["url"].lower()

    if "finansman" in url:
        kategori = "Finansman"

    elif "hesap" in url:
        kategori = "Hesap"

    elif "kart" in url:
        kategori = "Kart"

    elif "kampanya" in url:
        kategori = "Kampanya"

    elif "yatirim" in url or "yatırım" in url:
        kategori = "Yatırım"

    elif "sigorta" in url:
        kategori = "Sigorta"

    temiz_veriler.append({

        "banka": veri["banka"],
        "url": veri["url"],
        "baslik": veri["baslik"],
        "kategori": kategori,
        "telefon": telefon,
        "email": email,
        "icerik": icerik[:1500]

    })

df = pd.DataFrame(temiz_veriler)

df.to_csv(
    "clean/kuveytturk.csv",
    index=False,
    encoding="utf-8-sig"
)

print(df.head())

print("\nCSV başarıyla oluşturuldu.")
