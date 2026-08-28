from __future__ import annotations

KAMPANYA_TURLERI = [
    "Finansman Kampanyası",
    "İhtiyaç Finansmanı Kampanyası",
    "Konut Finansmanı Kampanyası",
    "Taşıt Finansmanı Kampanyası",
    "Kart Kampanyası",
    "Alışveriş Puanı Kampanyası",
    "Yeni Müşteri Kampanyası",
    "Yatırım Ürünü Kampanyası",
    "Kampanya Değil",
    "Diğer",
]

# Şartnamedeki finansal bilgi alanlarına göre hazırlanmıştır.
FINANSAL_CIKARIM_SEMASI = {
    "type": "object",
    "properties": {
        "banka": {"type": ["string", "null"]},
        "urun_adi": {"type": ["string", "null"]},
        "kampanya_turu": {
            "type": "string",
            "enum": KAMPANYA_TURLERI,
        },
        "kar_payi_orani_raw": {"type": ["string", "null"]},
        "finansman_tutari_raw": {"type": ["string", "null"]},
        "finansman_orani_raw": {"type": ["string", "null"]},
        "vade_raw": {"type": ["string", "null"]},
        "taksit_sayisi_raw": {"type": ["string", "null"]},
        "tahsis_ucreti_raw": {"type": ["string", "null"]},
        "masraf_bilgisi": {"type": ["string", "null"]},
        "odul_miktari_raw": {"type": ["string", "null"]},
        "indirim_orani_raw": {"type": ["string", "null"]},
        "alisveris_puani_raw": {"type": ["string", "null"]},
        "kampanya_baslangic_tarihi": {"type": ["string", "null"]},
        "kampanya_bitis_tarihi": {"type": ["string", "null"]},
        "hedef_kitle": {
            "type": "array",
            "items": {"type": "string"},
        },
        "kampanya_kosullari": {
            "type": "array",
            "items": {"type": "string"},
        },
        "avantajlar": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": [
        "banka",
        "finansman_orani_raw",
        "urun_adi",
        "kampanya_turu",
        "kar_payi_orani_raw",
        "finansman_tutari_raw",
        "vade_raw",
        "taksit_sayisi_raw",
        "tahsis_ucreti_raw",
        "masraf_bilgisi",
        "odul_miktari_raw",
        "indirim_orani_raw",
        "alisveris_puani_raw",
        "kampanya_baslangic_tarihi",
        "kampanya_bitis_tarihi",
        "hedef_kitle",
        "kampanya_kosullari",
        "avantajlar",
    ],
    "additionalProperties": False,
}

CHAT_SEMASI = {
    "type": "object",
    "properties": {
        "yanit": {"type": "string"},
        "kullanilan_kayit_idleri": {
            "type": "array",
            "items": {"type": "string"},
        },
        "uyari": {"type": ["string", "null"]},
    },
    "required": ["yanit", "kullanilan_kayit_idleri", "uyari"],
    "additionalProperties": False,
}
