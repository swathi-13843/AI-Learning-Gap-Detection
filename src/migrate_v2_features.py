"""
Database migration script for EduGap AI v2 Platform Upgrade.
Safely creates new tables and adds columns without breaking existing data:
- student_theory_progress
- student_video_progress
- academic_marks
- theory_materials
- student_learning_paths
- student_interventions_tracking
"""

import sqlite3
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "database" / "learning_gap.db"


def run_migration():
    print(f"Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Update students table columns safely
    cursor.execute("PRAGMA table_info(students)")
    existing_cols = [r[1] for r in cursor.fetchall()]

    if "completed_assessments_count" not in existing_cols:
        cursor.execute("ALTER TABLE students ADD COLUMN completed_assessments_count INTEGER DEFAULT 0")
        print("Added column completed_assessments_count to students")

    if "risk_confidence" not in existing_cols:
        cursor.execute("ALTER TABLE students ADD COLUMN risk_confidence REAL DEFAULT 0.0")
        print("Added column risk_confidence to students")

    if "current_semester" not in existing_cols:
        cursor.execute("ALTER TABLE students ADD COLUMN current_semester INTEGER DEFAULT 6")
        print("Added column current_semester to students")

    # 2. Theory Materials Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS theory_materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            unit TEXT NOT NULL,
            topic_name TEXT NOT NULL UNIQUE,
            definition TEXT NOT NULL,
            detailed_explanation TEXT NOT NULL,
            important_points TEXT NOT NULL,
            advantages TEXT NOT NULL,
            disadvantages TEXT NOT NULL,
            real_world_examples TEXT NOT NULL,
            applications TEXT NOT NULL,
            short_questions TEXT NOT NULL,
            long_questions TEXT NOT NULL,
            formulas TEXT NOT NULL,
            key_takeaways TEXT NOT NULL,
            diagram_svg TEXT,
            diagram_title TEXT,
            diagram_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("Verified theory_materials table")

    # 3. Student Theory Progress Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_theory_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            topic_name TEXT NOT NULL,
            status TEXT DEFAULT 'Not Started',
            notes TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, topic_name)
        )
    """)
    print("Verified student_theory_progress table")

    # 4. Student Video Progress Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_video_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            video_id INTEGER NOT NULL,
            is_completed INTEGER DEFAULT 0,
            watched_seconds INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, video_id)
        )
    """)
    print("Verified student_video_progress table")

    # 5. Academic Performance Marks Table (Mid-1, Mid-2, Semester Marks)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS academic_marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            semester INTEGER NOT NULL,
            academic_year TEXT NOT NULL,
            subject_name TEXT NOT NULL,
            mid1_marks REAL DEFAULT 0.0,
            mid1_max REAL DEFAULT 30.0,
            mid2_marks REAL DEFAULT 0.0,
            mid2_max REAL DEFAULT 30.0,
            assignment_marks REAL DEFAULT 0.0,
            assignment_max REAL DEFAULT 10.0,
            internal_marks REAL DEFAULT 0.0,
            internal_max REAL DEFAULT 40.0,
            semester_marks REAL DEFAULT 0.0,
            semester_max REAL DEFAULT 60.0,
            total_marks REAL DEFAULT 0.0,
            total_max REAL DEFAULT 100.0,
            status TEXT DEFAULT 'pending_review',
            verified_by TEXT,
            remarks TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("Verified academic_marks table")

    # 6. Student Personalized Adaptive Learning Paths Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_learning_paths (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            topic_name TEXT NOT NULL,
            current_step INTEGER DEFAULT 1,
            total_steps INTEGER DEFAULT 6,
            steps_json TEXT NOT NULL,
            status TEXT DEFAULT 'In Progress',
            initial_mastery REAL DEFAULT 0.0,
            reassessed_mastery REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, topic_name)
        )
    """)
    print("Verified student_learning_paths table")

    # 7. Student Intervention and Recovery Tracking Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_interventions_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            topic_name TEXT NOT NULL,
            initial_mastery REAL NOT NULL,
            recommendations_json TEXT NOT NULL,
            completion_status TEXT DEFAULT 'In Progress',
            reassessment_score REAL,
            updated_mastery REAL,
            improvement_delta REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("Verified student_interventions_tracking table")

    # 8. Add Diagnostic Assessment if not existing
    cursor.execute("SELECT id FROM assessments WHERE title LIKE '%Diagnostic%'")
    diag = cursor.fetchone()
    if not diag:
        cursor.execute("""
            INSERT INTO assessments (title, subject, topic, description, duration_minutes, total_marks, passing_marks, is_proctored, is_published)
            VALUES (
                'Initial Diagnostic Assessment - Academic Readiness Evaluation',
                'Computer Science & Engineering',
                'Comprehensive Baseline',
                'Mandatory entry evaluation for newly registered students to establish baseline knowledge mastery, learning gap indicators, and calibrated academic risk status.',
                25, 50, 20, 0, 1
            )
        """)
        diag_id = cursor.lastrowid
        print(f"Created Initial Diagnostic Assessment with ID {diag_id}")

        # Insert representative diagnostic questions
        diag_questions = [
            ("What is the time complexity of searching in an unsorted array of size N?", "mcq", '["O(1)", "O(log N)", "O(N)", "O(N^2)"]', "O(N)", 5, "An unsorted array requires scanning elements sequentially from start to end in the worst case."),
            ("In Python, which built-in data type is immutable?", "mcq", '["List", "Dictionary", "Set", "Tuple"]', "Tuple", 5, "Tuples cannot be modified after instantiation, guaranteeing immutability."),
            ("Which SQL clause is used to filter groups created by the GROUP BY statement?", "mcq", '["WHERE", "HAVING", "ORDER BY", "FILTER"]', "HAVING", 5, "WHERE filters individual rows prior to grouping, whereas HAVING filters aggregated groups."),
            ("In relational databases, what does an INNER JOIN return?", "mcq", '["All rows from left table", "All rows from both tables", "Only matching rows from both tables", "Non-matching rows"]', "Only matching rows from both tables", 5, "INNER JOIN evaluates predicate equality and yields records matching in both tables."),
            ("True or False: In supervised learning, the training dataset contains both feature inputs and target output labels.", "true_false", '["True", "False"]', "True", 5, "Supervised algorithms require labeled pairs (X, y) to learn predictive mappings."),
            ("Which evaluation metric is preferred when evaluating classifiers on severely imbalanced datasets?", "mcq", '["Raw Accuracy", "Precision-Recall AUC / F1-Score", "Mean Squared Error", "R-Squared"]', "Precision-Recall AUC / F1-Score", 5, "Accuracy can be deceptively high when predicting the majority class; F1 and PR-AUC assess minority class detection."),
            ("What is the primary role of the Update Gate in a Gated Recurrent Unit (GRU)?", "mcq", '["Determines how much past hidden state to forget", "Decides how much prior memory to carry forward versus candidate update", "Normalizes gradient variance across time", "Resets weights to zero"]', "Decides how much prior memory to carry forward versus candidate update", 5, "The GRU update gate balances historical context h_{t-1} against candidate state."),
            ("In K-Means clustering, what does the algorithm optimize to determine cluster centers?", "mcq", '["Within-Cluster Sum of Squares (Inertia)", "Maximum Margin Hyperplane", "Cross-Entropy Loss", "Information Gain"]', "Within-Cluster Sum of Squares (Inertia)", 5, "K-Means minimizes within-cluster variance by iteratively updating centroids to cluster member means."),
            ("Explain the fundamental difference between overfitting and underfitting in machine learning models.", "subjective", '[]', "Overfitting occurs when a model learns noise and specifics of training data leading to high variance and poor generalization; underfitting occurs when a model lacks capacity leading to high bias and poor training performance.", 5, "Overfitting = High variance / low bias; Underfitting = High bias / low variance."),
            ("In database transactions, explain the ACID properties and why each property is essential for data integrity.", "subjective", '[]', "Atomicity (all or nothing), Consistency (preserves database constraints), Isolation (concurrent transactions do not interfere), Durability (committed changes persist across failures).", 5, "ACID properties guarantee transactional reliability in relational database engines.")
        ]
        for q_text, q_type, q_opts, q_ans, q_marks, q_exp in diag_questions:
            cursor.execute("""
                INSERT INTO assessment_questions (assessment_id, question_text, question_type, options, correct_answer, marks, explanation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (diag_id, q_text, q_type, q_opts, q_ans, q_marks, q_exp))
        print("Added diagnostic questions to assessment")

    # 9. Update students who have 0 completed attempts to have 'Assessment Pending'
    cursor.execute("""
        SELECT s.student_id,
            (SELECT COUNT(*) FROM assessment_attempts aa WHERE aa.student_id = s.student_id AND (aa.status = 'evaluated' OR aa.score IS NOT NULL)) as eval_attempts,
            (SELECT COUNT(*) FROM quiz_attempts qa WHERE qa.student_id = s.student_id) as q_attempts
        FROM students s
    """)
    student_records = cursor.fetchall()
    for sid, eval_cnt, q_cnt in student_records:
        total_eval = (eval_cnt or 0) + (q_cnt or 0)
        cursor.execute("UPDATE students SET completed_assessments_count = ? WHERE student_id = ?", (total_eval, sid))
        if total_eval == 0:
            cursor.execute("""
                UPDATE students
                SET overall_risk = 'Assessment Pending',
                    risk_confidence = 0.0,
                    average_quiz_score = 0.0,
                    average_assignment_score = 0.0,
                    average_learning_gap = 0.0
                WHERE student_id = ?
            """, (sid,))
            print(f"Set student {sid} to Assessment Pending (0 completed assessments)")
        elif total_eval == 1:
            cursor.execute("""
                UPDATE students
                SET overall_risk = 'Insufficient Data',
                    risk_confidence = 35.0
                WHERE student_id = ? AND overall_risk = 'Medium Risk'
            """, (sid,))
            print(f"Set student {sid} to Insufficient Data (1 completed assessment)")

    conn.commit()
    conn.close()
    print("Database migration completed successfully!")


if __name__ == "__main__":
    run_migration()
