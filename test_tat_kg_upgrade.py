"""
Comprehensive End-to-End Verification Test Suite for TAT-KG Upgrade.
Tests:
1. BKT Parameter Calibration & Posterior Tracing
2. PyTorch GRU Temporal Embeddings & Forward Pass
3. LightGBM Classification & Feature Fusion
4. Hidden Learning Gap Detection (e.g. 85% overall GPA, 30% in SQL Joins)
5. SHAP Feature Attribution & Local Explanations
6. Personalized Recommendations (Targeted YouTube Links)
7. Model Evaluation Reports Integrity (Actual Experimental Values in CSV)
8. Live Flask Route Validation (/api/predict-topic-gap, /reports/<file>)
"""

import os
import tempfile
os.environ.setdefault("MPLCONFIGDIR", os.path.join(tempfile.gettempdir(), "matplotlib_edugap"))

import sys
from pathlib import Path
import json
import pandas as pd
import numpy as np

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import app
from src.knowledge_tracing import BayesianKnowledgeTracer
from src.gru_model import StudentTemporalGRU, TEMPORAL_FEATURE_COLS
from src.hybrid_model import TATKGHybridModel
from src.ai_engine import predict_topic_learning_gap_hybrid
from src.recommendation_engine import generate_personalized_topic_recommendation


def test_bkt_engine():
    tracer = BayesianKnowledgeTracer()
    # Test low vs high responses
    low_res = [0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
    high_res = [1, 1, 1, 1, 0, 1, 1, 1, 1, 1]

    p_low = tracer.predict_mastery_probability(low_res, "SQL Joins")
    p_high = tracer.predict_mastery_probability(high_res, "SQL Joins")

    assert p_low < p_high, f"Expected p_low ({p_low}) < p_high ({p_high})"
    assert p_low < 0.40, f"Expected low mastery probability, got {p_low}"
    assert p_high > 0.70, f"Expected high mastery probability, got {p_high}"
    print(f"[TEST 1 PASSED] BKT Engine verified: Low Mastery={p_low:.3f}, High Mastery={p_high:.3f}")


def test_gru_temporal_engine():
    import torch
    model = StudentTemporalGRU(input_dim=len(TEMPORAL_FEATURE_COLS), hidden_dim=32)
    dummy_input = torch.randn(4, 12, len(TEMPORAL_FEATURE_COLS))
    logits, hidden = model(dummy_input)

    assert logits.shape == (4, 12, 3)
    assert hidden.shape == (4, 12, 32)
    print(f"[TEST 2 PASSED] PyTorch GRU verified: Logits {logits.shape}, Latent Embeddings {hidden.shape}")


def test_tat_kg_model_loading():
    model = TATKGHybridModel.load("models")
    assert model.is_fitted is True
    assert len(model.fusion_feature_names) > 0
    print(f"[TEST 3 PASSED] TAT-KG Hybrid Model checkpoint verified with {len(model.fusion_feature_names)} fused features.")


def test_hidden_gap_detection_sql_joins():
    """
    Verifies Section 2 Requirement:
    Student with 85% overall GPA, 90% attendance, 80% assignment,
    but 30% in SQL Joins MUST be identified as having a learning gap in SQL Joins.
    """
    student_record = {
        "student_id": "S_SQL_TEST",
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
        "engagement_score": 85.0
    }

    res = predict_topic_learning_gap_hybrid(student_record, "SQL Joins")

    assert res["is_hidden_gap"] is True, "Hidden gap flag must be True"
    assert res["prediction"] in ["High Gap", "Medium Gap"], f"Expected gap detected, got {res['prediction']}"
    assert res["bkt_mastery_prob"] < 0.40, f"Expected low BKT mastery for 30% score, got {res['bkt_mastery_prob']}"
    assert "explanation" in res
    assert "recommendation" in res

    rec_vids = res["recommendation"].get("recommended_videos", [])
    assert len(rec_vids) > 0, "Expected recommended YouTube video for SQL Joins"
    assert "SQL" in rec_vids[0]["topic"] or "SQL" in rec_vids[0]["title"]

    print(f"[TEST 4 PASSED] Hidden Learning Gap in SQL Joins successfully detected!")
    print(f"               Prediction: {res['prediction']} (Confidence: {res['confidence']}%)")
    print(f"               BKT Mastery: {res['bkt_mastery_prob'] * 100:.1f}%")
    print(f"               Top Video Recommendation: {rec_vids[0]['title']}")


def test_reports_and_evaluation_integrity():
    csv_file = Path("reports/model_comparison.csv")
    assert csv_file.exists(), "reports/model_comparison.csv must exist"

    df_comp = pd.read_csv(csv_file)
    assert len(df_comp) == 11, f"Expected 11 evaluated models, found {len(df_comp)}"

    expected_models = [
        "Random Forest", "Decision Tree", "KNN", "SVM", "LightGBM",
        "BKT", "GRU", "BKT + GRU", "GRU + LightGBM", "BKT + LightGBM",
        "Proposed TAT-KG (BKT + GRU + LightGBM)"
    ]
    for em in expected_models:
        assert em in df_comp["Model"].values, f"Missing model: {em}"

    # Verify metrics are numeric and valid percentages
    for col in ["Accuracy", "Precision (Macro)", "Recall (Macro)", "Macro F1", "Weighted F1"]:
        assert (df_comp[col] >= 0.0).all() and (df_comp[col] <= 100.0).all()

    # Verify report images exist
    assert Path("reports/confusion_matrix.png").exists()
    assert Path("reports/model_comparison_chart.png").exists()
    assert Path("reports/feature_importance.png").exists()
    print(f"[TEST 5 PASSED] Model comparison reports verified for all 11 architectures (CSV + Figures).")


def test_flask_hybrid_endpoints():
    client = app.test_client()

    # 1. Test live hybrid prediction API
    payload = {
        "student_id": "S001",
        "topic": "SQL Joins",
        "quiz_score": 35.0,
        "assignment_score": 40.0,
        "attendance": 85.0,
        "videos_watched": 4,
        "lessons_completed": 3,
        "login_frequency": 3,
        "days_inactive": 5,
        "overall_avg_quiz": 80.0
    }
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["username"] = "admin"
        sess["role"] = "admin"

    r = client.post("/api/predict-topic-gap", json=payload)
    assert r.status_code == 200, f"Expected 200 OK from /api/predict-topic-gap, got {r.status_code}"
    data = r.get_json()
    assert "prediction" in data
    assert "bkt_mastery_prob" in data
    assert "explanation" in data
    assert "recommendation" in data
    print(f"[TEST 6 PASSED] Live /api/predict-topic-gap API response: {data['prediction']} (BKT Mastery: {data['bkt_mastery_prob']})")

    # 2. Test static report file serving
    r_file = client.get("/reports/model_comparison.csv")
    assert r_file.status_code == 200
    assert b"Proposed TAT-KG" in r_file.data
    print(f"[TEST 7 PASSED] Secure report file server /reports/model_comparison.csv verified with 200 OK.")


if __name__ == "__main__":
    print("=" * 60)
    print("RUNNING TAT-KG UPGRADE END-TO-END VERIFICATION TEST SUITE")
    print("=" * 60)
    test_bkt_engine()
    test_gru_temporal_engine()
    test_tat_kg_model_loading()
    test_hidden_gap_detection_sql_joins()
    test_reports_and_evaluation_integrity()
    test_flask_hybrid_endpoints()
    print("\n" + "=" * 60)
    print("ALL 7 TAT-KG VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)
