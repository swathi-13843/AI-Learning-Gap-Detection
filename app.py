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
        student_id = session.get("student_id")
        student = connection.execute(
            "SELECT * FROM students WHERE student_id = ?",
            (student_id,)
        ).fetchone()

        if student is None:
            connection.close()
            return render_template(
                "dashboard.html",
                total_students=0,
                high_risk=0,
                medium_risk=0,
                low_risk=0,
                students=[],
                current_student=None
            )

        connection.close()
        return render_template(
            "dashboard.html",
            total_students=1,
            high_risk=1 if student["overall_risk"] == "High Risk" else 0,
            medium_risk=1 if student["overall_risk"] == "Medium Risk" else 0,
            low_risk=1 if student["overall_risk"] == "Low Risk" else 0,
            students=[student],
            current_student=student
        )

    # ADMIN / INSTRUCTOR DASHBOARD
    total_students = connection.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    high_risk = connection.execute("SELECT COUNT(*) FROM students WHERE overall_risk = 'High Risk'").fetchone()[0]
    medium_risk = connection.execute("SELECT COUNT(*) FROM students WHERE overall_risk = 'Medium Risk'").fetchone()[0]
    low_risk = connection.execute("SELECT COUNT(*) FROM students WHERE overall_risk = 'Low Risk'").fetchone()[0]

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
        high_risk=high_risk,
        medium_risk=medium_risk,
        low_risk=low_risk,
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
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            session["student_id"] = user["student_id"]
            
            if user["role"] == "mentor":
                conn = get_db_connection()
                mentor_rec = conn.execute("SELECT id, name FROM mentors WHERE user_id = ? OR email = ?", (user["id"], user["email"])).fetchone()
                if mentor_rec:
                    session["mentor_id"] = mentor_rec["id"]
                    session["mentor_name"] = mentor_rec["name"]
                else:
                    session["mentor_name"] = user["username"]
                conn.close()

            elif user["role"] == "student" and user["student_id"]:
                # Ensure logging-in student has an active intervention and assigned mentor
                st_id = user["student_id"]
                conn = get_db_connection()
                
                # Check for active intervention
                active_int = conn.execute("""
                    SELECT id, mentor_name, mentor_id, status FROM interventions
                    WHERE student_id = ? AND status != 'Resolved'
                    ORDER BY id DESC LIMIT 1
                """, (st_id,)).fetchone()

                if not active_int or not active_int["mentor_name"]:
                    # Select mentor with lowest active mentee workload
                    chosen_mentor = conn.execute("""
                        SELECT m.id, m.name, m.title, m.specialty, COUNT(i.id) as load
                        FROM mentors m
                        LEFT JOIN interventions i ON (i.mentor_id = m.id OR i.mentor_name = m.name) AND i.status != 'Resolved'
                        GROUP BY m.id
                        ORDER BY load ASC, m.id ASC
                        LIMIT 1
                    """).fetchone()

                    # Retrieve student stats for context
                    st_row = conn.execute("SELECT name, overall_risk, average_learning_gap FROM students WHERE student_id = ?", (st_id,)).fetchone()
                    st_name = st_row["name"] if st_row else user["username"].title()
                    target_gap = float(st_row["average_learning_gap"]) if (st_row and st_row["average_learning_gap"]) else 45.0
                    risk_lvl = st_row["overall_risk"] if (st_row and st_row["overall_risk"]) else "Medium Risk"

                    cur = conn.cursor()
                    if active_int:
                        # Update existing intervention with assigned mentor
                        cur.execute("""
                            UPDATE interventions
                            SET mentor_id = ?, mentor_name = ?, status = 'In Progress', updated_at = datetime('now')
                            WHERE id = ?
                        """, (chosen_mentor["id"], chosen_mentor["name"], active_int["id"]))
                        int_id = active_int["id"]
                    else:
                        # Determine intervention type based on learning gap / risk
                        if target_gap >= 60.0 or risk_lvl == "High Risk":
                            int_type = "1-on-1 Dedicated Faculty Mentorship"
                            desc = "Weekly 45-minute clinical tutoring sessions with domain faculty mentor."
                            ai_sol = "Personalized concept mastery refreshers and homework reviews."
                        elif target_gap >= 35.0:
                            int_type = "Micro-Quiz Adaptive Remediation Loop"
                            desc = "Targeted adaptive quiz loops with continuous performance tracking."
                            ai_sol = "Topic-specific micro-assessments and immediate explanatory feedback."
                        else:
                            int_type = "Academic Counseling & Mentorship"
                            desc = "Academic wellness, schedule check-ins, and study milestones."
                            ai_sol = "Weekly milestone alignment and guided academic roadmaps."

                        cur.execute("""
                            INSERT INTO interventions (student_id, intervention_type, mentor_name, mentor_id, description, ai_recommended, progress_pct, status, target_gap, created_at, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?, 25, 'In Progress', ?, datetime('now'), datetime('now'))
                        """, (st_id, int_type, chosen_mentor["name"], chosen_mentor["id"], desc, ai_sol, target_gap))
                        int_id = cur.lastrowid

                    # Record in mentor_assignments table
                    cur.execute("""
                        INSERT INTO mentor_assignments (intervention_id, student_id, mentor_id, mentor_name, assigned_by)
                        VALUES (?, ?, ?, ?, 'System AI Auto-Assign')
                    """, (int_id, st_id, chosen_mentor["id"], chosen_mentor["name"]))

                    conn.commit()
                conn.close()

            flash(f"Welcome back, {session.get('mentor_name', user['username'])}.", "success")
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

    connection.close()

    return render_template(
        "student.html",
        student=student,
        gaps=gaps,
        recommendations=recommendations
    )

