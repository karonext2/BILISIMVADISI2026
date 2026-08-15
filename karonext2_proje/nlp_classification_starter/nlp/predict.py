from pathlib import Path
import joblib

from preprocess import preprocess_text

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "campaign_classifier.joblib"

model = joblib.load(MODEL_PATH)

def predict_category(text: str):
    clean = preprocess_text(text)

    label = model.predict([clean])[0]
    probabilities = model.predict_proba([clean])[0]
    classes = model.classes_

    scores = sorted(
        zip(classes, probabilities),
        key=lambda x: x[1],
        reverse=True
    )

    return {
        "kategori": label,
        "guven": float(scores[0][1]),
        "tum_skorlar": [
            {"kategori": cls, "skor": float(score)}
            for cls, score in scores
        ]
    }

if __name__ == "__main__":
    text = input("Kampanya metni: ")
    result = predict_category(text)

    print("\nTahmin:", result["kategori"])
    print("Güven:", f'%{result["guven"] * 100:.2f}')
    print("\nTüm skorlar:")
    for item in result["tum_skorlar"]:
        print(f'- {item["kategori"]}: %{item["skor"] * 100:.2f}')