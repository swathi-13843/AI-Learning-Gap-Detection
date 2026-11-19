"""
Production Verification Test Suite.
Validates:
1. Zero emojis in all HTML templates.
2. Jinja2 template syntax validity.
3. Machine Learning and Hybrid Model Inference.
4. Comprehensive route coverage for both Admin and Student roles.
5. REST API endpoints.
"""

import os
import tempfile
os.environ.setdefault("MPLCONFIGDIR", os.path.join(tempfile.gettempdir(), "matplotlib_edugap"))

import re
import sys
from pathlib import Path
import jinja2

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import app
from src.ai_engine import (
    predict_student_risk,
    get_student_cluster_persona,
    predict_topic_learning_gap_hybrid,
)


def test_no_emojis():
    templates_dir = Path("templates")
    emoji_pattern = re.compile(r"[\U00010000-\U0010ffff]|[\u2600-\u27BF]")
    for p in templates_dir.glob("*.html"):
        content = p.read_text(encoding="utf-8")
        matches = emoji_pattern.findall(content)
        assert len(matches) == 0, f"Found emojis {matches} in {p.name}"
    print("[TEST PASSED] Zero emojis found in all HTML templates.")


def test_template_syntax():
    env = jinja2.Environment()
    for p in Path("templates").glob("*.html"):
        content = p.read_text(encoding="utf-8")
        try:
            env.parse(content)
        except Exception as e:
            raise AssertionError(f"Jinja parse error in {p.name}: {e}")
    print("[TEST PASSED] All Jinja2 templates parse without syntax errors.")


def test_ml_inference():
    test_features = {
        "quiz_score": 42.0,
        "assignment_score": 50.0,
        "attendance": 65.0,
        "videos_watched": 2,
        "lessons_completed": 3,
        "login_frequency": 2,
        "days_inactive": 8,
        "previous_topic_score": 40.0,
        "engagement_score": 40.0,
    }
    res = predict_student_risk(test_features)
    assert "prediction" in res
    assert "probabilities" in res
    assert res["prediction"] in ["High Risk", "Medium Risk", "Low Risk"]
    print(f"[TEST PASSED] ML Risk Prediction: {res['prediction']} (Confidence: {res['confidence']}%)")

    persona = get_student_cluster_persona(test_features)
    assert "name" in persona
    print(f"[TEST PASSED] Cluster Persona: {persona['name']}")

    hybrid_res = predict_topic_learning_gap_hybrid(
        {
            "student_id": "S_TEST",
            "overall_avg_quiz": 85.0,
            "average_quiz_score": 85.0,
            "attendance": 90.0,
            "assignment_score": 80.0,
            "quiz_score": 30.0,
            "correct_answers": 6,
            "total_questions": 20,
            "quiz_attempts": 2,
            "videos_watched": 8,
            "lessons_completed": 8,
            "login_frequency": 6,
            "days_inactive": 1,
            "previous_topic_score": 85.0,
            "engagement_score": 85.0,
        },
        "SQL Joins",
    )
    assert hybrid_res["is_hidden_gap"] is True
    print(f"[TEST PASSED] TAT-KG Hybrid Inference: {hybrid_res['prediction']} (BKT Mastery: {hybrid_res['bkt_mastery_prob']:.2f})")


