import pandas as pd
from pathlib import Path


def generate_recommendation(row):
    recommendations = []

    # Recommendation based on quiz score
    if row["quiz_score"] < 50:
        recommendations.append(
            f"Revise the fundamentals of {row['topic']}."
        )
        recommendations.append(
            "Complete beginner-level practice questions."
        )

    elif row["quiz_score"] < 70:
        recommendations.append(
            f"Practice more exercises related to {row['topic']}."
        )

    else:
        recommendations.append(
            f"Try advanced exercises in {row['topic']}."
        )

    # Recommendation based on assignment score
    if row["assignment_score"] < 50:
        recommendations.append(
            "Review assignment mistakes and resubmit the assignment."
        )

    # Recommendation based on inactivity
    if row["days_inactive"] >= 7:
        recommendations.append(
            "Follow a daily learning schedule to improve consistency."
        )

    # Recommendation based on engagement
    if row["engagement_score"] < 40:
        recommendations.append(
            "Watch more learning videos and complete pending lessons."
        )

    # Recommendation based on learning gap
    if row["learning_gap_score"] >= 60:
        recommendations.append(
            "Schedule a mentor or instructor support session."
        )

    return " ".join(recommendations)


if __name__ == "__main__":
    input_file = Path(
        "data/processed/detected_learning_gaps.csv"
    )

    output_folder = Path("data/processed")
    output_folder.mkdir(parents=True, exist_ok=True)

    output_file = output_folder / "personalized_recommendations.csv"

    df = pd.read_csv(input_file)

    # Generate recommendations for each student-topic record
    df["recommendation"] = df.apply(
        generate_recommendation,
        axis=1
    )

    df.to_csv(output_file, index=False)

    print("Personalized recommendations generated successfully!")
    print("Total recommendations:", len(df))
    print("Saved file:", output_file)

    print("\nSample recommendations:")
    print(
        df[
            [
                "student_id",
                "topic",
                "gap_category",
                "recommendation"
            ]
        ].head(10).to_string(index=False)
    )