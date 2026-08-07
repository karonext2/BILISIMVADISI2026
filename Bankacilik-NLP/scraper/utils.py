import json
import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def sayfayi_indir(url):
    """Verilen URL'nin HTML içeriğini indirir."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Hata: {url}")
        print(e)
        return None


def html_parse(html):
    """HTML'i BeautifulSoup nesnesine çevirir."""
    return BeautifulSoup(html, "html.parser")


def sayfa_basligi(soup):
    """Sayfa başlığını döndürür."""
    if soup.title:
        return soup.title.get_text(strip=True)
    return ""


def sayfa_metni(soup):
    """Sayfadaki metni temizleyerek döndürür."""
    return soup.get_text(" ", strip=True)


def json_kaydet(veri, dosya_adi):
    """Veriyi JSON olarak kaydeder."""
    with open(dosya_adi, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=4)
