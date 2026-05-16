from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.pipeline import Pipeline

from preprocess import clean_text


def load_and_prepare_data() -> pd.DataFrame:
    """Load Fake.csv and True.csv, combine with labels, and apply preprocessing."""
    root = Path(__file__).parent

    # Load datasets
    fake_df = pd.read_csv(root / "dataset" / "Fake.csv")
    true_df = pd.read_csv(root / "dataset" / "True.csv")

    # Add labels: 0 for fake, 1 for true
    fake_df["label"] = 0
    true_df["label"] = 1

    # Combine datasets
    df = pd.concat([fake_df, true_df], ignore_index=True)

    # Feature engineering: combine title + text into single string column
    df["string"] = df["title"].fillna("") + " " + df["text"].fillna("")

    # Drop original columns — keep only string and label
    df = df.drop(columns=["title", "text", "subject", "date"])

    # Apply preprocessing using the shared clean_text function
    df["string"] = df["string"].apply(lambda s: clean_text(None, s))

    # Filter empty/NA rows
    na_count = df["string"].isna().sum()
    df = df.dropna()

    empty_count = (df["string"] == "").sum()
    df = df[df["string"] != ""]

    filtered_count = int(na_count) + int(empty_count)
    if filtered_count > 0:
        print(f"Filtered {filtered_count} rows (NA: {na_count}, empty: {empty_count})")

    # Print dataset summary
    print(f"Total rows after cleaning: {len(df)}")
    print(f"Class distribution:")
    print(df["label"].value_counts().to_string())

    return df


def train() -> Path:
    """Run full training pipeline and return the path to the saved model.pkl."""
    df = load_and_prepare_data()

    # Train/test split (80/20 stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        df["string"], df["label"], test_size=0.2, stratify=df["label"], random_state=42
    )

    # Build sklearn Pipeline with TF-IDF + LightGBM
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=10000, ngram_range=(1, 2), min_df=2, max_df=0.95)),
        ("classifier", LGBMClassifier(random_state=42, verbose=-1)),
    ])

    # Parameter distributions for RandomizedSearchCV
    param_distributions = {
        "tfidf__max_features": [20000, 40000],
        "tfidf__ngram_range": [(1, 1)],
        "tfidf__min_df": [1],
        "classifier__n_estimators": [200, 300],
        "classifier__learning_rate": [0.1],
        "classifier__num_leaves": [15],
        "classifier__max_depth": [-1],
    }

    # Run RandomizedSearchCV
    search = RandomizedSearchCV(
        pipeline,
        param_distributions,
        n_iter=5,
        cv=2,
        scoring="accuracy",
        random_state=42,
        n_jobs=1,  # LightGBM multiprocessing crashes on Windows
        verbose=1,
    )
    search.fit(X_train, y_train)

    # Get best model and evaluate
    best_model = search.best_estimator_
    y_pred = best_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    # Print training metrics
    print(f"\n{'=' * 50}")
    print(f"Training Complete")
    print(f"{'=' * 50}")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Fake", "True"]))
    print(f"Best Hyperparameters:")
    for param, value in search.best_params_.items():
        print(f"  {param}: {value}")

    # Save model
    model_path = Path(__file__).parent / "model.pkl"
    joblib.dump(best_model, model_path)
    print(f"\nModel saved to {model_path}")

    # Verify saved model works
    loaded = joblib.load(model_path)
    test_prediction = loaded.predict([X_test.iloc[0]])
    print(f"Verification prediction: {test_prediction[0]} (expected: {y_test.iloc[0]})")
    assert test_prediction[0] == y_test.iloc[0], "Verification failed!"
    print("Model verification passed")

    return model_path


if __name__ == "__main__":
    model_path = train()
    print(f"Training complete. Model saved to {model_path}")
