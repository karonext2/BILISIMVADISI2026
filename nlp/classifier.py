from __future__ import annotations

from nlp.extractor import extract_financial_info

def classify_campaign(
    text: str,
    banka: str | None = None,
    baslik: str | None = None,
) -> str:
    """
    Ayrı bir LLM çağrısı yapmaz.
    MVP'de extractor aynı çağrıda kampanya türünü de üretir.
    """
    result = extract_financial_info(text=text, banka=banka, baslik=baslik)
    return result["kampanya_turu"]
