import sqlite3
import pandas as pd
from pathlib import Path


# Database connection
database_file = Path("database/learning_gap.db")
connection = sqlite3.connect(database_file)


# Load processed files
summary_df = pd.read_csv(
    "data/processed/student_summary.csv"
)

gaps_df = pd.read_csv(
    "data/processed/detected_learning_gaps.csv"
)

recommendations_df = pd.read_csv(
    "data/processed/personalized_recommendations.csv"
)


# Clear old data to prevent duplicate records
connection.execute("DELETE FROM students")
connection.execute("DELETE FROM learning_gaps")
connection.execute("DELETE FROM recommendations")


# Insert student summary data
students_data = summary_df[
    [
        "student_id",
        "average_quiz_score",
        "average_assignment_score",
        "average_learning_gap",
        "average_attendance",
        "overall_risk"
    ]
]

students_data.to_sql(
    "students",
    connection,
    if_exists="append",
    index=False
)


# Insert learning-gap data
gaps_data = gaps_df[
    [
        "student_id",
        "topic",
        "learning_gap_score",
        "gap_category",
        "priority"
    ]
]

gaps_data.to_sql(
    "learning_gaps",
    connection,
    if_exists="append",
    index=False
)


# Insert recommendations
recommendations_data = recommendations_df[
    [
        "student_id",
        "topic",
        "recommendation"
    ]
]

recommendations_data.to_sql(
    "recommendations",
    connection,
    if_exists="append",
    index=False
)


connection.commit()
connection.close()


print("Data inserted into SQLite successfully!")
print("Students inserted:", len(students_data))
print("Learning-gap records inserted:", len(gaps_data))
print("Recommendations inserted:", len(recommendations_data))