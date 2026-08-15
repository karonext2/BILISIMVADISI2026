from pathlib import Path
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    accuracy_score,
    confusion_matrix,
    f1_score,
)

from preprocess import preprocess_text

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "final_dataset.csv"
MODEL_PATH = ROOT / "models" / "campaign_classifier.joblib"

df = pd.read_csv(DATA_PATH)
df = df.dropna(subset=["metin", "kategori"]).copy()

df["metin"] = df["metin"].astype(str).apply(preprocess_text)
df["kategori"] = df["kategori"].astype(str)

print("Toplam örnek:", len(df))
print("\nSınıf dağılımı:")
print(df["kategori"].value_counts())

X_train, X_test, y_train, y_test = train_test_split(
    df["metin"],
    df["kategori"],
    test_size=0.20,
    random_state=42,
    stratify=df["kategori"],
)

pipeline = Pipeline([
    (
        "tfidf",
        TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95,
            sublinear_tf=True,
        ),
    ),
    (
        "classifier",
        LogisticRegression(
            max_iter=3000,
            class_weight="balanced",
            random_state=42,
        ),
    ),
])

pipeline.fit(X_train, y_train)
pred = pipeline.predict(X_test)

print("\n=== TEST SONUÇLARI ===")
print("Accuracy:", round(accuracy_score(y_test, pred), 4))
print("Macro F1:", round(f1_score(y_test, pred, average="macro"), 4))
print("\nClassification Report:")
print(classification_report(y_test, pred, digits=4, zero_division=0))
print("Confusion Matrix:")
print(confusion_matrix(y_test, pred))

# En küçük sınıfta en az 5 örnek olduğu için 5-fold uygulanabilir.
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(
    pipeline,
    df["metin"],
    df["kategori"],
    cv=cv,
    scoring="f1_macro",
)

print("\n5-Fold Macro F1:", round(cv_scores.mean(), 4))
print("Fold skorları:", [round(x, 4) for x in cv_scores])

# Nihai modeli tüm veriyle yeniden eğit ve kaydet
pipeline.fit(df["metin"], df["kategori"])

MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(pipeline, MODEL_PATH)

print(f"\nYeni model kaydedildi: {MODEL_PATH}")
print("Sınıflar:", list(pipeline.classes_))