import json
import pandas as pd

# JSON dosyasını oku
with open("raw/kuveytturk.json", "r", encoding="utf-8") as f:
    veriler = json.load(f)

# DataFrame'e dönüştür
df = pd.DataFrame(veriler)

# CSV olarak kaydet
df.to_csv("clean/kuveytturk.csv", index=False, encoding="utf-8-sig")

print("CSV başarıyla oluşturuldu!")
print(df.head())
