from nlp.normalizer import (
    normalize_percentage,
    normalize_percentage_range,
    normalize_amount_tl,
    normalize_term_months,
    normalize_term_range,
    normalize_fee,
    normalize_extraction,
)

def test_percentage():
    assert normalize_percentage("%2,05") == 2.05
    assert normalize_percentage("% 2.05") == 2.05
    assert normalize_percentage("2.05 %") == 2.05

def test_amount():
    assert normalize_amount_tl("500 TL") == 500.0
    assert normalize_amount_tl("500₺") == 500.0
    assert normalize_amount_tl("1.500.000 TL") == 1500000.0

def test_term():
    assert normalize_term_months("120 aya kadar") == 120
    assert normalize_term_months("10 yıl") == 120


def test_term_range_mixed_units():
    assert normalize_term_range("1 - 36 Ay") == (1, 36)
    assert normalize_term_range("120 aya kadar") == (120, 120)
    assert normalize_term_range("1 - 10 yıl") == (12, 120)
    # karışık birim: her sayı kendi birimiyle
    assert normalize_term_range("6 ay - 2 yıl") == (6, 24)


def test_percentage_range():
    assert normalize_percentage_range("%3.79 - %4.19") == (3.79, 4.19)
    assert normalize_percentage_range("%2,99") == (2.99, 2.99)


def test_fee_percent_vs_tl():
    assert normalize_fee("%0,5") == (None, 0.5)
    assert normalize_fee("575 TL") == (575.0, None)


def test_normalize_extraction_runs():
    """A1/A2 regresyonu: fonksiyon UnboundLocalError vermeden çalışmalı."""
    out = normalize_extraction(
        {
            "kar_payi_orani_raw": "%2,99 - %3,49",
            "vade_raw": "1 - 36 Ay",
            "finansman_tutari_raw": "50.000 TL - 250.000 TL",
            "tahsis_ucreti_raw": "%0,5",
            "finansman_orani_raw": "%80'e kadar",
        }
    )
    assert out["kar_payi_orani_min"] == 2.99
    assert out["kar_payi_orani_max"] == 3.49
    assert out["vade_max_ay"] == 36
    assert out["finansman_tutari_max"] == 250000.0
    assert out["tahsis_ucreti_orani"] == 0.5
    assert out["finansman_orani"] == 80.0
