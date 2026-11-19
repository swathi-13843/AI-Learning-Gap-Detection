"""
Feature Engineering Module for EduGap AI.
Extracts rich behavioral, temporal, Bayesian Knowledge Tracing (BKT),
and curriculum progression features from student activity data.

Includes:
- BKT topic mastery probability & learning gain
- Student engagement score
- Recent performance trend
- Quiz improvement rate
- Topic completion rate
- Activity consistency
- Learning progress over time
- Previous topic dependency
- Hidden learning gap indicators (high overall performance but weak in specific topic)
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import numpy as np
import pandas as pd
from src.knowledge_tracing import BayesianKnowledgeTracer


def compute_student_aggregates(df):
    """
    Computes global baseline performance for each student across all topics.
    Used to compare individual topic performance against student's own norm.
    """
    agg = df.groupby("student_id").agg(
        overall_avg_quiz=("quiz_score", "mean"),
        overall_avg_assignment=("assignment_score", "mean"),
        overall_attendance=("attendance", "mean"),
        overall_login_freq=("login_frequency", "mean")
    ).reset_index()
    return agg


def engineer_learning_gap_features(df, bkt_tracer=None):
    """
    Main feature engineering pipeline.
    Combines static metrics, BKT mastery estimates, and temporal progress indicators.
    """
    df = df.copy()

    # 1. Basic Quiz Accuracy
    if "total_questions" in df.columns and "correct_answers" in df.columns:
        df["quiz_accuracy"] = (df["correct_answers"] / df["total_questions"].replace(0, 1)) * 100.0
    else:
        df["quiz_accuracy"] = df["quiz_score"]

    # 2. Student Engagement Score
    df["engagement_score"] = (
        df.get("videos_watched", 0) * 5.0
        + df.get("lessons_completed", 0) * 5.0
        + df.get("login_frequency", 0) * 5.0
    ).clip(0.0, 100.0)

    # 3. Topic Completion Rate
    df["topic_completion_rate"] = (df.get("lessons_completed", 1) / 10.0).clip(0.0, 1.0) * 100.0

    # 4. Activity Consistency
    # High attendance + low inactive days = high consistency
    df["activity_consistency"] = (
        df.get("attendance", 75.0) * 0.60
        + (1.0 - (df.get("days_inactive", 5).clip(0, 15) / 15.0)) * 40.0
    ).clip(0.0, 100.0)

    # 5. Quiz Improvement Rate
    # More attempts with higher quiz score indicates positive effort / recovery
    attempts = df.get("quiz_attempts", 1).clip(lower=1)
    df["quiz_improvement_rate"] = (df["quiz_score"] / attempts).clip(0.0, 100.0)

    # 6. Temporal sequence features (grouped by student in curriculum order)
    if "topic_order_idx" not in df.columns:
        topic_order = [
            "Python Basics", "OOP", "SQL", "SQL Joins", "Statistics", "Probability",
            "Regression", "Classification", "Decision Trees", "Random Forest", "K-Means", "PCA"
        ]
        topic_rank = {t: i for i, t in enumerate(topic_order)}
        df["topic_order_idx"] = df["topic"].map(lambda x: topic_rank.get(x, 99))

    df = df.sort_values(by=["student_id", "topic_order_idx"]).reset_index(drop=True)

    # Recent performance trend (diff between current and previous topic score)
    df["previous_topic_dependency"] = df.groupby("student_id")["quiz_score"].diff().fillna(0.0)
    df["recent_performance_trend"] = df.groupby("student_id")["quiz_score"].transform(
        lambda s: s.rolling(window=3, min_periods=1).mean()
    )
    df["learning_progress_over_time"] = df.groupby("student_id")["quiz_score"].transform(
        lambda s: s.expanding().mean()
    )

    # 7. Student-level baseline comparison & Hidden Gap Detection
    student_aggs = compute_student_aggregates(df)
    df = df.merge(student_aggs, on="student_id", how="left")

    # Differential: how much worse is student performing on THIS topic compared to their overall average?
    df["topic_gap_differential"] = df["overall_avg_quiz"] - df["quiz_score"]

    # Hidden gap flag: student has high overall performance (>= 75%) but poor topic performance (<= 50%)
    df["is_hidden_gap_candidate"] = (
        (df["overall_avg_quiz"] >= 70.0) & (df["quiz_score"] <= 55.0)
    ).astype(int)

    # 8. Bayesian Knowledge Tracing (BKT) Features
    if bkt_tracer is None:
        bkt_tracer = BayesianKnowledgeTracer()

    bkt_records = []
    for _, row in df.iterrows():
        bkt_feat = bkt_tracer.extract_features_for_student_topic(
            quiz_score=float(row["quiz_score"]),
            total_questions=int(row.get("total_questions", 20)),
            correct_answers=int(row.get("correct_answers", round(20 * row["quiz_score"] / 100.0))),
            attempts=int(row.get("quiz_attempts", 1)),
            topic=row.get("topic")
        )
        bkt_records.append(bkt_feat)

    bkt_df = pd.DataFrame(bkt_records)
    for col in bkt_df.columns:
        df[col] = bkt_df[col].values

    # 9. Learning Gap Score & Category (Ground Truth Definition)
    # Bounded between 0 and 100
    df["learning_gap_score"] = (
        100.0 - (
            0.40 * df["quiz_score"]
            + 0.25 * df["assignment_score"]
            + 0.15 * df["previous_topic_score"]
            + 0.20 * df["engagement_score"]
        )
    ).clip(0.0, 100.0)

    def categorize_gap(score):
        if score >= 60.0:
            return "High Gap"
        elif score >= 30.0:
            return "Medium Gap"
        else:
            return "Low Gap"

    df["gap_category"] = df["learning_gap_score"].apply(categorize_gap)

    return df


# Retain backward-compatible alias for existing scripts
def create_features(df):
    return engineer_learning_gap_features(df)


if __name__ == "__main__":
    from src.preprocessing import load_raw_activity_data, preprocess_activity_data

    raw = load_raw_activity_data()
    cleaned = preprocess_activity_data(raw)
    engineered = engineer_learning_gap_features(cleaned)

    out_file = Path("data/processed/engineered_student_activity.csv")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    engineered.to_csv(out_file, index=False)

    print("Feature engineering successfully completed!")
    print("Output shape:", engineered.shape)
    print("New features preview:")
    cols = [
        "student_id", "topic", "quiz_score", "bkt_mastery_prob",
        "topic_gap_differential", "is_hidden_gap_candidate", "learning_gap_score", "gap_category"
    ]
    print(engineered[cols].head(10))
