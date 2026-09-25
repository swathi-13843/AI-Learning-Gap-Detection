
import pandas as pd
import numpy as np
from pathlib import Path

# Make the generated data reproducible
np.random.seed(42)

# Create student IDs
students = [
    f"S{str(i).zfill(3)}"
    for i in range(1, 301)
]

# List of learning topics
topics = [
    "Python Basics",
    "OOP",
    "SQL",
    "SQL Joins",
    "Statistics",
    "Probability",
    "Regression",
    "Classification",
    "Decision Trees",
    "Random Forest",
    "K-Means",
    "PCA"
]

rows = []

# Generate data for every student and every topic
for student in students:
    for topic in topics:

        quiz_score = np.random.randint(30, 96)
        total_questions = 20

        correct_answers = round(
            total_questions * quiz_score / 100
        )

        quiz_attempts = np.random.randint(1, 7)
        time_spent = np.random.randint(15, 121)
        assignment_score = np.random.randint(35, 96)
        attendance = np.random.randint(60, 101)
        videos_watched = np.random.randint(0, 10)
        lessons_completed = np.random.randint(1, 11)
        login_frequency = np.random.randint(1, 8)
        days_inactive = np.random.randint(0, 15)
        previous_topic_score = np.random.randint(30, 96)

        rows.append([
            student,
            topic,
            quiz_score,
            total_questions,
            correct_answers,
            quiz_attempts,
            time_spent,
            assignment_score,
            attendance,
            videos_watched,
            lessons_completed,
            login_frequency,
            days_inactive,
            previous_topic_score
        ])

# Define the dataset columns
columns = [
    "student_id",
    "topic",
    "quiz_score",
    "total_questions",
    "correct_answers",
    "quiz_attempts",
    "time_spent_minutes",
    "assignment_score",
    "attendance",
    "videos_watched",
    "lessons_completed",
    "login_frequency",
    "days_inactive",
    "previous_topic_score"
]

# Create a DataFrame
df = pd.DataFrame(rows, columns=columns)

# Create the output folder
output_folder = Path("data/raw")
output_folder.mkdir(parents=True, exist_ok=True)

# Save the dataset
output_file = output_folder / "student_activity.csv"
df.to_csv(output_file, index=False)

# Display the result
print("Dataset created successfully!")
print("File:", output_file)
print("Rows:", len(df))
print("Columns:", len(df.columns))
print("\nFirst five rows:")
print(df.head())