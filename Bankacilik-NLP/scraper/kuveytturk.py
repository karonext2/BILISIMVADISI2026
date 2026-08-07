from utils import (
    sayfayi_indir,
    html_parse,
    sayfa_basligi,
    sayfa_metni,
    json_kaydet,
)

LINK_DOSYASI = "raw/kuveytturk_links.txt"

veriler = []

with open(LINK_DOSYASI, "r", encoding="utf-8") as f:
    linkler = [satir.strip() for satir in f if satir.strip()]

print(f"{len(linkler)} link okunuyor...\n")

for i, url in enumerate(linkler, start=1):

    print(f"[{i}/{len(linkler)}] {url}")

    html = sayfayi_indir(url)

    if html is None:
        continue

    soup = html_parse(html)

    veri = {
        "banka": "Kuveyt Türk",
        "url": url,
        "baslik": sayfa_basligi(soup),
        "icerik": sayfa_metni(soup)[:3000]
    }

    veriler.append(veri)

json_kaydet(veriler, "raw/kuveytturk.json")

print("\n===================================")
print(f"{len(veriler)} sayfa başarıyla kaydedildi.")
print("raw/kuveytturk.json oluşturuldu.")
