import pandas as pd
from pathlib import Path


def detect_learning_gaps(df):
    # Sort records by highest learning gap
    df = df.sort_values(
        by="learning_gap_score",
        ascending=False
    )

    # Add a priority level
    def assign_priority(category):
        if category == "High Gap":
            return "High Priority"
        elif category == "Medium Gap":
            return "Medium Priority"
        else:
            return "Low Priority"

    df["priority"] = df["gap_category"].apply(assign_priority)

    return df


def create_student_summary(df):
    # Create student-level summary
    summary = df.groupby("student_id").agg(
        average_quiz_score=("quiz_score", "mean"),
        average_assignment_score=("assignment_score", "mean"),
        average_learning_gap=("learning_gap_score", "mean"),
        average_attendance=("attendance", "mean"),
        total_topics=("topic", "count"),
        high_gap_topics=(
            "gap_category",
            lambda x: (x == "High Gap").sum()
        ),
        medium_gap_topics=(
            "gap_category",
            lambda x: (x == "Medium Gap").sum()
        ),
        low_gap_topics=(
            "gap_category",
            lambda x: (x == "Low Gap").sum()
        )
    ).reset_index()

    # Categorize overall student risk
    def classify_student_risk(gap_score):
        if gap_score >= 60:
            return "High Risk"
        elif gap_score >= 30:
            return "Medium Risk"
        else:
            return "Low Risk"

    summary["overall_risk"] = summary[
        "average_learning_gap"
    ].apply(classify_student_risk)

    return summary


if __name__ == "__main__":
    input_file = Path(
        "data/processed/engineered_student_activity.csv"
    )

    output_folder = Path("data/processed")
    output_folder.mkdir(parents=True, exist_ok=True)

    gap_file = output_folder / "detected_learning_gaps.csv"
    summary_file = output_folder / "student_summary.csv"

    data = pd.read_csv(input_file)

    detected_data = detect_learning_gaps(data)
    student_summary = create_student_summary(detected_data)

    detected_data.to_csv(gap_file, index=False)
    student_summary.to_csv(summary_file, index=False)

    print("Learning gap detection completed successfully!")
    print("Total records:", len(detected_data))
    print("Total students:", len(student_summary))

    print("\nGap category distribution:")
    print(detected_data["gap_category"].value_counts())

    print("\nStudent summary sample:")
    print(student_summary.head())

    print("\nFiles saved:")
    print(gap_file)
    print(summary_file)