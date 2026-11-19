"""
Data Preprocessing Module for EduGap AI.
Handles loading, validation, deduplication, chronological sorting,
and missing value imputation for student activity datasets.
"""

from pathlib import Path
import numpy as np
import pandas as pd


def load_raw_activity_data(filepath=None):
    if filepath is None:
        filepath = Path("data/raw/student_activity.csv")
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Raw data file not found at {filepath}")
    return pd.read_csv(filepath)


def preprocess_activity_data(df, output_path=None):
    """
    Cleans raw student activity data:
    1. Deduplicates
    2. Enforces curriculum topic order
    3. Handles missing values with robust median imputation
    4. Validates boundary ranges
    """
    df_clean = df.copy()
    df_clean = df_clean.drop_duplicates()

    # Enforce standard curriculum topic ordering
    topic_order = [
        "Python Basics", "OOP", "SQL", "SQL Joins", "Statistics", "Probability",
        "Regression", "Classification", "Decision Trees", "Random Forest", "K-Means", "PCA"
    ]
    topic_rank = {t: i for i, t in enumerate(topic_order)}
    df_clean["topic_order_idx"] = df_clean["topic"].map(lambda x: topic_rank.get(x, 99))
    df_clean = df_clean.sort_values(by=["student_id", "topic_order_idx"]).reset_index(drop=True)

    # Impute missing values
    num_cols = df_clean.select_dtypes(include=[np.number]).columns
    for c in num_cols:
        if df_clean[c].isnull().any():
            median_val = df_clean[c].median()
            df_clean[c] = df_clean[c].fillna(median_val)

    # Bounded value clipping to valid domain ranges
    if "quiz_score" in df_clean.columns:
        df_clean["quiz_score"] = df_clean["quiz_score"].clip(0.0, 100.0)
    if "assignment_score" in df_clean.columns:
        df_clean["assignment_score"] = df_clean["assignment_score"].clip(0.0, 100.0)
    if "attendance" in df_clean.columns:
        df_clean["attendance"] = df_clean["attendance"].clip(0.0, 100.0)
    if "days_inactive" in df_clean.columns:
        df_clean["days_inactive"] = df_clean["days_inactive"].clip(0, 30)

    if output_path is not None:
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        df_clean.to_csv(out_file, index=False)

    return df_clean


if __name__ == "__main__":
    raw_df = load_raw_activity_data()
    cleaned = preprocess_activity_data(raw_df, "data/processed/cleaned_student_activity.csv")
    print(f"Data preprocessing complete. Cleaned shape: {cleaned.shape}")
