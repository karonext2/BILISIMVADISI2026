from __future__ import annotations

from nlp.normalizer import (
    normalize_percentage,
    normalize_amount_tl,
    normalize_term_months,
)
from services.comparison import compare_records

def main():
    assert normalize_percentage("%2,05") == 2.05
    assert normalize_percentage("2.05 %") == 2.05
    assert normalize_amount_tl("1.500.000 TL") == 1500000.0
    assert normalize_amount_tl("1.500,50 TL") == 1500.50
    assert normalize_term_months("120 aya kadar") == 120
    assert normalize_term_months("10 yıl") == 120

    records = [
        {
            "record_id": "A",
            "banka": "A Bankası",
            "urun_adi": "Konut Finansmanı",
            "kar_payi_orani": 1.89,
            "vade_ay": 120,
            "odul_miktari_tl": None,
            "tahsis_ucreti_tl": 0,
        },
        {
            "record_id": "B",
            "banka": "B Bankası",
            "urun_adi": "Konut Finansmanı",
            "kar_payi_orani": 1.95,
            "vade_ay": 120,
            "odul_miktari_tl": None,
            "tahsis_ucreti_tl": None,
        },
        {
            "record_id": "C",
            "banka": "C Bankası",
            "urun_adi": "Konut Finansmanı",
            "kar_payi_orani": 1.87,
            "vade_ay": 96,
            "odul_miktari_tl": 5000,
            "tahsis_ucreti_tl": None,
        },
    ]

    result = compare_records(records)
    assert result["en_dusuk_kar_payi"]["banka"] == "C Bankası"
    assert result["en_uzun_vade"]["vade_ay"] == 120
    assert result["en_yuksek_odul"]["banka"] == "C Bankası"

    print("Offline testlerin tamamı başarılı.")

if __name__ == "__main__":
    main()
