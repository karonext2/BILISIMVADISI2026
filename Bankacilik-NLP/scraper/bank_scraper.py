import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime


class BankScraper:

    def __init__(self, banka_adi):
        self.banka = banka_adi

        self.headers = {
            "User-Agent": "Mozilla/5.0"
        }

        self.veriler = []

    def scrape(self, linkler):

        for i, url in enumerate(linkler, start=1):

            print(f"[{i}/{len(linkler)}] {url}")

            try:

                response = requests.get(
                    url,
                    headers=self.headers,
                    timeout=20
                )

                soup = BeautifulSoup(
                    response.text,
                    "html.parser"
                )

                baslik = ""

                if soup.title:
                    baslik = soup.title.get_text(strip=True)

                icerik = soup.get_text(
                    " ",
                    strip=True
                )

                self.veriler.append({

                    "banka": self.banka,
                    "url": url,
                    "baslik": baslik,
                    "icerik": icerik[:3000],
                    "erisim_tarihi": datetime.now().strftime("%Y-%m-%d")

                })

            except Exception as e:

                print("HATA:", e)

    def json_kaydet(self, dosya):

        with open(
            dosya,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                self.veriler,
                f,
                ensure_ascii=False,
                indent=4
            )

        print(f"\n{dosya} oluşturuldu.")
