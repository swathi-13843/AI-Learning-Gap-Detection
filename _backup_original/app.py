import os
import sqlite3
from functools import wraps
from pathlib import Path

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash

# AI Intelligence Service
from src.ai_engine import (
    predict_student_risk,
    get_student_cluster_persona,
    generate_topic_recommendation
)
from src.curriculum_data import CURRICULUM_ROADMAP

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "edugap-production-secret-token-key-2026")

DATABASE = Path("database/learning_gap.db")

# ============================================================
# DATABASE CONNECTION
# ============================================================
def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection

# ============================================================
# LOGIN REQUIRED DECORATOR
# ============================================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please authenticate to access the academic platform.", "info")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# ============================================================
# HOME / DASHBOARD
# ============================================================
@app.route("/")
@login_required
def dashboard():
    connection = get_db_connection()

    if session.get("role") == "student":
        student_id = session.get("student_id") or "S001"
        student = connection.execute(
            "SELECT * FROM students WHERE student_id = ?",
            (student_id,)
        ).fetchone()

        # Fetch student personalized guidance from Admin
        student_guidance_list = connection.execute("""
            SELECT * FROM student_guidance
            WHERE student_id = ?
            ORDER BY id DESC LIMIT 5
        """, (student_id,)).fetchall()

        # Fetch weak topics from learning_gaps and student answers
        weak_topics = connection.execute("""
            SELECT topic FROM learning_gaps
            WHERE student_id = ? AND learning_gap_score >= 30.0
            ORDER BY learning_gap_score DESC
        """, (student_id,)).fetchall()
        weak_topic_names = [w["topic"] for w in weak_topics]

        # Fetch recommended YouTube videos matching weak topics or assigned specifically
        if weak_topic_names:
            placeholders = ",".join("?" for _ in weak_topic_names)
            recommended_videos = connection.execute(f"""
                SELECT * FROM youtube_resources
                WHERE topic IN ({placeholders}) OR assigned_to_student_id = ?
                ORDER BY id DESC LIMIT 6
            """, (*weak_topic_names, student_id)).fetchall()
        else:
            recommended_videos = connection.execute("""
                SELECT * FROM youtube_resources
                ORDER BY id DESC LIMIT 6
            """).fetchall()

        connection.close()

        if student is None:
            return render_template(
                "dashboard.html",
                total_students=0,
                high_risk=0,
                medium_risk=0,
                low_risk=0,
                students=[],
                current_student=None,
                student_guidance_list=[],
                recommended_videos=[]
            )

        return render_template(
            "dashboard.html",
            total_students=1,
            high_risk=1 if student["overall_risk"] == "High Risk" else 0,
            medium_risk=1 if student["overall_risk"] == "Medium Risk" else 0,
            low_risk=1 if student["overall_risk"] == "Low Risk" else 0,
            students=[student],
            current_student=student,
            student_guidance_list=student_guidance_list,
            recommended_videos=recommended_videos
        )

    # ADMIN / ACADEMIC MONITOR CONSOLE
    total_students = connection.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    high_risk = connection.execute("SELECT COUNT(*) FROM students WHERE overall_risk = 'High Risk'").fetchone()[0]
    medium_risk = connection.execute("SELECT COUNT(*) FROM students WHERE overall_risk = 'Medium Risk'").fetchone()[0]
    low_risk = connection.execute("SELECT COUNT(*) FROM students WHERE overall_risk = 'Low Risk'").fetchone()[0]

    # Real database statistics for Admin Overview
    active_assessments = connection.execute("SELECT COUNT(*) FROM assessments WHERE is_published = 1").fetchone()[0]
    total_quizzes = connection.execute("SELECT COUNT(*) FROM quizzes").fetchone()[0]
    flagged_proctoring_count = connection.execute("SELECT COUNT(*) FROM assessment_attempts WHERE proctoring_flag_count > 0").fetchone()[0]
    pending_evaluations = connection.execute("SELECT COUNT(*) FROM assessment_attempts WHERE status = 'submitted'").fetchone()[0]
    total_yt_resources = connection.execute("SELECT COUNT(*) FROM youtube_resources").fetchone()[0]
    avg_gap_row = connection.execute("SELECT AVG(average_learning_gap) FROM students").fetchone()
    cohort_avg_gap = round(avg_gap_row[0], 1) if avg_gap_row and avg_gap_row[0] is not None else 35.0

    students = connection.execute("""
        SELECT *
        FROM students
        ORDER BY average_learning_gap DESC
        LIMIT 50
    """).fetchall()

    connection.close()

    return render_template(
        "dashboard.html",
        total_students=total_students,
        cohort_avg_gap=cohort_avg_gap,
        total_quizzes=total_quizzes,
        high_risk=high_risk,
        medium_risk=medium_risk,
        low_risk=low_risk,
        active_assessments=active_assessments,
        flagged_proctoring_count=flagged_proctoring_count,
        pending_evaluations=pending_evaluations,
        total_yt_resources=total_yt_resources,
        students=students,
        current_student=None
    )

