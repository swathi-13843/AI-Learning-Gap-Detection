"""
Database enhancement migration script for EduGap AI.
Adds tables and schemas for:
- youtube_resources: Curated and Admin-managed YouTube learning links per topic/subject
- student_guidance: Direct guidance, improvement goals, and revision topics set by Admin
- assessments: Proctored & standard tests/quizzes created by Admin
- assessment_questions: Objective (MCQ, True/False, Multi-select) & Subjective questions
- assessment_attempts: Student attempts, timer, autosave, submission status, score
- assessment_answers: Individual question responses and subjective scores/evaluations
- proctoring_logs: Real-time proctoring security events (tab switches, webcam/face alerts, fullscreen changes)
"""
import sqlite3
from pathlib import Path

DB_PATH = Path("database/learning_gap.db")

def run_migration():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. YouTube Learning Resources Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS youtube_resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        youtube_url TEXT NOT NULL,
        video_id TEXT,
        subject TEXT NOT NULL,
        topic TEXT NOT NULL,
        description TEXT,
        difficulty_level TEXT DEFAULT 'Intermediate',
        learning_objective TEXT,
        thumbnail_url TEXT,
        assigned_to_student_id TEXT,
        created_by_admin TEXT DEFAULT 'Admin',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Student Guidance & Study Improvement Plans
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_guidance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        admin_id INTEGER,
        admin_name TEXT DEFAULT 'Academic Administrator',
        guidance_text TEXT NOT NULL,
        improvement_goals TEXT,
        recommended_topics TEXT,
        practice_assignments TEXT,
        status TEXT DEFAULT 'Active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(student_id)
    );
    """)

    # 3. Enhanced Assessments Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assessments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        subject TEXT NOT NULL,
        topic TEXT NOT NULL,
        duration_minutes INTEGER DEFAULT 30,
        passing_marks REAL DEFAULT 50.0,
        total_marks REAL DEFAULT 100.0,
        negative_marking REAL DEFAULT 0.0,
        attempt_limit INTEGER DEFAULT 1,
        shuffle_questions INTEGER DEFAULT 1,
        shuffle_options INTEGER DEFAULT 1,
        is_proctored INTEGER DEFAULT 1,
        proctoring_strictness TEXT DEFAULT 'Standard',
        assigned_to_student_id TEXT,
        due_date TIMESTAMP,
        is_published INTEGER DEFAULT 1,
        results_published INTEGER DEFAULT 1,
        created_by TEXT DEFAULT 'Admin',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 4. Assessment Questions Table (Objective & Subjective)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assessment_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        assessment_id INTEGER NOT NULL,
        question_text TEXT NOT NULL,
        question_type TEXT DEFAULT 'mcq', -- 'mcq', 'true_false', 'multiple_select', 'subjective'
        option_a TEXT,
        option_b TEXT,
        option_c TEXT,
        option_d TEXT,
        correct_answer TEXT, -- e.g. 'A', 'True', 'A,C', or rubric keywords for subjective
        marks REAL DEFAULT 5.0,
        explanation TEXT,
        FOREIGN KEY (assessment_id) REFERENCES assessments(id) ON DELETE CASCADE
    );
    """)

    # 5. Assessment Attempts Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assessment_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        assessment_id INTEGER NOT NULL,
        student_id TEXT NOT NULL,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        submitted_at TIMESTAMP,
        time_taken_seconds INTEGER DEFAULT 0,
        score REAL DEFAULT 0.0,
        max_score REAL DEFAULT 100.0,
        percentage REAL DEFAULT 0.0,
        passed INTEGER DEFAULT 0,
        status TEXT DEFAULT 'in_progress', -- 'in_progress', 'submitted', 'evaluated'
        proctoring_flag_count INTEGER DEFAULT 0,
        review_status TEXT DEFAULT 'normal', -- 'normal', 'flagged', 'under_review', 'reviewed'
        review_notes TEXT,
        evaluated_by TEXT,
        evaluated_at TIMESTAMP,
        FOREIGN KEY (assessment_id) REFERENCES assessments(id) ON DELETE CASCADE,
        FOREIGN KEY (student_id) REFERENCES students(student_id)
    );
    """)

    # 6. Assessment Submitted Answers
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assessment_answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attempt_id INTEGER NOT NULL,
        question_id INTEGER NOT NULL,
        student_id TEXT NOT NULL,
        student_answer TEXT,
        is_correct INTEGER DEFAULT 0,
        awarded_marks REAL DEFAULT 0.0,
        max_marks REAL DEFAULT 5.0,
        feedback TEXT,
        last_saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (attempt_id) REFERENCES assessment_attempts(id) ON DELETE CASCADE,
        FOREIGN KEY (question_id) REFERENCES assessment_questions(id) ON DELETE CASCADE
    );
    """)

    # 7. Proctoring Security Events Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS proctoring_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attempt_id INTEGER NOT NULL,
        student_id TEXT NOT NULL,
        assessment_id INTEGER NOT NULL,
        event_type TEXT NOT NULL, -- 'tab_switch', 'window_blur', 'face_missing', 'multiple_faces', 'fullscreen_exit', 'copy_paste'
        severity TEXT DEFAULT 'warning', -- 'info', 'warning', 'critical'
        details TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (attempt_id) REFERENCES assessment_attempts(id) ON DELETE CASCADE
    );
    """)

    # Ensure mentor role accounts are mapped cleanly or upgraded
    cursor.execute("UPDATE users SET role = 'admin' WHERE role = 'mentor';")

    conn.commit()
    conn.close()
    print("Database schema migration completed successfully!")

if __name__ == "__main__":
    run_migration()
