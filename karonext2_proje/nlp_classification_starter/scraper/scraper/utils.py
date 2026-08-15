from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
}

def get_html(url: str, timeout: int = 25) -> str | None:
    try:
        r = requests.get(
            url,
            headers=HEADERS,
            timeout=timeout,
            allow_redirects=True,
        )
        r.raise_for_status()
        return r.text
    except requests.RequestException as exc:
        print(f"[HATA] {url}: {exc}")
        return None

def normalize_url(base_url: str, href: str) -> str | None:
    if not href:
        return None

    href = href.strip()

    if href.startswith(("mailto:", "tel:", "javascript:", "#")):
        return None

    full = urljoin(base_url, href)
    parsed_base = urlparse(base_url)
    parsed_full = urlparse(full)

    # www farkını tolere et
    base_host = parsed_base.netloc.lower().removeprefix("www.")
    full_host = parsed_full.netloc.lower().removeprefix("www.")

    if full_host and full_host != base_host:
        return None

    return full.split("#")[0]

def linkleri_topla(base_url: str, keywords: list[str], limit: int = 250) -> list[str]:
    html = get_html(base_url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    found = set()

    for a in soup.find_all("a", href=True):
        label = " ".join(a.stripped_strings)
        href = a.get("href", "")
        combined = f"{label} {href}".lower()

        if any(k.lower() in combined for k in keywords):
            full = normalize_url(base_url, href)
            if full:
                found.add(full)

        if len(found) >= limit:
            break

    return sorted(found)

def sayfa_metni_cek(url: str) -> tuple[str, str] | None:
    html = get_html(url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    for tag in soup([
        "script", "style", "noscript", "svg",
        "header", "footer", "nav", "form"
    ]):
        tag.decompose()

    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()

    content = (
        soup.find("main")
        or soup.find("article")
        or soup.find(attrs={"role": "main"})
        or soup.body
        or soup
    )

    text = " ".join(content.stripped_strings)
    text = re.sub(r"\s+", " ", text).strip()

    # Navigasyon/boş sayfa gibi çok kısa içerikleri alma.
    if len(text) < 150:
        return None

    # Aşırı uzun sayfaları başlangıçta kontrol altında tut.
    if len(text) > 30000:
        text = text[:30000]

    return title, text