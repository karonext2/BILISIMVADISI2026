"""Extractor — LLM çağırmadan yapılabilen kontroller (A1/A2 regresyonu)."""

import pytest

from nlp.extractor import _build_user_prompt, _system_prompt, extract_financial_info


def test_bos_metin_valueerror():
    with pytest.raises(ValueError):
        extract_financial_info("")
    with pytest.raises(ValueError):
        extract_financial_info("   ")


def test_prompt_kurulur_ve_degiskenler_enjekte_edilir():
    p = _build_user_prompt("Konut finansmanı %2,99", banka="Kuveyt Türk", baslik="Konut Finansmanı")
    assert "{{METIN}}" not in p and "{{BANKA}}" not in p and "{{BASLIK}}" not in p
    assert "Kuveyt Türk" in p and "Konut Finansmanı" in p and "%2,99" in p


def test_sistem_prompt_yuklenir():
    s = _system_prompt()
    assert "kâr payı" in s.lower()
    assert len(s) > 500