def test_all_routes():
    client = app.test_client()

    # 1. Public Authentication Routes
    for pub_route in ["/login", "/register"]:
        r = client.get(pub_route)
        assert r.status_code == 200, f"Public route {pub_route} returned {r.status_code}"
    print("[TEST PASSED] Public authentication routes verified with 200 OK.")

    # 2. Admin Authenticated Routes
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["username"] = "admin"
        sess["role"] = "admin"
        sess["student_id"] = None

    admin_endpoints = [
        "/",
        "/assessments",
        "/assessments/1",
        "/assessments/create",
        "/assessments/evaluate/1",
        "/proctoring-review",
        "/youtube-resources",
        "/students-management",
        "/student/guidance",
        "/student/guidance/S001",
        "/assignments",
        "/topics",
        "/analytics",
        "/interventions",
        "/student/S001",
        "/settings",
        "/theory",
        "/theory/SQL%20Joins",
        "/video-learning",
        "/academic-tracker",
        "/heatmap",
        "/future-predictions",
        "/admin/export-students-csv",
        "/api/curriculum-roadmap/SQL%20Joins",
        "/reports/model_comparison.csv",
    ]

    for endpoint in admin_endpoints:
        r = client.get(endpoint)
        assert r.status_code == 200, f"Admin endpoint {endpoint} returned {r.status_code}"
    print(f"[TEST PASSED] All {len(admin_endpoints)} Admin endpoints verified with 200 OK.")

    # 3. Student Authenticated Routes
    with client.session_transaction() as sess:
        sess["user_id"] = 2
        sess["username"] = "swathi"
        sess["role"] = "student"
        sess["student_id"] = "S001"

    student_endpoints = [
        "/",
        "/profile",
        "/quizzes",
        "/quiz/1",
        "/assessments",
        "/assessments/take/1",
        "/assignments",
        "/topics",
        "/youtube-resources",
        "/settings",
        "/theory",
        "/theory/SQL%20Joins",
        "/video-learning",
        "/academic-tracker",
        "/heatmap",
        "/learning-path",
        "/future-predictions",
        "/student/download-report/S001",
    ]

    for endpoint in student_endpoints:
        r = client.get(endpoint)
        assert r.status_code == 200, f"Student endpoint {endpoint} returned {r.status_code}"
    print(f"[TEST PASSED] All {len(student_endpoints)} Student endpoints verified with 200 OK.")

    # 4. API Endpoints
    r_risk = client.post("/api/predict-risk", json={
        "quiz_score": 85.0,
        "assignment_score": 90.0,
        "attendance": 95.0,
        "videos_watched": 8,
        "lessons_completed": 9,
        "login_frequency": 6,
        "days_inactive": 1,
        "previous_topic_score": 88.0,
        "engagement_score": 90.0,
    })
    assert r_risk.status_code == 200
    assert "prediction" in r_risk.get_json()

    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["username"] = "admin"
        sess["role"] = "admin"

    r_topic = client.post("/api/predict-topic-gap", json={
        "student_id": "S001",
        "topic": "SQL Joins",
        "quiz_score": 35.0,
        "assignment_score": 40.0,
        "attendance": 85.0,
        "videos_watched": 4,
        "lessons_completed": 3,
        "login_frequency": 3,
        "days_inactive": 5,
        "overall_avg_quiz": 80.0,
    })
    assert r_topic.status_code == 200
    assert "prediction" in r_topic.get_json()
    print("[TEST PASSED] REST API endpoints /api/predict-risk and /api/predict-topic-gap verified with 200 OK.")


def test_new_student_risk_status():
    from app import get_db_connection, evaluate_student_risk_status
    import uuid
    client = app.test_client()
    test_uid = f"STEST_{uuid.uuid4().hex[:6].upper()}"
    test_user = f"newuser_{uuid.uuid4().hex[:6]}"

    # Register new user
    r = client.post("/register", data={
        "username": test_user,
        "email": f"{test_user}@test.edu",
        "password": "Password123!",
        "student_id": test_uid
    }, follow_redirects=True)
    assert r.status_code == 200

    conn = get_db_connection()
    st = conn.execute("SELECT * FROM students WHERE student_id = ?", (test_uid,)).fetchone()
    assert st is not None, "New student record not created"
    assert st["overall_risk"] == "Assessment Pending", f"Expected Assessment Pending, got {st['overall_risk']}"
    assert st["completed_assessments_count"] == 0, f"Expected 0 completed assessments, got {st['completed_assessments_count']}"

    # Evaluate risk without assessments
    status, conf = evaluate_student_risk_status(test_uid, conn)
    assert status == "Assessment Pending"
    assert conf == 0.0

    # Cleanup test record
    conn.execute("DELETE FROM students WHERE student_id = ?", (test_uid,))
    conn.execute("DELETE FROM users WHERE student_id = ?", (test_uid,))
    conn.commit()
    conn.close()
    print("[TEST PASSED] New user registration correctly defaults to Assessment Pending (Zero activity bias).")


if __name__ == "__main__":
    print("=" * 60)
    print("RUNNING PRODUCTION VERIFICATION TEST SUITE")
    print("=" * 60)
    test_no_emojis()
    test_template_syntax()
    test_ml_inference()
    test_all_routes()
    test_new_student_risk_status()
    print("\n" + "=" * 60)
    print("ALL PRODUCTION VALIDATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)
