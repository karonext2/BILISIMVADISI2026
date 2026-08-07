from bank_scraper import BankScraper

# Linkleri oku
with open("raw/kuveytturk_links.txt", "r", encoding="utf-8") as f:
    linkler = [satir.strip() for satir in f if satir.strip()]

print(f"{len(linkler)} link bulundu.")

# Scraper oluştur
scraper = BankScraper("Kuveyt Türk")

# Verileri çek
scraper.scrape(linkler)

# JSON olarak kaydet
scraper.json_kaydet("raw/kuveytturk_v2.json")
