import re

def preprocess_text(text: str) -> str:
    """
    Basit Türkçe metin ön işleme.
    TF-IDF için agresif stemming/lemmatization yapmıyoruz.
    """
    text = str(text).lower()
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"\S+@\S+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text