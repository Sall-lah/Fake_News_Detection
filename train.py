from __future__ import annotations

from pathlib import Path

import pandas as pd

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


if __name__ == "__main__":
    df = load_and_prepare_data()
