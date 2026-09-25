import sqlite3
from pathlib import Path


# ============================================================
# DATABASE PATH
# ============================================================

DATABASE = Path("database/learning_gap.db")


# ============================================================
# CONNECT TO DATABASE
# ============================================================

connection = sqlite3.connect(DATABASE)

cursor = connection.cursor()


# ============================================================
# TOPICS
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS topics (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    topic_name TEXT NOT NULL UNIQUE,

    subject TEXT,

    description TEXT

)
""")


# ============================================================
# STUDENT TOPICS
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS student_topics (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    student_id TEXT NOT NULL,

    topic_id INTEGER NOT NULL,

    score REAL DEFAULT 0,

    learning_gap_score REAL DEFAULT 0,

    gap_category TEXT,

    priority TEXT,

    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (topic_id)
        REFERENCES topics(id)

)
""")


# ============================================================
# QUIZZES
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS quizzes (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    topic_id INTEGER NOT NULL,

    title TEXT NOT NULL,

    description TEXT,

    total_questions INTEGER DEFAULT 0,

    duration INTEGER DEFAULT 30,

    due_date TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (topic_id)
        REFERENCES topics(id)

)
""")


# ============================================================
# QUESTIONS
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS questions (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    quiz_id INTEGER NOT NULL,

    question TEXT NOT NULL,

    option_a TEXT NOT NULL,

    option_b TEXT NOT NULL,

    option_c TEXT NOT NULL,

    option_d TEXT NOT NULL,

    correct_answer TEXT NOT NULL,

    FOREIGN KEY (quiz_id)
        REFERENCES quizzes(id)

)
""")


# ============================================================
# QUIZ ATTEMPTS
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS quiz_attempts (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    student_id TEXT NOT NULL,

    quiz_id INTEGER NOT NULL,

    score REAL DEFAULT 0,

    percentage REAL DEFAULT 0,

    time_taken INTEGER DEFAULT 0,

    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (quiz_id)
        REFERENCES quizzes(id)

)
""")


# ============================================================
# QUIZ ANSWERS
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS quiz_answers (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    attempt_id INTEGER NOT NULL,

    question_id INTEGER NOT NULL,

    selected_answer TEXT,

    is_correct INTEGER DEFAULT 0,

    FOREIGN KEY (attempt_id)
        REFERENCES quiz_attempts(id),

    FOREIGN KEY (question_id)
        REFERENCES questions(id)

)
""")


# ============================================================
# ASSIGNMENTS
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS assignments (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    topic_id INTEGER NOT NULL,

    title TEXT NOT NULL,

    description TEXT,

    due_date TEXT,

    max_score REAL DEFAULT 100,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (topic_id)
        REFERENCES topics(id)

)
""")


# ============================================================
# SUBMISSIONS
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS submissions (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    assignment_id INTEGER NOT NULL,

    student_id TEXT NOT NULL,

    score REAL,

    status TEXT DEFAULT 'Pending',

    feedback TEXT,

    submitted_at TIMESTAMP,

    FOREIGN KEY (assignment_id)
        REFERENCES assignments(id)

)
""")


# ============================================================
# ACTIVITY LOGS
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS activity_logs (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    student_id TEXT NOT NULL,

    topic_id INTEGER,

    activity_type TEXT NOT NULL,

    duration INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (topic_id)
        REFERENCES topics(id)

)
""")


# ============================================================
# REMINDERS
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS reminders (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    student_id TEXT NOT NULL,

    title TEXT NOT NULL,

    description TEXT,

    due_date TEXT,

    status TEXT DEFAULT 'Pending',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)
""")


# ============================================================
# NOTIFICATIONS
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS notifications (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    student_id TEXT NOT NULL,

    message TEXT NOT NULL,

    notification_type TEXT DEFAULT 'General',

    is_read INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)
""")


# ============================================================
# ACHIEVEMENTS
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS achievements (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    student_id TEXT NOT NULL,

    achievement TEXT NOT NULL,

    description TEXT,

    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)
""")


# ============================================================
# SAVE CHANGES
# ============================================================

connection.commit()


# ============================================================
# DISPLAY TABLES
# ============================================================

tables = cursor.execute("""
SELECT name
FROM sqlite_master
WHERE type = 'table'
ORDER BY name
""").fetchall()


print("\nDatabase upgrade completed successfully!\n")

print("Current database tables:")

for table in tables:
    print(" -", table[0])


# ============================================================
# CLOSE DATABASE
# ============================================================

connection.close()