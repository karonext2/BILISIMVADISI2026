"""
Katılım bankaları için scraper yapılandırması.

Bu sürüm 10 banka için hazırlanmıştır.
"""

BANKALAR = {
    "adilkatilim": {
        "ad": "Adil Katılım",
        "base_url": "https://www.adilkatilim.com.tr",
    },
    "albaraka": {
        "ad": "Albaraka Türk",
        "base_url": "https://www.albaraka.com.tr",
    },
    "dunyakatilim": {
        "ad": "Dünya Katılım",
        "base_url": "https://www.dunyakatilim.com.tr",
    },
    "hayatfinans": {
        "ad": "Hayat Finans",
        "base_url": "https://hayatfinans.com.tr",
    },
    "kuveytturk": {
        "ad": "Kuveyt Türk",
        "base_url": "https://www.kuveytturk.com.tr",
    },
    "tombank": {
        "ad": "T.O.M. Bank",
        "base_url": "https://www.tombank.com.tr",
    },
    "emlakkatilim": {
        "ad": "Türkiye Emlak Katılım",
        "base_url": "https://www.emlakbank.com.tr",
    },
    "turkiyefinans": {
        "ad": "Türkiye Finans",
        "base_url": "https://www.turkiyefinans.com.tr",
    },
    "vakifkatilim": {
        "ad": "Vakıf Katılım",
        "base_url": "https://www.vakifkatilim.com.tr",
    },
    "ziraatkatilim": {
        "ad": "Ziraat Katılım",
        "base_url": "https://www.ziraatkatilim.com.tr",
    },
}

ANAHTAR_KELIMELER = [
    "kampanya",
    "kampanyalar",
    "finansman",
    "finansmanı",
    "finansmani",
    "konut",
    "ev",
    "taşıt",
    "tasit",
    "araç",
    "arac",
    "otomobil",
    "ihtiyaç",
    "ihtiyac",
    "kart",
    "kredi-karti",
    "kredi kartı",
    "katılma",
    "katilma",
    "hesap",
    "yatırım",
    "yatirim",
    "sukuk",
    "fon",
    "kira sertifikası",
    "kira-sertifikasi",
    "avantaj",
    "fırsat",
    "firsat",
    "indirim",
]