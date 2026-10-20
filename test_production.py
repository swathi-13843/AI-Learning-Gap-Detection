import re
from pathlib import Path
from app import app
from src.ai_engine import predict_student_risk, get_student_cluster_persona

def test_no_emojis():
    templates_dir = Path("templates")
    emoji_pattern = re.compile(r"[\U00010000-\U0010ffff]|[\u2600-\u27BF]")
    for p in templates_dir.glob("*.html"):
        content = p.read_text(encoding="utf-8")
        matches = emoji_pattern.findall(content)
        assert len(matches) == 0, f"Found emojis {matches} in {p.name}"
    print("[TEST PASSED] Zero emojis found in all HTML templates.")

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
        "engagement_score": 40.0
    }
    res = predict_student_risk(test_features)
    assert "prediction" in res
    assert "probabilities" in res
    assert res["prediction"] in ["High Risk", "Medium Risk", "Low Risk"]
    print(f"[TEST PASSED] ML Risk Prediction: {res['prediction']} (Confidence: {res['confidence']}%)")

    persona = get_student_cluster_persona(test_features)
    assert "name" in persona
    print(f"[TEST PASSED] Cluster Persona: {persona['name']}")

def test_routes():
    client = app.test_client()
    
    # 1. Login page
    res = client.get("/login")
    assert res.status_code == 200

    # 2. Register page
    res = client.get("/register")
    assert res.status_code == 200

    # 3. Simulate authenticated admin
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["username"] = "admin"
        sess["role"] = "admin"
        sess["student_id"] = None

    # Admin should get 302 redirect on student-only /quizzes
    r_quiz = client.get("/quizzes")
    assert r_quiz.status_code == 302, f"Admin should be redirected from /quizzes, got {r_quiz.status_code}"

    for endpoint in ["/", "/assessments", "/assignments", "/topics", "/analytics", "/interventions", "/student/S001", "/settings"]:
        r = client.get(endpoint)
        assert r.status_code == 200, f"Endpoint {endpoint} failed with code {r.status_code}"
    print("[TEST PASSED] Admin authenticated routes verified with 200 OK.")

    # 4. Simulate student session
    with client.session_transaction() as sess:
        sess["user_id"] = 2
        sess["username"] = "swathi"
        sess["role"] = "student"
        sess["student_id"] = "S001"

    for endpoint in ["/", "/profile", "/quizzes", "/quiz/1", "/settings"]:
        r = client.get(endpoint)
        assert r.status_code == 200, f"Student endpoint {endpoint} failed with code {r.status_code}"
    print("[TEST PASSED] Student authenticated routes verified with 200 OK.")

    # 5. Test API risk prediction endpoint
    r = client.post("/api/predict-risk", json={
        "quiz_score": 85.0,
        "assignment_score": 90.0,
        "attendance": 95.0,
        "videos_watched": 8,
        "lessons_completed": 9,
        "login_frequency": 6,
        "days_inactive": 1,
        "previous_topic_score": 88.0,
        "engagement_score": 90.0
    })
    assert r.status_code == 200
    data = r.get_json()
    assert "prediction" in data
    print(f"[TEST PASSED] Live /api/predict-risk endpoint response: {data['prediction']}")

if __name__ == "__main__":
    test_no_emojis()
    test_ml_inference()
    test_routes()
    print("\nALL PRODUCTION VALIDATION TESTS PASSED SUCCESSFULLY!")