# ============================================================
# ADAPTIVE QUIZZES
# ============================================================
@app.route("/quizzes")
@login_required
def quizzes_page():
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
# ASSIGNMENTS
# ============================================================
@app.route("/assignments")
@login_required
def assignments_page():
    connection = get_db_connection()
    assignments = connection.execute("""
        SELECT a.*, t.topic_name, t.subject
        FROM assignments a
        JOIN topics t ON a.topic_id = t.id
        ORDER BY a.id
    """).fetchall()

    student_id = session.get("student_id") or "S001"
    submissions = connection.execute("""
        SELECT * FROM submissions WHERE student_id = ?
    """, (student_id,)).fetchall()
    
    submission_map = {sub["assignment_id"]: sub for sub in submissions}
    connection.close()

    return render_template("assignments.html", assignments=assignments, submission_map=submission_map)

@app.route("/assignment/submit/<int:assignment_id>", methods=["POST"])
@login_required
def submit_assignment(assignment_id):
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

    # Record submission with status Submitted and score
    awarded_score = 90.0
    connection.execute("""
        INSERT INTO submissions (assignment_id, student_id, score, status, feedback, file_name, github_repo, comments)
        VALUES (?, ?, ?, 'Submitted', 'Submission logged successfully. Evaluator code review queued.', ?, ?, ?)
    """, (assignment_id, student_id, awarded_score, file_name, github_repo, comments))

    # Update student average_assignment_score
    sub_avg = connection.execute("""
        SELECT AVG(score) as avg_sc FROM submissions WHERE student_id = ?
    """, (student_id,)).fetchone()

    if sub_avg and sub_avg["avg_sc"] is not None:
        connection.execute("""
            UPDATE students SET average_assignment_score = ? WHERE student_id = ?
        """, (round(sub_avg["avg_sc"], 2), student_id))

    connection.commit()
    connection.close()

    flash(f"Work submitted for '{assignment['title']}'! Submission recorded with evaluator review in progress.", "success")
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

    if student_id:
        # Fetch student_topics records
        st_rows = connection.execute("""
            SELECT st.*, t.topic_name, t.subject, t.description
            FROM student_topics st
            JOIN topics t ON st.topic_id = t.id
            WHERE st.student_id = ?
        """, (student_id,)).fetchall()

        st_map = {row["topic_id"]: row for row in st_rows}

        # If student has no student_topics records yet, check learning_gaps
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
                
                # Classification of strength
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
    else:
        # Admin view - Cohort aggregate coverage
        cohort_stats = connection.execute("""
            SELECT topic_id, AVG(score) as avg_score, AVG(learning_gap_score) as avg_gap
            FROM student_topics
            GROUP BY topic_id
        """).fetchall()
        cohort_map = {row["topic_id"]: row for row in cohort_stats}

        for t in all_topics:
            tid = t["id"]
            if tid in cohort_map:
                c_avg_sc = round(float(cohort_map[tid]["avg_score"]), 1)
                c_avg_gap = round(float(cohort_map[tid]["avg_gap"]), 1)
                covered_count += 1
                if c_avg_sc >= 70:
                    strong_topics.append(t["topic_name"])
                    status_tier = "strong"
                elif c_avg_gap >= 45:
                    weak_topics.append(t["topic_name"])
                    status_tier = "weak"
                else:
                    status_tier = "moderate"

                topics_with_status.append({
                    "id": t["id"],
                    "topic_name": t["topic_name"],
                    "subject": t["subject"],
                    "description": t["description"],
                    "is_covered": True,
                    "score": c_avg_sc,
                    "gap": c_avg_gap,
                    "status_tier": status_tier,
                    "gap_category": "Cohort Metric",
                    "priority": "Monitored"
                })
            else:
                topics_with_status.append({
                    "id": t["id"],
                    "topic_name": t["topic_name"],
                    "subject": t["subject"],
                    "description": t["description"],
                    "is_covered": False,
                    "score": 50.0,
                    "gap": 50.0,
                    "status_tier": "moderate",
                    "gap_category": "Syllabus Standard",
                    "priority": "Scheduled"
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
        curriculum_roadmap=CURRICULUM_ROADMAP
    )

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
# RUN SERVER
# ============================================================
if __name__ == "__main__":
    app.run(debug=True, port=5000)