# ============================================================
# AUTHENTICATION: LOGIN & REGISTER & LOGOUT
# ============================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        connection = get_db_connection()
        user = connection.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?",
            (username, username)
        ).fetchone()
        connection.close()

        if user and check_password_hash(user["password"], password):
            # Enforce strictly two roles: admin and student
            role = "admin" if user["role"] in ["admin", "mentor"] else "student"
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = role
            session["student_id"] = user["student_id"]

            flash(f"Welcome back, {user['username'].title()}.", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid credentials supplied. Please check and retry.", "error")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        student_id = request.form.get("student_id", "").strip().upper()

        if not username or not email or not password or not student_id:
            flash("All registration fields are required.", "error")
            return redirect(url_for("register"))

        connection = get_db_connection()
        existing_student = connection.execute(
            "SELECT * FROM students WHERE student_id = ?",
            (student_id,)
        ).fetchone()

        if existing_student is None:
            # Create student placeholder
            connection.execute("""
                INSERT INTO students (student_id, name, email, average_quiz_score, average_assignment_score, average_learning_gap, average_attendance, overall_risk)
                VALUES (?, ?, ?, 50.0, 50.0, 50.0, 75.0, 'Medium Risk')
            """, (student_id, username.title(), email))

        existing_user = connection.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?",
            (username, email)
        ).fetchone()

        if existing_user:
            connection.close()
            flash("Username or email already registered in system.", "error")
            return redirect(url_for("register"))

        password_hash = generate_password_hash(password)
        connection.execute("""
            INSERT INTO users (username, email, password, role, student_id)
            VALUES (?, ?, ?, 'student', ?)
        """, (username, email, password_hash, student_id))

        connection.commit()
        connection.close()

        flash("Account provisioned successfully. Please sign in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("login"))

# ============================================================
# PROFILE & TOPIC LOGGING
# ============================================================
@app.route("/profile")
@login_required
def profile():
    student_id = session.get("student_id")
    # If admin or user without student_id clicks My Profile, view primary student S001
    if not student_id:
        student_id = "S001"

    connection = get_db_connection()

    student = connection.execute(
        "SELECT * FROM students WHERE student_id = ?",
        (student_id,)
    ).fetchone()

    # If student does not exist in DB yet, create a default record
    if student is None:
        default_name = session.get("username", "Student").title()
        connection.execute("""
            INSERT INTO students (student_id, name, email, average_quiz_score, average_assignment_score, average_learning_gap, average_attendance, overall_risk)
            VALUES (?, ?, ?, 50.0, 50.0, 50.0, 80.0, 'Low Risk')
        """, (student_id, default_name, f"{session.get('username','student')}@edulearn.ai"))
        connection.commit()
        student = connection.execute(
            "SELECT * FROM students WHERE student_id = ?",
            (student_id,)
        ).fetchone()

    topics = connection.execute(
        "SELECT * FROM topics ORDER BY id"
    ).fetchall()

    performance_data = connection.execute("""
        SELECT
            st.id,
            st.student_id,
            st.topic_id,
            st.score,
            st.learning_gap_score,
            st.gap_category,
            st.priority,
            st.last_updated,
            t.topic_name,
            t.subject
        FROM student_topics st
        JOIN topics t ON st.topic_id = t.id
        WHERE st.student_id = ?
        ORDER BY st.learning_gap_score DESC
    """, (student_id,)).fetchall()

    connection.close()

    # Determine persona from student metrics safely
    features = {
        "quiz_score": student["average_quiz_score"] if student and "average_quiz_score" in student.keys() else 50,
        "assignment_score": student["average_assignment_score"] if student and "average_assignment_score" in student.keys() else 50,
        "attendance": student["average_attendance"] if student and "average_attendance" in student.keys() else 75,
        "videos_watched": 4,
        "lessons_completed": 5,
        "login_frequency": 3,
        "days_inactive": 5,
        "engagement_score": 50
    }
    persona = get_student_cluster_persona(features)

    return render_template(
        "profile.html",
        student=student,
        topics=topics,
        performance_data=performance_data,
        persona=persona
    )

@app.route("/update-performance", methods=["POST"])
@login_required
def update_performance():
    if session.get("role") != "student":
        return redirect(url_for("dashboard"))

    student_id = session.get("student_id")
    topic_id = request.form.get("topic_id")
    score_raw = request.form.get("score", 0)

    try:
        score = float(score_raw)
    except ValueError:
        flash("Invalid score provided.", "error")
        return redirect(url_for("profile"))

    if score < 0 or score > 100:
        flash("Score must be between 0 and 100.", "error")
        return redirect(url_for("profile"))

    connection = get_db_connection()
    topic = connection.execute("SELECT * FROM topics WHERE id = ?", (topic_id,)).fetchone()
    if not topic:
        connection.close()
        flash("Invalid topic selected.", "error")
        return redirect(url_for("profile"))

    # Recalculate learning gap
    learning_gap_score = round(100.0 - score, 2)
    if learning_gap_score >= 60:
        gap_category = "High Gap"
        priority = "High Priority"
    elif learning_gap_score >= 30:
        gap_category = "Medium Gap"
        priority = "Medium Priority"
    else:
        gap_category = "Low Gap"
        priority = "Low Priority"

    existing = connection.execute(
        "SELECT id FROM student_topics WHERE student_id = ? AND topic_id = ?",
        (student_id, topic_id)
    ).fetchone()

    if existing:
        connection.execute("""
            UPDATE student_topics
            SET score = ?, learning_gap_score = ?, gap_category = ?, priority = ?, last_updated = CURRENT_TIMESTAMP
            WHERE student_id = ? AND topic_id = ?
        """, (score, learning_gap_score, gap_category, priority, student_id, topic_id))
    else:
        connection.execute("""
            INSERT INTO student_topics (student_id, topic_id, score, learning_gap_score, gap_category, priority)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (student_id, topic_id, score, learning_gap_score, gap_category, priority))

    # Recalculate student averages
    aggregates = connection.execute("""
        SELECT AVG(score) as avg_score, AVG(learning_gap_score) as avg_gap
        FROM student_topics
        WHERE student_id = ?
    """, (student_id,)).fetchone()

    new_avg_score = aggregates["avg_score"] or score
    new_avg_gap = aggregates["avg_gap"] or learning_gap_score
    overall_risk = "High Risk" if new_avg_gap >= 60 else ("Medium Risk" if new_avg_gap >= 30 else "Low Risk")

    connection.execute("""
        UPDATE students
        SET average_quiz_score = ?, average_learning_gap = ?, overall_risk = ?
        WHERE student_id = ?
    """, (round(new_avg_score, 2), round(new_avg_gap, 2), overall_risk, student_id))

    connection.commit()
    connection.close()

    flash(f"Assessment score for {topic['topic_name']} recorded. Gap recalculated to {learning_gap_score}%.", "success")
    return redirect(url_for("profile"))

# ============================================================
# STUDENT DETAILS DRILLDOWN
# ============================================================
@app.route("/student/<student_id>")
@login_required
def student_details(student_id):
    # Enforce access authorization: Students can only view their own profile
    if session.get("role") == "student" and session.get("student_id") != student_id:
        flash("Unauthorized access. You may only view your personal academic record.", "error")
        return redirect(url_for("dashboard"))

    connection = get_db_connection()

    student = connection.execute(
        "SELECT * FROM students WHERE student_id = ?",
        (student_id,)
    ).fetchone()

    gaps = connection.execute("""
        SELECT * FROM learning_gaps
        WHERE student_id = ?
        ORDER BY learning_gap_score DESC
    """, (student_id,)).fetchall()

    recommendations = connection.execute("""
        SELECT * FROM recommendations
        WHERE student_id = ?
    """, (student_id,)).fetchall()

    # Guidance history published by Admin
    guidance_history = connection.execute("""
        SELECT * FROM student_guidance
        WHERE student_id = ?
        ORDER BY id DESC
    """, (student_id,)).fetchall()

    # Test and examination history
    assessment_history = connection.execute("""
        SELECT att.*, a.title as assessment_title, a.passing_marks
        FROM assessment_attempts att
        JOIN assessments a ON a.id = att.assessment_id
        WHERE att.student_id = ?
        ORDER BY att.id DESC
    """, (student_id,)).fetchall()

    # YouTube resources recommended for this student
    weak_topic_names = [g["topic"] for g in gaps if g["learning_gap_score"] >= 30.0]
    if weak_topic_names:
        placeholders = ",".join("?" for _ in weak_topic_names)
        recommended_videos = connection.execute(f"""
            SELECT * FROM youtube_resources
            WHERE topic IN ({placeholders}) OR assigned_to_student_id = ?
            ORDER BY id DESC LIMIT 6
        """, (*weak_topic_names, student_id)).fetchall()
    else:
        recommended_videos = connection.execute("""
            SELECT * FROM youtube_resources
            WHERE assigned_to_student_id = ? OR assigned_to_student_id IS NULL OR assigned_to_student_id = ''
            ORDER BY id DESC LIMIT 6
        """, (student_id,)).fetchall()

    connection.close()

    return render_template(
        "student.html",
        student=student,
        gaps=gaps,
        recommendations=recommendations,
        guidance_history=guidance_history,
        assessment_history=assessment_history,
        recommended_videos=recommended_videos
    )

# ============================================================
# ADAPTIVE QUIZZES
# ============================================================
@app.route("/quizzes")
@login_required
def quizzes_page():
    if session.get("role") == "admin":
        flash("Adaptive Quizzes are designed for student conceptual mastery evaluation. For administrator tests, use Assessments & Tests.", "info")
        return redirect(url_for("assessments_page"))

    connection = get_db_connection()
    quizzes = connection.execute("""
        SELECT q.*, t.topic_name, t.subject
        FROM quizzes q
        JOIN topics t ON q.topic_id = t.id
        ORDER BY q.id
    """).fetchall()

    student_id = session.get("student_id") or "S001"
    attempts = connection.execute("""
        SELECT quiz_id, score, percentage, MAX(attempted_at) as last_attempt
        FROM quiz_attempts
        WHERE student_id = ?
        GROUP BY quiz_id
    """, (student_id,)).fetchall()

    attempt_map = {att["quiz_id"]: att for att in attempts}
    connection.close()
    return render_template("quizzes.html", quizzes=quizzes, attempt_map=attempt_map)

@app.route("/quiz/<int:quiz_id>", methods=["GET", "POST"])
@login_required
def quiz_detail(quiz_id):
    if session.get("role") == "admin":
        flash("Adaptive Quizzes are reserved for student evaluation.", "info")
        return redirect(url_for("assessments_page"))

    connection = get_db_connection()
    quiz = connection.execute("""
        SELECT q.*, t.topic_name, t.subject
        FROM quizzes q
        JOIN topics t ON q.topic_id = t.id
        WHERE q.id = ?
    """, (quiz_id,)).fetchone()

    if not quiz:
        connection.close()
        flash("Quiz not found.", "error")
        return redirect(url_for("quizzes_page"))

    questions = connection.execute("""
        SELECT * FROM questions WHERE quiz_id = ? ORDER BY id
    """, (quiz_id,)).fetchall()

    if request.method == "POST":
        student_id = session.get("student_id") or "S001"
        total = len(questions)
        correct = 0

        for q in questions:
            user_ans = request.form.get(f"question_{q['id']}")
            if user_ans == q["correct_answer"]:
                correct += 1

        percentage = round((correct / total) * 100, 2) if total > 0 else 0
        gap_score = round(100.0 - percentage, 2)
        gap_category = "High Gap" if gap_score >= 60 else ("Medium Gap" if gap_score >= 30 else "Low Gap")
        priority = "High Priority" if gap_score >= 60 else ("Medium Priority" if gap_score >= 30 else "Low Priority")

        # Save quiz attempt
        connection.execute("""
            INSERT INTO quiz_attempts (student_id, quiz_id, score, percentage, time_taken)
            VALUES (?, ?, ?, ?, ?)
        """, (student_id, quiz_id, correct, percentage, 10))

        # Update student_topics
        existing = connection.execute("""
            SELECT id FROM student_topics WHERE student_id = ? AND topic_id = ?
        """, (student_id, quiz["topic_id"])).fetchone()

        if existing:
            connection.execute("""
                UPDATE student_topics
                SET score = ?, learning_gap_score = ?, gap_category = ?, priority = ?, last_updated = CURRENT_TIMESTAMP
                WHERE student_id = ? AND topic_id = ?
            """, (percentage, gap_score, gap_category, priority, student_id, quiz["topic_id"]))
        else:
            connection.execute("""
                INSERT INTO student_topics (student_id, topic_id, score, learning_gap_score, gap_category, priority)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (student_id, quiz["topic_id"], percentage, gap_score, gap_category, priority))

        # Recalculate student averages
        aggregates = connection.execute("""
            SELECT AVG(score) as avg_score, AVG(learning_gap_score) as avg_gap
            FROM student_topics WHERE student_id = ?
        """, (student_id,)).fetchone()

        if aggregates and aggregates["avg_score"] is not None:
            new_quiz_avg = round(aggregates["avg_score"], 2)
            new_gap_avg = round(aggregates["avg_gap"], 2)
            overall_risk = "High Risk" if new_gap_avg >= 60 else ("Medium Risk" if new_gap_avg >= 30 else "Low Risk")
            connection.execute("""
                UPDATE students
                SET average_quiz_score = ?, average_learning_gap = ?, overall_risk = ?
                WHERE student_id = ?
            """, (new_quiz_avg, new_gap_avg, overall_risk, student_id))

        connection.commit()
        connection.close()

        flash(f"Assessment completed. Score: {correct}/{total} ({percentage}%). Updated Gap: {gap_score}%.", "success")
        return redirect(url_for("profile") if session.get("role") == "student" else url_for("quizzes_page"))

    connection.close()
    return render_template("quiz_detail.html", quiz=quiz, questions=questions)

# ============================================================
# ASSIGNMENTS & PROJECT EVALUATION
# ============================================================
@app.route("/assignments")
@login_required
def assignments_page():
    connection = get_db_connection()
    role = session.get("role")
    
    assignments = connection.execute("""
        SELECT a.*, t.topic_name, t.subject
        FROM assignments a
        JOIN topics t ON a.topic_id = t.id
        ORDER BY a.id
    """).fetchall()

    if role == "admin":
        # Admin view: Fetch all student submissions with student name, project details, and grading status
        submissions = connection.execute("""
            SELECT s.*, a.title as assignment_title, a.max_score, st.name as student_name, st.department
            FROM submissions s
            JOIN assignments a ON s.assignment_id = a.id
            LEFT JOIN students st ON s.student_id = st.student_id
            ORDER BY s.id DESC
        """).fetchall()
        connection.close()
        return render_template("assignments.html", assignments=assignments, submissions=submissions, is_admin=True)
    else:
        # Student view: Fetch submissions made by current student
        student_id = session.get("student_id") or "S001"
        submissions = connection.execute("""
            SELECT * FROM submissions WHERE student_id = ?
        """, (student_id,)).fetchall()
        submission_map = {sub["assignment_id"]: sub for sub in submissions}
        connection.close()
        return render_template("assignments.html", assignments=assignments, submission_map=submission_map, is_admin=False)

@app.route("/assignment/submit/<int:assignment_id>", methods=["POST"])
@login_required
def submit_assignment(assignment_id):
    if session.get("role") == "admin":
        flash("Administrators do not submit assignments. Use the Evaluation console to review and score student deliverables.", "info")
        return redirect(url_for("assignments_page"))

    student_id = session.get("student_id") or "S001"
    github_repo = request.form.get("github_repo", "").strip()
    comments = request.form.get("comments", "").strip()
    
    file_name = None
    if "submission_file" in request.files:
        uploaded_file = request.files["submission_file"]
        if uploaded_file and uploaded_file.filename:
            file_name = uploaded_file.filename

    connection = get_db_connection()
    assignment = connection.execute(
        "SELECT * FROM assignments WHERE id = ?",
        (assignment_id,)
    ).fetchone()

    if not assignment:
        connection.close()
        flash("Assignment not found.", "error")
        return redirect(url_for("assignments_page"))

    # Initial submission status is 'Submitted' with 0.0 awarded until Admin grades it
    initial_score = 0.0
    connection.execute("""
        INSERT INTO submissions (assignment_id, student_id, score, status, feedback, file_name, github_repo, comments)
        VALUES (?, ?, ?, 'Pending Evaluation', 'Submission uploaded successfully. Awaiting administrator evaluation and score.', ?, ?, ?)
    """, (assignment_id, student_id, initial_score, file_name, github_repo, comments))

    connection.commit()
    connection.close()

    flash(f"Deliverable for '{assignment['title']}' submitted successfully! Awaiting administrator evaluation.", "success")
    return redirect(url_for("assignments_page"))

@app.route("/admin/grade-submission/<int:submission_id>", methods=["POST"])
@login_required
def admin_grade_submission(submission_id):
    if session.get("role") != "admin":
        flash("Access restricted to Academic Administrators.", "error")
        return redirect(url_for("dashboard"))

    marks_str = request.form.get("score", "").strip()
    feedback = request.form.get("feedback", "").strip() or "Evaluation completed by academic administrator."

    try:
        score = float(marks_str)
    except ValueError:
        flash("Invalid numerical score entered.", "error")
        return redirect(url_for("assignments_page"))

    connection = get_db_connection()
    submission = connection.execute("""
        SELECT s.*, a.max_score FROM submissions s
        JOIN assignments a ON s.assignment_id = a.id
        WHERE s.id = ?
    """, (submission_id,)).fetchone()

    if not submission:
        connection.close()
        flash("Submission record not found.", "error")
        return redirect(url_for("assignments_page"))

    max_sc = float(submission["max_score"])
    if score < 0 or score > max_sc:
        connection.close()
        flash(f"Score must be between 0 and {max_sc}.", "error")
        return redirect(url_for("assignments_page"))

    connection.execute("""
        UPDATE submissions
        SET score = ?, status = 'Graded', feedback = ?
        WHERE id = ?
    """, (score, feedback, submission_id))

    # Recalculate student average_assignment_score
    student_id = submission["student_id"]
    sub_avg = connection.execute("""
        SELECT AVG(score) as avg_sc FROM submissions WHERE student_id = ? AND status = 'Graded'
    """, (student_id,)).fetchone()

    if sub_avg and sub_avg["avg_sc"] is not None:
        connection.execute("""
            UPDATE students SET average_assignment_score = ? WHERE student_id = ?
        """, (round(sub_avg["avg_sc"], 2), student_id))

    connection.commit()
    connection.close()

    flash(f"Graded submission #{submission_id} for student {student_id}: awarded {score}/{max_sc} marks.", "success")
    return redirect(url_for("assignments_page"))

# ============================================================
# TOPICS / KNOWLEDGE MAP DIRECTORY
# ============================================================
@app.route("/topics")
@login_required
def topics_page():
    connection = get_db_connection()
    all_topics = connection.execute("SELECT * FROM topics ORDER BY id").fetchall()

    student_id = session.get("student_id")
    if not student_id and session.get("role") != "admin":
        student_id = "S001"

    # Default metrics
    covered_count = 0
    total_count = len(all_topics)
    strong_topics = []
    weak_topics = []
    topics_with_status = []

    role = session.get("role")
    student_languages = []

    if role == "admin":
        # Admin view: purely managing curriculum topics
        for t in all_topics:
            topics_with_status.append({
                "id": t["id"],
                "topic_name": t["topic_name"],
                "subject": t["subject"],
                "description": t["description"],
                "is_covered": True,
                "score": 100.0,
                "gap": 0.0,
                "status_tier": "strong",
                "gap_category": "Curriculum Standard",
                "priority": "Active"
            })
        covered_count = total_count
        remaining_count = 0
        strong_topics = []
        weak_topics = []
    else:
        # Student view: fetch student-specific learning gaps and student languages
        student_id = session.get("student_id") or "S001"
        student_lang_rows = connection.execute("""
            SELECT * FROM student_languages WHERE student_id = ? ORDER BY id DESC
        """, (student_id,)).fetchall()
        student_languages = [dict(lr) for lr in student_lang_rows]

        # Fetch student_topics records
        st_rows = connection.execute("""
            SELECT st.*, t.topic_name, t.subject, t.description
            FROM student_topics st
            JOIN topics t ON st.topic_id = t.id
            WHERE st.student_id = ?
        """, (student_id,)).fetchall()

        st_map = {row["topic_id"]: row for row in st_rows}

        if not st_map:
            gaps_rows = connection.execute("""
                SELECT lg.*, t.id as t_id, t.subject, t.description
                FROM learning_gaps lg
                JOIN topics t ON lg.topic = t.topic_name
                WHERE lg.student_id = ?
            """, (student_id,)).fetchall()
            st_map = {}
            for gr in gaps_rows:
                sc = round(max(0.0, 100.0 - gr["learning_gap_score"]), 1)
                st_map[gr["t_id"]] = {
                    "topic_id": gr["t_id"],
                    "score": sc,
                    "learning_gap_score": gr["learning_gap_score"],
                    "gap_category": gr["gap_category"],
                    "priority": gr["priority"],
                    "topic_name": gr["topic"],
                    "subject": gr["subject"],
                    "description": gr["description"]
                }

        for t in all_topics:
            tid = t["id"]
            if tid in st_map:
                item = st_map[tid]
                score = round(float(item["score"]), 1)
                gap = round(float(item["learning_gap_score"]), 1)
                covered = True if score > 0 else False
                if covered:
                    covered_count += 1
                
                if score >= 70 or gap < 30:
                    status_tier = "strong"
                    strong_topics.append(t["topic_name"])
                elif gap >= 45 or score < 55:
                    status_tier = "weak"
                    weak_topics.append(t["topic_name"])
                else:
                    status_tier = "moderate"

                topics_with_status.append({
                    "id": t["id"],
                    "topic_name": t["topic_name"],
                    "subject": t["subject"],
                    "description": t["description"],
                    "is_covered": covered,
                    "score": score,
                    "gap": gap,
                    "status_tier": status_tier,
                    "gap_category": item["gap_category"] if "gap_category" in item else ("High" if gap >= 60 else "Moderate"),
                    "priority": item["priority"] if "priority" in item else "Normal"
                })
            else:
                topics_with_status.append({
                    "id": t["id"],
                    "topic_name": t["topic_name"],
                    "subject": t["subject"],
                    "description": t["description"],
                    "is_covered": False,
                    "score": 0.0,
                    "gap": 100.0,
                    "status_tier": "uncovered",
                    "gap_category": "Pending",
                    "priority": "Unassessed"
                })

        remaining_count = max(0, total_count - covered_count)

    connection.close()

    return render_template(
        "topics.html",
        topics=topics_with_status,
        total_count=total_count,
        covered_count=covered_count,
        remaining_count=remaining_count,
        strong_topics=strong_topics,
        weak_topics=weak_topics,
        student_languages=student_languages,
        curriculum_roadmap=CURRICULUM_ROADMAP,
        is_admin=(role == "admin")
    )

@app.route("/admin/topics/add", methods=["POST"])
@login_required
def admin_add_topic():
    if session.get("role") != "admin":
        flash("Access restricted to Academic Administrators.", "error")
        return redirect(url_for("topics_page"))

    topic_name = request.form.get("topic_name", "").strip()
    subject = request.form.get("subject", "").strip() or "Computer Science"
    description = request.form.get("description", "").strip() or f"Curriculum module covering {topic_name}."

    if not topic_name:
        flash("Topic name is required.", "error")
        return redirect(url_for("topics_page"))

    connection = get_db_connection()
    existing = connection.execute("SELECT id FROM topics WHERE topic_name = ?", (topic_name,)).fetchone()
    if existing:
        connection.close()
        flash(f"Topic '{topic_name}' already exists in syllabus.", "error")
        return redirect(url_for("topics_page"))

    connection.execute("""
        INSERT INTO topics (topic_name, subject, description)
        VALUES (?, ?, ?)
    """, (topic_name, subject, description))
    connection.commit()
    connection.close()

    flash(f"New curriculum topic '{topic_name}' added to knowledge map.", "success")
    return redirect(url_for("topics_page"))

@app.route("/admin/topics/delete/<int:topic_id>", methods=["POST"])
@login_required
def admin_delete_topic(topic_id):
    if session.get("role") != "admin":
        flash("Access restricted to Academic Administrators.", "error")
        return redirect(url_for("topics_page"))

    connection = get_db_connection()
    topic = connection.execute("SELECT * FROM topics WHERE id = ?", (topic_id,)).fetchone()
    if not topic:
        connection.close()
        flash("Topic not found.", "error")
        return redirect(url_for("topics_page"))

    connection.execute("DELETE FROM topics WHERE id = ?", (topic_id,))
    connection.commit()
    connection.close()

    flash(f"Topic '{topic['topic_name']}' removed from knowledge map.", "success")
    return redirect(url_for("topics_page"))

@app.route("/student/languages/add", methods=["POST"])
@login_required
def student_add_language():
    student_id = session.get("student_id") or "S001"
    language_name = request.form.get("language_name", "").strip()
    proficiency_level = request.form.get("proficiency_level", "Intermediate").strip()

    if not language_name:
        flash("Language name cannot be blank.", "error")
        return redirect(url_for("topics_page"))

    connection = get_db_connection()
    connection.execute("""
        CREATE TABLE IF NOT EXISTS student_languages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            language_name TEXT NOT NULL,
            proficiency_level TEXT DEFAULT 'Intermediate',
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, language_name)
        )
    """)

    try:
        connection.execute("""
            INSERT INTO student_languages (student_id, language_name, proficiency_level)
            VALUES (?, ?, ?)
        """, (student_id, language_name, proficiency_level))
        connection.commit()
        flash(f"Programming language '{language_name}' added to your portfolio.", "success")
    except sqlite3.IntegrityError:
        flash(f"Language '{language_name}' is already in your skills profile.", "info")
    finally:
        connection.close()

    return redirect(url_for("topics_page"))

@app.route("/student/languages/delete/<int:lang_id>", methods=["POST"])
@login_required
def student_delete_language(lang_id):
    student_id = session.get("student_id") or "S001"
    connection = get_db_connection()
    connection.execute("""
        DELETE FROM student_languages WHERE id = ? AND student_id = ?
    """, (lang_id, student_id))
    connection.commit()
    connection.close()

    flash("Programming language removed from your portfolio.", "info")
    return redirect(url_for("topics_page"))

@app.route("/api/curriculum-roadmap/<path:topic_name>")
@login_required
def api_curriculum_roadmap(topic_name):
    # Lookup in roadmap dictionary with fuzzy fallback
    if topic_name in CURRICULUM_ROADMAP:
        return jsonify(CURRICULUM_ROADMAP[topic_name])
    for key, data in CURRICULUM_ROADMAP.items():
        if key.lower() in topic_name.lower() or topic_name.lower() in key.lower():
            return jsonify(data)
    # Default fallback
    return jsonify({
        "title": topic_name,
        "description": "Curriculum specifications and modular learning objectives.",
        "levels": {
            "Beginner": ["Core terminology & definitions", "Foundational principles", "Basic syntax & mechanics"],
            "Intermediate": ["Algorithmic workflows", "Data structures & manipulation", "Error handling & validation"],
            "Advanced": ["Architecture & optimization", "Edge cases & performance tuning"],
            "Practical": ["Applied case study implementation", "Real-world dataset project"]
        }
    })

# ============================================================
# AI RISK CENTER & ANALYTICS
# ============================================================
@app.route("/analytics")
@login_required
def analytics_page():
    connection = get_db_connection()
    student_id = session.get("student_id")
    role = session.get("role")
    
    # Risk history fetch
    if role == "student" and student_id:
        history_records = connection.execute("""
            SELECT rh.*, s.name as student_name
            FROM risk_history rh
            LEFT JOIN students s ON rh.student_id = s.student_id
            WHERE rh.student_id = ?
            ORDER BY rh.recorded_at DESC
            LIMIT 20
        """, (student_id,)).fetchall()
    else:
        history_records = connection.execute("""
            SELECT rh.*, s.name as student_name
            FROM risk_history rh
            LEFT JOIN students s ON rh.student_id = s.student_id
            ORDER BY rh.recorded_at DESC
            LIMIT 30
        """).fetchall()

    # Pre-fetch students list for what-if selector or testing
    all_students = connection.execute("SELECT student_id, name, overall_risk, average_learning_gap, average_quiz_score, average_assignment_score, average_attendance FROM students ORDER BY student_id ASC LIMIT 50").fetchall()
    
    connection.close()
    return render_template(
        "analytics.html",
        history_records=history_records,
        students=all_students
    )

@app.route("/api/predict-risk", methods=["POST"])
@login_required
def api_predict_risk():
    data = request.get_json() or {}
    prediction_result = predict_student_risk(data)
    return jsonify(prediction_result)

@app.route("/api/record-simulation", methods=["POST"])
@login_required
def api_record_simulation():
    data = request.get_json() or {}
    student_id = data.get("student_id") or session.get("student_id") or "S001"
    risk_level = data.get("prediction", "Medium Risk")
    confidence = float(data.get("confidence", 70.0))
    quiz = float(data.get("quiz_score", 50.0))
    assignment = float(data.get("assignment_score", 50.0))
    attendance = float(data.get("attendance", 75.0))
    days_inactive = int(data.get("days_inactive", 5))
    engagement = float(data.get("engagement_score", 50.0))
    top_driver = data.get("top_driver", "Interactive What-If Simulation")

    connection = get_db_connection()
    connection.execute("""
        INSERT INTO risk_history (student_id, risk_level, confidence, quiz_score, assignment_score, attendance, days_inactive, engagement_score, top_driver)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (student_id, risk_level, confidence, quiz, assignment, attendance, days_inactive, engagement, top_driver))
    connection.commit()
    connection.close()

    return jsonify({"status": "success", "message": "Simulation snapshot recorded in risk audit trail."})

# ============================================================
# INTERVENTIONS & MENTORSHIP
# ============================================================
@app.route("/interventions")
@login_required
def interventions_page():
    connection = get_db_connection()
    role = session.get("role")
    student_id = session.get("student_id")
    mentor_id = session.get("mentor_id")
    mentor_name = session.get("mentor_name")

    # Fetch all interventions with student and mentor information
    query = """
        SELECT i.*, s.name as student_name, s.overall_risk, s.average_learning_gap, s.average_quiz_score, s.average_attendance,
               m.title as mentor_title, m.specialty as mentor_specialty, m.email as mentor_email
        FROM interventions i
        LEFT JOIN students s ON i.student_id = s.student_id
        LEFT JOIN mentors m ON (i.mentor_id = m.id OR i.mentor_name = m.name)
    """
    params = []
    if role == "student" and student_id:
        query += " WHERE i.student_id = ?"
        params.append(student_id)
    elif role == "mentor":
        # Filter strictly for the logged-in mentor
        query += " WHERE (i.mentor_id = ? OR i.mentor_name = ? OR m.user_id = ?)"
        params.extend([mentor_id or 0, mentor_name or '', session.get('user_id') or 0])

    interventions = connection.execute(query + " ORDER BY i.id DESC", tuple(params)).fetchall()

    # Pre-calculate Summary Cards metrics based on viewable interventions
    total_interventions = len(interventions)
    active_in_progress = sum(1 for item in interventions if item["status"] == "In Progress")
    resolved_count = sum(1 for item in interventions if item["status"] == "Resolved")
    pending_count = sum(1 for item in interventions if item["status"] == "Pending")
    
    # Average progress percentage
    progresses = [item["progress_pct"] for item in interventions if item["progress_pct"] is not None]
    avg_progress = round(sum(progresses) / len(progresses), 1) if progresses else 0.0

    # Students needing interventions (AI Risk Center detected learning gaps)
    # High gap (>= 60%), Moderate gap (35-59%), and engagement drops
    all_at_risk_students = connection.execute("""
        SELECT student_id, name, average_learning_gap, overall_risk, average_quiz_score, average_attendance
        FROM students
        ORDER BY average_learning_gap DESC
    """).fetchall()

    # Partition by trigger recommendation
    high_sev_candidate = None
    mod_sev_candidate = None
    wellness_candidate = None

    for st in all_at_risk_students:
        gap = float(st["average_learning_gap"] or 0)
        att = float(st["average_attendance"] or 100)
        if gap >= 60.0 and not high_sev_candidate:
            high_sev_candidate = st
        elif 35.0 <= gap < 60.0 and not mod_sev_candidate:
            mod_sev_candidate = st
        elif (att < 75.0 or gap >= 30.0) and not wellness_candidate:
            wellness_candidate = st

    # Fallbacks if partition is sparse
    if not high_sev_candidate and all_at_risk_students:
        high_sev_candidate = all_at_risk_students[0]
    if not mod_sev_candidate and len(all_at_risk_students) > 1:
        mod_sev_candidate = all_at_risk_students[1]
    if not wellness_candidate and len(all_at_risk_students) > 2:
        wellness_candidate = all_at_risk_students[2]

    # Available mentors loaded dynamically from database
    db_mentors = connection.execute("SELECT id, name, title, specialty FROM mentors ORDER BY id ASC").fetchall()
    mentors = []
    for m in db_mentors:
        assigned_count = connection.execute(
            "SELECT COUNT(*) FROM interventions WHERE (mentor_id = ? OR mentor_name = ?) AND status != 'Resolved'",
            (m["id"], m["name"])
        ).fetchone()[0]
        mentors.append({
            "id": m["id"],
            "name": m["name"],
            "title": m["title"],
            "specialty": m["specialty"],
            "load": f"{assigned_count} Active Student{'s' if assigned_count != 1 else ''}"
        })

    connection.close()

    return render_template(
        "interventions.html",
        interventions=interventions,
        total_interventions=total_interventions,
        active_in_progress=active_in_progress,
        resolved_count=resolved_count,
        pending_count=pending_count,
        avg_progress=avg_progress,
        all_at_risk_students=all_at_risk_students,
        high_sev_candidate=high_sev_candidate,
        mod_sev_candidate=mod_sev_candidate,
        wellness_candidate=wellness_candidate,
        mentors=mentors
    )

@app.route("/interventions/create", methods=["POST"])
@login_required
def create_intervention():
    # Only Admin / Instructor can initiate interventions
    if session.get("role") != "admin":
        flash("Only administrative instructors have authority to create remedial interventions.", "error")
        return redirect(url_for("interventions_page"))

    student_id = request.form.get("student_id", "").strip()
    intervention_type = request.form.get("intervention_type", "1-on-1 Mentorship").strip()
    mentor_id_raw = request.form.get("mentor_id")
    mentor_name = request.form.get("mentor_name", "").strip()
    description = request.form.get("description", "Targeted academic recovery protocol initiated.").strip()
    ai_recommended = request.form.get("ai_recommended", "AI-prescribed structured remediation milestones.").strip()
    status = request.form.get("status", "Pending").strip()
    progress_pct = int(request.form.get("progress_pct", 0))

    connection = get_db_connection()

    # Validate student
    st = connection.execute("SELECT student_id, name, overall_risk, average_learning_gap FROM students WHERE student_id = ?", (student_id,)).fetchone()
    if not st:
        connection.close()
        flash(f"Student record '{student_id}' could not be located.", "error")
        return redirect(url_for("interventions_page"))

    # Resolve mentor details
    mentor_id = None
    if mentor_id_raw and mentor_id_raw.isdigit():
        m_rec = connection.execute("SELECT id, name FROM mentors WHERE id = ?", (int(mentor_id_raw),)).fetchone()
        if m_rec:
            mentor_id = m_rec["id"]
            mentor_name = m_rec["name"]
    elif mentor_name:
        m_rec = connection.execute("SELECT id, name FROM mentors WHERE name = ?", (mentor_name,)).fetchone()
        if m_rec:
            mentor_id = m_rec["id"]
            mentor_name = m_rec["name"]

    target_gap = float(st["average_learning_gap"] or 50.0)

    # Insert intervention record
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO interventions (student_id, intervention_type, mentor_name, mentor_id, description, ai_recommended, progress_pct, status, target_gap, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
    """, (student_id, intervention_type, mentor_name or None, mentor_id, description, ai_recommended, progress_pct, status, target_gap))
    intervention_id = cursor.lastrowid

    # If mentor was assigned immediately, record assignment
    if mentor_name:
        cursor.execute("""
            INSERT INTO mentor_assignments (intervention_id, student_id, mentor_id, mentor_name, assigned_by)
            VALUES (?, ?, ?, ?, ?)
        """, (intervention_id, student_id, mentor_id, mentor_name, session.get("username", "admin")))

    connection.commit()
    connection.close()

    flash(f"Intervention created successfully for {st['name']} ({student_id}).", "success")
    return redirect(url_for("interventions_page"))

@app.route("/interventions/assign-mentor/<int:intervention_id>", methods=["POST"])
@login_required
def assign_mentor(intervention_id):
    # Only Admin / Instructor can assign mentors
    if session.get("role") != "admin":
        flash("Unauthorized. Students and mentors cannot reassign faculty mentorships.", "error")
        return redirect(url_for("interventions_page"))

    mentor_id_raw = request.form.get("mentor_id")
    mentor_name = request.form.get("mentor_name", "").strip()

    connection = get_db_connection()
    mentor_id = None
    if mentor_id_raw and mentor_id_raw.isdigit():
        m_rec = connection.execute("SELECT id, name FROM mentors WHERE id = ?", (int(mentor_id_raw),)).fetchone()
        if m_rec:
            mentor_id = m_rec["id"]
            mentor_name = m_rec["name"]
    elif mentor_name:
        m_rec = connection.execute("SELECT id, name FROM mentors WHERE name = ?", (mentor_name,)).fetchone()
        if m_rec:
            mentor_id = m_rec["id"]
            mentor_name = m_rec["name"]

    if not mentor_name:
        connection.close()
        flash("Please select a valid faculty mentor.", "error")
        return redirect(url_for("interventions_page"))

    # Fetch current intervention
    curr = connection.execute("SELECT * FROM interventions WHERE id = ?", (intervention_id,)).fetchone()
    if curr:
        # If currently pending, transition to In Progress upon mentor assignment
        new_status = "In Progress" if curr["status"] == "Pending" else curr["status"]
        connection.execute("""
            UPDATE interventions
            SET mentor_name = ?, mentor_id = ?, status = ?, updated_at = datetime('now')
            WHERE id = ?
        """, (mentor_name, mentor_id, new_status, intervention_id))

        connection.execute("""
            INSERT INTO mentor_assignments (intervention_id, student_id, mentor_id, mentor_name, assigned_by)
            VALUES (?, ?, ?, ?, ?)
        """, (intervention_id, curr["student_id"], mentor_id, mentor_name, session.get("username", "admin")))
        connection.commit()
        flash(f"Assigned Mentor: {mentor_name} (Status: Mentor Assigned).", "success")
    else:
        flash("Intervention protocol record not found.", "error")

    connection.close()
    return redirect(url_for("interventions_page"))

@app.route("/interventions/update-progress/<int:intervention_id>", methods=["POST"])
@login_required
def update_intervention_progress(intervention_id):
    role = session.get("role")
    if role not in ["admin", "mentor"]:
        flash("Unauthorized. Students cannot update intervention progress.", "error")
        return redirect(url_for("interventions_page"))

    progress_pct = int(request.form.get("progress_pct", 0))
    progress_pct = max(0, min(100, progress_pct))
    mentor_notes = request.form.get("mentor_notes", "").strip()

    connection = get_db_connection()
    curr = connection.execute("SELECT * FROM interventions WHERE id = ?", (intervention_id,)).fetchone()
    
    if not curr:
        connection.close()
        flash("Intervention not found.", "error")
        return redirect(url_for("interventions_page"))

    # Permission check for mentor
    if role == "mentor":
        mentor_name = session.get("mentor_name")
        mentor_id = session.get("mentor_id")
        if curr["mentor_name"] != mentor_name and curr["mentor_id"] != mentor_id:
            connection.close()
            flash("You may only update interventions specifically assigned to you.", "error")
            return redirect(url_for("interventions_page"))

    # Status rule: only becomes Resolved when explicitly marked or confirmed, but if progress > 0 and was Pending, shift to In Progress
    new_status = curr["status"]
    if curr["status"] == "Pending" and progress_pct > 0:
        new_status = "In Progress"

    if mentor_notes:
        connection.execute("""
            UPDATE interventions
            SET progress_pct = ?, status = ?, mentor_notes = ?, updated_at = datetime('now')
            WHERE id = ?
        """, (progress_pct, new_status, mentor_notes, intervention_id))
    else:
        connection.execute("""
            UPDATE interventions
            SET progress_pct = ?, status = ?, updated_at = datetime('now')
            WHERE id = ?
        """, (progress_pct, new_status, intervention_id))

    connection.commit()
    connection.close()
    flash(f"Progress updated successfully ({progress_pct}%).", "success")
    return redirect(url_for("interventions_page"))

@app.route("/interventions/resolve/<int:intervention_id>", methods=["POST"])
@login_required
def resolve_intervention(intervention_id):
    role = session.get("role")
    if role not in ["admin", "mentor"]:
        flash("Unauthorized. Only faculty mentors or administrators can resolve interventions.", "error")
        return redirect(url_for("interventions_page"))

    connection = get_db_connection()
    curr = connection.execute("SELECT * FROM interventions WHERE id = ?", (intervention_id,)).fetchone()
    if curr:
        if role == "mentor":
            mentor_name = session.get("mentor_name")
            mentor_id = session.get("mentor_id")
            if curr["mentor_name"] != mentor_name and curr["mentor_id"] != mentor_id:
                connection.close()
                flash("Unauthorized to resolve interventions for other mentors.", "error")
                return redirect(url_for("interventions_page"))

        connection.execute("""
            UPDATE interventions
            SET status = 'Resolved', progress_pct = 100, updated_at = datetime('now')
            WHERE id = ?
        """, (intervention_id,))
        connection.commit()
        flash("Intervention successfully marked as Resolved.", "success")
    connection.close()
    return redirect(url_for("interventions_page"))

@app.route("/interventions/toggle/<int:intervention_id>", methods=["POST"])
@login_required
def toggle_intervention_status(intervention_id):
    if session.get("role") != "admin":
        flash("Administrative privileges required to modify interventions.", "error")
        return redirect(url_for("interventions_page"))

    connection = get_db_connection()
    curr = connection.execute("SELECT status, progress_pct FROM interventions WHERE id = ?", (intervention_id,)).fetchone()
    if curr:
        if curr["status"] == "Resolved":
            new_status = "In Progress"
            new_pct = 60
        elif curr["status"] == "In Progress":
            new_status = "Resolved"
            new_pct = 100
        else:
            new_status = "In Progress"
            new_pct = 25
        connection.execute("UPDATE interventions SET status = ?, progress_pct = ?, updated_at = datetime('now') WHERE id = ?", (new_status, new_pct, intervention_id))
        connection.commit()
    connection.close()
    flash("Intervention protocol status updated.", "success")
    return redirect(url_for("interventions_page"))
    return redirect(url_for("interventions_page"))

# ============================================================
# SETTINGS & ACCOUNT MANAGEMENT
# ============================================================
@app.route("/settings")
@login_required
def settings_page():
    user_id = session.get("user_id")
    connection = get_db_connection()
    
    # Fetch current user details
    current_user = connection.execute(
        "SELECT id, username, email, role, student_id, COALESCE(status, 'active') as status, created_at FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()
    
    # Fetch registered users list: restricted to Admin and Faculty Mentors only
    role = session.get("role")
    if role in ["admin", "mentor"]:
        all_users = connection.execute(
            "SELECT id, username, email, role, student_id, COALESCE(status, 'active') as status, created_at FROM users ORDER BY role ASC, id ASC"
        ).fetchall()
    else:
        # Students are strictly restricted from viewing other students or admins directory
        all_users = []
    
    connection.close()
    
    if not current_user:
        flash("User profile not found.", "error")
        return redirect(url_for("login"))

    return render_template(
        "settings.html",
        current_user=current_user,
        all_users=all_users
    )

@app.route("/change-password", methods=["POST"])
@login_required
def change_password():
    user_id = session.get("user_id")
    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not current_password or not new_password or not confirm_password:
        flash("All password fields are required.", "error")
        return redirect(url_for("settings_page"))

    if new_password != confirm_password:
        flash("New passwords do not match. Please re-type carefully.", "error")
        return redirect(url_for("settings_page"))

    if len(new_password) < 6:
        flash("New password must be at least 6 characters long.", "error")
        return redirect(url_for("settings_page"))

    connection = get_db_connection()
    user = connection.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

    if not user or not check_password_hash(user["password"], current_password):
        connection.close()
        flash("Current password entered is incorrect.", "error")
        return redirect(url_for("settings_page"))

    new_hash = generate_password_hash(new_password)
    connection.execute("UPDATE users SET password = ? WHERE id = ?", (new_hash, user_id))
    connection.commit()
    connection.close()

    flash("Password updated successfully. Please use your new credentials for future sign-ins.", "success")
    return redirect(url_for("settings_page"))

@app.route("/settings/toggle-user/<int:user_id>", methods=["POST"])
@login_required
def toggle_user_status(user_id):
    if session.get("role") != "admin":
        flash("Administrative permissions required to change account status.", "error")
        return redirect(url_for("settings_page"))

    if user_id == session.get("user_id"):
        flash("Cannot deactivate your own active administrative session.", "error")
        return redirect(url_for("settings_page"))

    connection = get_db_connection()
    target_user = connection.execute("SELECT id, username, COALESCE(status, 'active') as status FROM users WHERE id = ?", (user_id,)).fetchone()
    if target_user:
        new_status = "inactive" if target_user["status"] == "active" else "active"
        connection.execute("UPDATE users SET status = ? WHERE id = ?", (new_status, user_id))
        connection.commit()
        flash(f"Account '{target_user['username']}' status set to {new_status.upper()}.", "success")
    connection.close()

    return redirect(url_for("settings_page"))

# ============================================================
# STUDENT MANAGEMENT & GUIDANCE (ADMIN)
# ============================================================
@app.route("/students-management")
@login_required
def students_management():
    if session.get("role") != "admin":
        flash("Access restricted to Academic Administrators.", "error")
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    students = connection.execute("""
        SELECT * FROM students
        ORDER BY student_id ASC
    """).fetchall()
    connection.close()

    return render_template("students_management.html", students=students)

@app.route("/admin/add-student", methods=["POST"])
@login_required
def admin_add_student():
    if session.get("role") != "admin":
        flash("Administrative privileges required.", "error")
        return redirect(url_for("dashboard"))

    student_id = request.form.get("student_id", "").strip().upper()
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    department = request.form.get("department", "Computer Science").strip()

    if not student_id or not name or not email:
        flash("All student fields are required.", "error")
        return redirect(url_for("students_management"))

    connection = get_db_connection()
    existing = connection.execute("SELECT * FROM students WHERE student_id = ?", (student_id,)).fetchone()
    if existing:
        connection.close()
        flash(f"Student ID {student_id} already exists.", "error")
        return redirect(url_for("students_management"))

    connection.execute("""
        INSERT INTO students (student_id, name, email, department, average_quiz_score, average_assignment_score, average_learning_gap, average_attendance, overall_risk)
        VALUES (?, ?, ?, ?, 50.0, 50.0, 50.0, 75.0, 'Medium Risk')
    """, (student_id, name, email, department))

    # Also register a default student user account if username not taken
    user_exist = connection.execute("SELECT * FROM users WHERE username = ?", (student_id.lower(),)).fetchone()
    if not user_exist:
        pwd_hash = generate_password_hash("student123")
        connection.execute("""
            INSERT INTO users (username, email, password, role, student_id)
            VALUES (?, ?, ?, 'student', ?)
        """, (student_id.lower(), email, pwd_hash, student_id))

    connection.commit()
    connection.close()

    flash(f"Student record for {name} ({student_id}) created successfully.", "success")
    return redirect(url_for("students_management"))

@app.route("/student/guidance")
@login_required
def student_guidance_page():
    if session.get("role") != "admin":
        flash("Access restricted to Academic Administrators.", "error")
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    students = connection.execute("""
        SELECT s.*, 
               (SELECT COUNT(*) FROM student_guidance WHERE student_id = s.student_id) as guidance_count,
               (SELECT MAX(created_at) FROM student_guidance WHERE student_id = s.student_id) as last_guided
        FROM students s
        ORDER BY s.average_learning_gap DESC
    """).fetchall()
    connection.close()
    return render_template("students_management.html", students=students)

@app.route("/student/guidance/<student_id>")
@login_required
def guide_student_view(student_id):
    if session.get("role") != "admin":
        flash("Access restricted to Academic Administrators.", "error")
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    student = connection.execute("SELECT * FROM students WHERE student_id = ?", (student_id,)).fetchone()
    if not student:
        connection.close()
        flash("Student record not found.", "error")
        return redirect(url_for("students_management"))

    gaps = connection.execute("""
        SELECT * FROM learning_gaps WHERE student_id = ? ORDER BY learning_gap_score DESC
    """, (student_id,)).fetchall()

    guidance_history = connection.execute("""
        SELECT * FROM student_guidance WHERE student_id = ? ORDER BY id DESC
    """, (student_id,)).fetchall()

    connection.close()
    return render_template("student_guidance.html", student=student, gaps=gaps, guidance_history=guidance_history)

@app.route("/student/guidance/save/<student_id>", methods=["POST"])
@login_required
def save_student_guidance(student_id):
    if session.get("role") != "admin":
        flash("Unauthorized guidance authoring.", "error")
        return redirect(url_for("dashboard"))

    guidance_text = request.form.get("guidance_text", "").strip()
    improvement_goals = request.form.get("improvement_goals", "").strip()
    recommended_topics = request.form.get("recommended_topics", "").strip()
    practice_assignments = request.form.get("practice_assignments", "").strip()

    if not guidance_text:
        flash("Guidance feedback cannot be empty.", "error")
        return redirect(url_for("guide_student_view", student_id=student_id))

    connection = get_db_connection()
    connection.execute("""
        INSERT INTO student_guidance (
            student_id, admin_id, admin_name, guidance_text,
            improvement_goals, recommended_topics, practice_assignments
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        student_id,
        session.get("user_id"),
        session.get("username", "Academic Administrator").title(),
        guidance_text,
        improvement_goals,
        recommended_topics,
        practice_assignments
    ))
    connection.commit()
    connection.close()

    flash(f"Personalized study plan & guidance saved for {student_id}.", "success")
    return redirect(url_for("guide_student_view", student_id=student_id))

# ============================================================
# ASSESSMENTS & PROCTORED EXAMINATIONS
# ============================================================
@app.route("/assessments")
@login_required
def assessments_page():
    connection = get_db_connection()
    role = session.get("role")
    student_id = session.get("student_id") or "S001"

    assessments = connection.execute("""
        SELECT a.*, COUNT(q.id) as q_count
        FROM assessments a
        LEFT JOIN assessment_questions q ON q.assessment_id = a.id
        WHERE a.is_published = 1 OR ? = 'admin'
        GROUP BY a.id
        ORDER BY a.id DESC
    """, (role,)).fetchall()

    student_attempts = {}
    if role == "student":
        attempts = connection.execute("""
            SELECT * FROM assessment_attempts WHERE student_id = ? ORDER BY id DESC
        """, (student_id,)).fetchall()
        for att in attempts:
            if att["assessment_id"] not in student_attempts:
                student_attempts[att["assessment_id"]] = att

    connection.close()
    return render_template("assessments.html", assessments=assessments, student_attempts=student_attempts)

@app.route("/assessments/create", methods=["GET", "POST"])
@login_required
def admin_create_assessment():
    if session.get("role") != "admin":
        flash("Administrative credentials required to author assessments.", "error")
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        subject = request.form.get("subject", "").strip()
        topic = request.form.get("topic", "").strip()
        duration_minutes = int(request.form.get("duration_minutes", 30))
        passing_marks = float(request.form.get("passing_marks", 50.0))
        negative_marking = float(request.form.get("negative_marking", 0.0))
        attempt_limit = int(request.form.get("attempt_limit", 1))
        is_proctored = 1 if request.form.get("is_proctored") else 0
        shuffle_questions = 1 if request.form.get("shuffle_questions") else 0
        shuffle_options = 1 if request.form.get("shuffle_options") else 0

        q_types = request.form.getlist("q_type[]")
        q_texts = request.form.getlist("q_text[]")
        q_marks_list = request.form.getlist("q_marks[]")
        q_opt_as = request.form.getlist("q_opt_a[]")
        q_opt_bs = request.form.getlist("q_opt_b[]")
        q_opt_cs = request.form.getlist("q_opt_c[]")
        q_opt_ds = request.form.getlist("q_opt_d[]")
        q_corrects = request.form.getlist("q_correct[]")
        q_explanations = request.form.getlist("q_explanation[]")

        total_marks = sum(float(m) for m in q_marks_list) if q_marks_list else 100.0

        cur = connection.cursor()
        cur.execute("""
            INSERT INTO assessments (
                title, description, subject, topic, duration_minutes,
                passing_marks, total_marks, negative_marking, attempt_limit,
                shuffle_questions, shuffle_options, is_proctored, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            title, description, subject, topic, duration_minutes,
            passing_marks, total_marks, negative_marking, attempt_limit,
            shuffle_questions, shuffle_options, is_proctored, session.get("username", "Admin")
        ))
        assessment_id = cur.lastrowid

        for i in range(len(q_texts)):
            if q_texts[i].strip():
                cur.execute("""
                    INSERT INTO assessment_questions (
                        assessment_id, question_text, question_type,
                        option_a, option_b, option_c, option_d,
                        correct_answer, marks, explanation
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    assessment_id,
                    q_texts[i].strip(),
                    q_types[i] if i < len(q_types) else 'mcq',
                    q_opt_as[i] if i < len(q_opt_as) else '',
                    q_opt_bs[i] if i < len(q_opt_bs) else '',
                    q_opt_cs[i] if i < len(q_opt_cs) else '',
                    q_opt_ds[i] if i < len(q_opt_ds) else '',
                    q_corrects[i].strip() if i < len(q_corrects) else 'A',
                    float(q_marks_list[i]) if i < len(q_marks_list) else 10.0,
                    q_explanations[i] if i < len(q_explanations) else ''
                ))

        connection.commit()
        connection.close()

        flash(f"Assessment '{title}' published successfully with {len(q_texts)} questions.", "success")
        return redirect(url_for("assessments_page"))

    topics = connection.execute("SELECT topic_name, subject FROM topics ORDER BY subject, topic_name").fetchall()
    connection.close()
    return render_template("admin_create_assessment.html", topics=topics)

@app.route("/assessments/<int:assessment_id>")
@login_required
def assessment_detail(assessment_id):
    connection = get_db_connection()
    assessment = connection.execute("SELECT * FROM assessments WHERE id = ?", (assessment_id,)).fetchone()
    if not assessment:
        connection.close()
        flash("Assessment not found.", "error")
        return redirect(url_for("assessments_page"))

    attempts = connection.execute("""
        SELECT att.*, s.name as student_name
        FROM assessment_attempts att
        LEFT JOIN students s ON s.student_id = att.student_id
        WHERE att.assessment_id = ?
        ORDER BY att.id DESC
    """, (assessment_id,)).fetchall()

    connection.close()
    return render_template("assessment_detail.html", assessment=assessment, attempts=attempts)

@app.route("/assessments/take/<int:assessment_id>")
@login_required
def take_assessment(assessment_id):
    if session.get("role") != "student":
        flash("Admin and evaluator accounts cannot sit for student examination sessions.", "info")
        return redirect(url_for("assessment_detail", assessment_id=assessment_id))

    student_id = session.get("student_id") or "S001"
    connection = get_db_connection()

    assessment = connection.execute("SELECT * FROM assessments WHERE id = ?", (assessment_id,)).fetchone()
    if not assessment:
        connection.close()
        flash("Assessment not found.", "error")
        return redirect(url_for("assessments_page"))

    # Check attempt limit
    completed_attempts = connection.execute("""
        SELECT COUNT(*) FROM assessment_attempts
        WHERE assessment_id = ? AND student_id = ? AND status IN ('submitted', 'evaluated')
    """, (assessment_id, student_id)).fetchone()[0]

    if completed_attempts >= assessment["attempt_limit"]:
        connection.close()
        flash(f"You have reached the maximum attempt limit ({assessment['attempt_limit']}) for this examination.", "error")
        return redirect(url_for("assessments_page"))

    # Find active attempt or create new attempt
    cur = connection.cursor()
    active_attempt = connection.execute("""
        SELECT * FROM assessment_attempts
        WHERE assessment_id = ? AND student_id = ? AND status = 'in_progress'
        ORDER BY id DESC LIMIT 1
    """, (assessment_id, student_id)).fetchone()

    if not active_attempt:
        cur.execute("""
            INSERT INTO assessment_attempts (assessment_id, student_id, max_score, status)
            VALUES (?, ?, ?, 'in_progress')
        """, (assessment_id, student_id, assessment["total_marks"]))
        connection.commit()
        attempt_id = cur.lastrowid
        active_attempt = connection.execute("SELECT * FROM assessment_attempts WHERE id = ?", (attempt_id,)).fetchone()

    # Load questions
    questions = connection.execute("""
        SELECT * FROM assessment_questions WHERE assessment_id = ? ORDER BY id ASC
    """, (assessment_id,)).fetchall()

    # Load existing saved answers
    saved_answers = connection.execute("""
        SELECT question_id, student_answer FROM assessment_answers WHERE attempt_id = ?
    """, (active_attempt["id"],)).fetchall()
    answers_map = {ans["question_id"]: ans["student_answer"] for ans in saved_answers}

    connection.close()
    return render_template("take_assessment.html", assessment=assessment, attempt=active_attempt, questions=questions, answers_map=answers_map)

@app.route("/api/assessment/autosave", methods=["POST"])
@login_required
def api_assessment_autosave():
    data = request.get_json() or {}
    attempt_id = data.get("attempt_id")
    question_id = data.get("question_id")
    answer = str(data.get("answer", "")).strip()
    student_id = session.get("student_id") or "S001"

    if not attempt_id or not question_id:
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    connection = get_db_connection()
    # Upsert answer
    existing = connection.execute("""
        SELECT id FROM assessment_answers WHERE attempt_id = ? AND question_id = ?
    """, (attempt_id, question_id)).fetchone()

    if existing:
        connection.execute("""
            UPDATE assessment_answers
            SET student_answer = ?, last_saved_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (answer, existing["id"]))
    else:
        connection.execute("""
            INSERT INTO assessment_answers (attempt_id, question_id, student_id, student_answer)
            VALUES (?, ?, ?, ?)
        """, (attempt_id, question_id, student_id, answer))

    connection.commit()
    connection.close()
    return jsonify({"status": "success", "saved": True})

@app.route("/api/proctoring/log-event", methods=["POST"])
@login_required
def api_proctoring_log():
    data = request.get_json() or {}
    attempt_id = data.get("attempt_id")
    event_type = data.get("event_type", "warning")
    severity = data.get("severity", "warning")
    details = data.get("details", "")
    student_id = session.get("student_id") or "S001"

    if not attempt_id:
        return jsonify({"status": "error", "message": "Missing attempt_id"}), 400

    connection = get_db_connection()
    att = connection.execute("SELECT assessment_id FROM assessment_attempts WHERE id = ?", (attempt_id,)).fetchone()
    assessment_id = att["assessment_id"] if att else 1

    connection.execute("""
        INSERT INTO proctoring_logs (attempt_id, student_id, assessment_id, event_type, severity, details)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (attempt_id, student_id, assessment_id, event_type, severity, details))

    # Increment attempt flag count
    connection.execute("""
        UPDATE assessment_attempts
        SET proctoring_flag_count = proctoring_flag_count + 1,
            review_status = CASE WHEN review_status = 'normal' THEN 'flagged' ELSE review_status END
        WHERE id = ?
    """, (attempt_id,))

    connection.commit()
    connection.close()
    return jsonify({"status": "logged", "event": event_type})

@app.route("/assessments/submit/<int:assessment_id>", methods=["POST"])
@login_required
def submit_proctored_assessment(assessment_id):
    student_id = session.get("student_id") or "S001"
    attempt_id = request.form.get("attempt_id")

    connection = get_db_connection()
    assessment = connection.execute("SELECT * FROM assessments WHERE id = ?", (assessment_id,)).fetchone()
    questions = connection.execute("SELECT * FROM assessment_questions WHERE assessment_id = ?", (assessment_id,)).fetchall()

    total_score = 0.0
    has_subjective = False

    for q in questions:
        q_id = q["id"]
        q_type = q["question_type"]
        q_marks = float(q["marks"])
        correct_ans = (q["correct_answer"] or "").strip().upper()

        if q_type == "multiple_select":
            submitted_opts = request.form.getlist(f"ans_{q_id}[]")
            submitted_val = ",".join(sorted(submitted_opts))
        else:
            submitted_val = request.form.get(f"ans_{q_id}", "").strip()

        # Check correctness for objective types
        is_correct = 0
        awarded_marks = 0.0

        if q_type == "subjective":
            has_subjective = True
            # Subjective questions remain queued for Admin evaluation
            is_correct = 0
            awarded_marks = 0.0
        elif q_type in ["mcq", "true_false"]:
            if submitted_val.upper() == correct_ans:
                is_correct = 1
                awarded_marks = q_marks
            elif assessment["negative_marking"] > 0 and submitted_val != "":
                awarded_marks = -float(assessment["negative_marking"])
        elif q_type == "multiple_select":
            submitted_set = set(submitted_val.split(",")) if submitted_val else set()
            correct_set = set(correct_ans.split(","))
            if submitted_set == correct_set:
                is_correct = 1
                awarded_marks = q_marks

        total_score += max(0.0, awarded_marks)

        # Upsert answer record
        existing = connection.execute("""
            SELECT id FROM assessment_answers WHERE attempt_id = ? AND question_id = ?
        """, (attempt_id, q_id)).fetchone()

        if existing:
            connection.execute("""
                UPDATE assessment_answers
                SET student_answer = ?, is_correct = ?, awarded_marks = ?, max_marks = ?, last_saved_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (submitted_val, is_correct, awarded_marks, q_marks, existing["id"]))
        else:
            connection.execute("""
                INSERT INTO assessment_answers (attempt_id, question_id, student_id, student_answer, is_correct, awarded_marks, max_marks)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (attempt_id, q_id, student_id, submitted_val, is_correct, awarded_marks, q_marks))

    max_score = float(assessment["total_marks"])
    percentage = (total_score / max_score * 100.0) if max_score > 0 else 0.0
    passed = 1 if percentage >= float(assessment["passing_marks"]) else 0
    status = "submitted" if has_subjective else "evaluated"

    connection.execute("""
        UPDATE assessment_attempts
        SET submitted_at = CURRENT_TIMESTAMP,
            score = ?,
            percentage = ?,
            passed = ?,
            status = ?
        WHERE id = ?
    """, (round(total_score, 1), round(percentage, 1), passed, status, attempt_id))

    # Update student learning gaps based on examination results
    topic_name = assessment["topic"]
    if percentage < 50.0:
        gap_score = 100.0 - percentage
        connection.execute("""
            INSERT OR REPLACE INTO learning_gaps (student_id, topic, learning_gap_score, gap_category, priority)
            VALUES (?, ?, ?, 'High Gap', 'High')
        """, (student_id, topic_name, gap_score))

    connection.commit()
    connection.close()

    flash(f"Examination '{assessment['title']}' submitted successfully! Score: {total_score:.1f}/{max_score}.", "success")
    return redirect(url_for("assessments_page"))

# ============================================================
# EVALUATION OF STUDENT ATTEMPTS (ADMIN)
# ============================================================
@app.route("/assessments/evaluate/<int:attempt_id>")
@login_required
def evaluate_attempt_view(attempt_id):
    if session.get("role") != "admin":
        flash("Evaluation console restricted to Academic Administrators.", "error")
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    attempt = connection.execute("SELECT * FROM assessment_attempts WHERE id = ?", (attempt_id,)).fetchone()
    if not attempt:
        connection.close()
        flash("Attempt not found.", "error")
        return redirect(url_for("assessments_page"))

    assessment = connection.execute("SELECT * FROM assessments WHERE id = ?", (attempt["assessment_id"],)).fetchone()
    student = connection.execute("SELECT * FROM students WHERE student_id = ?", (attempt["student_id"],)).fetchone()

    q_answers = connection.execute("""
        SELECT q.*, ans.id as ans_id, ans.student_answer, ans.awarded_marks, ans.is_correct, ans.feedback
        FROM assessment_questions q
        LEFT JOIN assessment_answers ans ON ans.question_id = q.id AND ans.attempt_id = ?
        WHERE q.assessment_id = ?
        ORDER BY q.id ASC
    """, (attempt_id, attempt["assessment_id"])).fetchall()

    connection.close()
    return render_template("evaluate_attempt.html", attempt=attempt, assessment=assessment, student=student, q_answers=q_answers)

@app.route("/assessments/evaluate/submit/<int:attempt_id>", methods=["POST"])
@login_required
def submit_attempt_evaluation(attempt_id):
    if session.get("role") != "admin":
        flash("Evaluation permissions required.", "error")
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    attempt = connection.execute("SELECT * FROM assessment_attempts WHERE id = ?", (attempt_id,)).fetchone()
    if not attempt:
        connection.close()
        flash("Attempt not found.", "error")
        return redirect(url_for("assessments_page"))

    assessment = connection.execute("SELECT * FROM assessments WHERE id = ?", (attempt["assessment_id"],)).fetchone()
    answers = connection.execute("SELECT id FROM assessment_answers WHERE attempt_id = ?", (attempt_id,)).fetchall()

    total_evaluated_score = 0.0
    for ans in answers:
        ans_id = ans["id"]
        awarded = float(request.form.get(f"awarded_marks_{ans_id}", 0.0))
        feedback = request.form.get(f"feedback_{ans_id}", "").strip()
        total_evaluated_score += awarded

        connection.execute("""
            UPDATE assessment_answers
            SET awarded_marks = ?, feedback = ?
            WHERE id = ?
        """, (awarded, feedback, ans_id))

    review_status = request.form.get("review_status", "reviewed")
    review_notes = request.form.get("review_notes", "").strip()

    max_sc = float(attempt["max_score"])
    new_pct = (total_evaluated_score / max_sc * 100.0) if max_sc > 0 else 0.0
    passed = 1 if new_pct >= float(assessment["passing_marks"]) else 0

    connection.execute("""
        UPDATE assessment_attempts
        SET score = ?,
            percentage = ?,
            passed = ?,
            status = 'evaluated',
            review_status = ?,
            review_notes = ?,
            evaluated_by = ?,
            evaluated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (
        round(total_evaluated_score, 1),
        round(new_pct, 1),
        passed,
        review_status,
        review_notes,
        session.get("username", "Admin"),
        attempt_id
    ))

    # Update student average quiz score
    student_id = attempt["student_id"]
    avg_row = connection.execute("""
        SELECT AVG(percentage) as avg_p FROM assessment_attempts WHERE student_id = ?
    """, (student_id,)).fetchone()
    if avg_row and avg_row["avg_p"] is not None:
        connection.execute("""
            UPDATE students SET average_quiz_score = ? WHERE student_id = ?
        """, (round(avg_row["avg_p"], 1), student_id))

    connection.commit()
    connection.close()

    flash(f"Evaluation finalized for attempt #{attempt_id}. Total Score: {total_evaluated_score:.1f}/{max_sc}.", "success")
    return redirect(url_for("assessment_detail", assessment_id=attempt["assessment_id"]))

# ============================================================
# PROCTORING REVIEW DASHBOARD (ADMIN)
# ============================================================
@app.route("/proctoring-review")
@login_required
def proctoring_review_page():
    if session.get("role") != "admin":
        flash("Proctoring security review restricted to Academic Administrators.", "error")
        return redirect(url_for("dashboard"))

    connection = get_db_connection()
    attempts = connection.execute("""
        SELECT att.*, a.title as assessment_title, s.name as student_name
        FROM assessment_attempts att
        JOIN assessments a ON a.id = att.assessment_id
        LEFT JOIN students s ON s.student_id = att.student_id
        ORDER BY att.id DESC
    """).fetchall()

    proctoring_logs = connection.execute("""
        SELECT l.*, a.title as assessment_title
        FROM proctoring_logs l
        JOIN assessments a ON a.id = l.assessment_id
        ORDER BY l.id DESC LIMIT 100
    """).fetchall()

    total_attempts = len(attempts)
    flagged_attempts = sum(1 for a in attempts if a["proctoring_flag_count"] > 0)
    clean_attempts = total_attempts - flagged_attempts

    connection.close()
    return render_template(
        "proctoring_review.html",
        attempts=attempts,
        proctoring_logs=proctoring_logs,
        total_attempts=total_attempts,
        flagged_attempts=flagged_attempts,
        clean_attempts=clean_attempts
    )

# ============================================================
# YOUTUBE LEARNING RESOURCES (ADMIN & STUDENT)
# ============================================================
@app.route("/youtube-resources")
@login_required
def youtube_resources_page():
    connection = get_db_connection()
    role = session.get("role")
    student_id = session.get("student_id") or "S001"

    if role == "student":
        # Get student's weak topics from actual gaps
        weak_topics = connection.execute("""
            SELECT topic FROM learning_gaps WHERE student_id = ? AND learning_gap_score >= 30.0
        """, (student_id,)).fetchall()
        weak_topic_names = [w["topic"] for w in weak_topics]

        if weak_topic_names:
            placeholders = ",".join("?" for _ in weak_topic_names)
            resources = connection.execute(f"""
                SELECT * FROM youtube_resources
                WHERE topic IN ({placeholders}) OR assigned_to_student_id = ? OR assigned_to_student_id IS NULL OR assigned_to_student_id = ''
                ORDER BY id DESC
            """, (*weak_topic_names, student_id)).fetchall()
        else:
            resources = connection.execute("""
                SELECT * FROM youtube_resources
                WHERE assigned_to_student_id = ? OR assigned_to_student_id IS NULL OR assigned_to_student_id = ''
                ORDER BY id DESC
            """, (student_id,)).fetchall()
    else:
        resources = connection.execute("SELECT * FROM youtube_resources ORDER BY id DESC").fetchall()

    topics = connection.execute("SELECT topic_name FROM topics ORDER BY topic_name").fetchall()
    connection.close()

    return render_template("youtube_resources.html", resources=resources, topics=topics)

@app.route("/youtube-resources/add", methods=["POST"])
@login_required
def add_youtube_resource():
    if session.get("role") != "admin":
        flash("Administrative credentials required to manage learning resources.", "error")
        return redirect(url_for("youtube_resources_page"))

    title = request.form.get("title", "").strip()
    youtube_url = request.form.get("youtube_url", "").strip()
    subject = request.form.get("subject", "").strip()
    topic = request.form.get("topic", "").strip()
    difficulty_level = request.form.get("difficulty_level", "Intermediate")
    assigned_to = request.form.get("assigned_to_student_id", "").strip() or None
    description = request.form.get("description", "").strip()
    learning_objective = request.form.get("learning_objective", "").strip()

    if not title or not youtube_url or not topic:
        flash("Title, YouTube URL, and Topic tag are required.", "error")
        return redirect(url_for("youtube_resources_page"))

    # Extract YouTube ID
    import re
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", youtube_url)
    video_id = match.group(1) if match else ""
    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg" if video_id else ""

    connection = get_db_connection()
    connection.execute("""
        INSERT INTO youtube_resources (
            title, youtube_url, video_id, subject, topic, description,
            difficulty_level, learning_objective, thumbnail_url,
            assigned_to_student_id, created_by_admin
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        title, youtube_url, video_id, subject, topic, description,
        difficulty_level, learning_objective, thumbnail_url,
        assigned_to, session.get("username", "Admin")
    ))
    connection.commit()
    connection.close()

    flash(f"YouTube resource '{title}' added to topic '{topic}'.", "success")
    return redirect(url_for("youtube_resources_page"))

@app.route("/youtube-resources/delete/<int:resource_id>", methods=["POST"])
@login_required
def delete_youtube_resource(resource_id):
    if session.get("role") != "admin":
        flash("Unauthorized deletion.", "error")
        return redirect(url_for("youtube_resources_page"))

    connection = get_db_connection()
    connection.execute("DELETE FROM youtube_resources WHERE id = ?", (resource_id,))
    connection.commit()
    connection.close()

    flash("YouTube learning resource removed.", "success")
    return redirect(url_for("youtube_resources_page"))

# ============================================================
# RUN SERVER
# ============================================================
if __name__ == "__main__":
    app.run(debug=True, port=5000)