from chatbot import guardrails


def test_faiz_kar_payina_cevrilir():
    assert "kâr payı" in guardrails.terminoloji_duzelt("Bu üründe faiz oranı yüksek.")
    # 'faizsiz' bozulmamalı
    assert "faizsiz" in guardrails.terminoloji_duzelt("faizsiz finansman")


def test_teknik_terim_temizlenir():
    metin = "Vektör araması ve embedding ile bulundu."
    assert guardrails.teknik_terim_var_mi(metin)
    temiz = guardrails.teknik_terimleri_temizle(metin)
    assert not guardrails.teknik_terim_var_mi(temiz)


def test_dogrulanmamis_sayi_yakalanir():
    baglam = "Kuveyt Türk konut finansmanı %2,99 aylık, 120 ay vade."
    yanit_iyi = "Kâr payı %2,99 ve vade 120 ay."
    yanit_kotu = "Kâr payı %1,50 ve vade 84 ay."
    assert guardrails.dogrulanmamis_sayilar(yanit_iyi, baglam) == []
    bulunan = guardrails.dogrulanmamis_sayilar(yanit_kotu, baglam)
    assert any("1,50" in b or "%1" in b for b in bulunan)


def test_uygula_uyari_ekler():
    y, uyari = guardrails.uygula(
        "Faiz oranı %9,99 civarındadır.",
        baglam="Kâr payı %2,99 aylık.",
    )
    assert "kâr payı" in y.lower()
    assert uyari and "doğrulanamadı" in uyari
