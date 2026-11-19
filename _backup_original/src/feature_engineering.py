import pandas as pd
from pathlib import Path


def create_features(df):
    # Calculate quiz accuracy
    df["quiz_accuracy"] = (
        df["correct_answers"] / df["total_questions"]
    ) * 100

    # Calculate learning engagement score
    df["engagement_score"] = (
        df["videos_watched"] * 5
        + df["lessons_completed"] * 5
        + df["login_frequency"] * 5
    )

    # Limit engagement score to a maximum of 100
    df["engagement_score"] = df["engagement_score"].clip(upper=100)

    # Calculate the learning gap score
    df["learning_gap_score"] = (
        100 - (
            0.40 * df["quiz_score"]
            + 0.25 * df["assignment_score"]
            + 0.15 * df["previous_topic_score"]
            + 0.20 * df["engagement_score"]
        )
    )

    # Ensure the score remains between 0 and 100
    df["learning_gap_score"] = df["learning_gap_score"].clip(0, 100)

    # Categorize learning gaps
    def categorize_gap(score):
        if score >= 60:
            return "High Gap"
        elif score >= 30:
            return "Medium Gap"
        else:
            return "Low Gap"

    df["gap_category"] = df["learning_gap_score"].apply(categorize_gap)

    return df


if __name__ == "__main__":
    input_file = Path("data/processed/cleaned_student_activity.csv")
    output_folder = Path("data/processed")
    output_folder.mkdir(parents=True, exist_ok=True)

    output_file = output_folder / "engineered_student_activity.csv"

    data = pd.read_csv(input_file)
    processed_data = create_features(data)
    processed_data.to_csv(output_file, index=False)

    print("Feature engineering completed successfully!")
    print("Rows:", len(processed_data))
    print("Columns:", len(processed_data.columns))
    print("Saved file:", output_file)
    print("\nSample results:")
    print(
        processed_data[
            [
                "student_id",
                "topic",
                "learning_gap_score",
                "gap_category"
            ]
        ].head()
    )