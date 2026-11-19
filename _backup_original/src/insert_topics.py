import sqlite3
from pathlib import Path


DATABASE = Path("database/learning_gap.db")


topics = [
    ("Python Basics", "Python", "Fundamentals of Python programming"),
    ("OOP", "Python", "Object-oriented programming concepts"),
    ("SQL", "Database", "SQL fundamentals and queries"),
    ("SQL Joins", "Database", "INNER JOIN, LEFT JOIN, RIGHT JOIN and related concepts"),
    ("Statistics", "Data Science", "Basic statistics concepts"),
    ("Probability", "Data Science", "Probability concepts and calculations"),
    ("Regression", "Machine Learning", "Regression algorithms and concepts"),
    ("Classification", "Machine Learning", "Classification algorithms and concepts"),
    ("Decision Trees", "Machine Learning", "Decision tree concepts"),
    ("Random Forest", "Machine Learning", "Random forest concepts"),
    ("K-Means", "Machine Learning", "K-Means clustering"),
    ("PCA", "Data Science", "Principal Component Analysis")
]


connection = sqlite3.connect(DATABASE)

cursor = connection.cursor()


for topic_name, subject, description in topics:

    cursor.execute(
        """
        INSERT OR IGNORE INTO topics
        (topic_name, subject, description)

        VALUES (?, ?, ?)
        """,
        (topic_name, subject, description)
    )


connection.commit()


print("\nTopics inserted successfully!\n")


rows = cursor.execute(
    """
    SELECT id, topic_name, subject
    FROM topics
    ORDER BY id
    """
).fetchall()


for row in rows:

    print(
        f"{row[0]}. {row[1]} - {row[2]}"
    )


connection.close()