import sqlite3
from pathlib import Path


# Create the database folder
database_folder = Path("database")
database_folder.mkdir(parents=True, exist_ok=True)

database_file = database_folder / "learning_gap.db"


# Connect to SQLite database
connection = sqlite3.connect(database_file)
cursor = connection.cursor()


# Create students table
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    student_id TEXT PRIMARY KEY,
    average_quiz_score REAL,
    average_assignment_score REAL,
    average_learning_gap REAL,
    average_attendance REAL,
    overall_risk TEXT
)
""")


# Create learning gaps table
cursor.execute("""
CREATE TABLE IF NOT EXISTS learning_gaps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    topic TEXT,
    learning_gap_score REAL,
    gap_category TEXT,
    priority TEXT
)
""")


# Create recommendations table
cursor.execute("""
CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    topic TEXT,
    recommendation TEXT
)
""")


# Create interventions table
cursor.execute("""
CREATE TABLE IF NOT EXISTS interventions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    intervention_type TEXT,
    description TEXT,
    status TEXT DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")


connection.commit()
connection.close()

print("Database created successfully!")
print("Database location:", database_file)