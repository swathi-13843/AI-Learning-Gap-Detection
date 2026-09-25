import sqlite3
from pathlib import Path


DATABASE = Path("database/learning_gap.db")


connection = sqlite3.connect(DATABASE)

cursor = connection.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS users (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT NOT NULL UNIQUE,

    email TEXT NOT NULL UNIQUE,

    password TEXT NOT NULL,

    role TEXT NOT NULL DEFAULT 'student',

    student_id TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)
""")


connection.commit()

print("Users table created successfully.")


connection.close()