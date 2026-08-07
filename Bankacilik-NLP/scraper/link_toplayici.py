import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.kuveytturk.com.tr"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(BASE_URL, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

anahtar_kelimeler = [
    "finansman",
    "hesap",
    "kart",
    "kampanya",
    "yatirim",
    "yatırım",
    "sigorta",
    "birikim"
]

linkler = set()

for a in soup.find_all("a", href=True):
    href = a.get("href")

    if not href:
        continue

    if href.startswith("/"):
        href = BASE_URL + href

    if "kuveytturk.com.tr" in href:
        if any(k in href.lower() for k in anahtar_kelimeler):
            linkler.add(href)

print(f"{len(linkler)} adet link bulundu.")

with open("raw/kuveytturk_links.txt", "w", encoding="utf-8") as dosya:
    for link in sorted(linkler):
        dosya.write(link + "\n")

print("Linkler raw klasörüne kaydedildi.")
