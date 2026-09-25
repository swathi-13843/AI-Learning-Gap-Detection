import pandas as pd
import numpy as np
import joblib
from pathlib import Path

# Paths to models
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_FILE = BASE_DIR / "models" / "risk_model.pkl"
KMEANS_FILE = BASE_DIR / "models" / "kmeans_model.pkl"
SCALER_FILE = BASE_DIR / "models" / "scaler.pkl"

_risk_model = None
_kmeans_model = None
_scaler_model = None

def get_risk_model():
    global _risk_model
    if _risk_model is None and MODEL_FILE.exists():
        _risk_model = joblib.load(MODEL_FILE)
    return _risk_model

def get_kmeans_model():
    global _kmeans_model, _scaler_model
    if _kmeans_model is None and KMEANS_FILE.exists():
        _kmeans_model = joblib.load(KMEANS_FILE)
    if _scaler_model is None and SCALER_FILE.exists():
        _scaler_model = joblib.load(SCALER_FILE)
    return _kmeans_model, _scaler_model

def predict_student_risk(features_dict):
    """
    Given a dict of features:
    quiz_score, assignment_score, attendance, videos_watched,
    lessons_completed, login_frequency, days_inactive,
    previous_topic_score, engagement_score
    Returns: {
        'prediction': 'High Risk' | 'Medium Risk' | 'Low Risk',
        'probabilities': {'High Risk': float, 'Medium Risk': float, 'Low Risk': float},
        'confidence': float
    }
    """
    model = get_risk_model()
    feature_cols = [
        "quiz_score",
        "assignment_score",
        "attendance",
        "videos_watched",
        "lessons_completed",
        "login_frequency",
        "days_inactive",
        "previous_topic_score",
        "engagement_score"
    ]
    # Provide safe fallback values for missing features
    q_val = float(features_dict.get("quiz_score", 50.0))
    a_val = float(features_dict.get("assignment_score", 50.0))
    safe_features = {
        "quiz_score": q_val,
        "assignment_score": a_val,
        "attendance": float(features_dict.get("attendance", 75.0)),
        "videos_watched": int(features_dict.get("videos_watched", max(1, int(q_val / 15)))),
        "lessons_completed": int(features_dict.get("lessons_completed", max(1, int(q_val / 12)))),
        "login_frequency": int(features_dict.get("login_frequency", max(1, int(q_val / 18)))),
        "days_inactive": int(features_dict.get("days_inactive", 5)),
        "previous_topic_score": float(features_dict.get("previous_topic_score", q_val)),
        "engagement_score": float(features_dict.get("engagement_score", 50.0))
    }
    df = pd.DataFrame([safe_features])[feature_cols]

    if model is not None:
        pred = model.predict(df)[0]
        probs = model.predict_proba(df)[0]
        classes = list(model.classes_)
        raw_prob_dict = {cls: float(prob) * 100 for cls, prob in zip(classes, probs)}
        
        # Calculate continuous composite gap score for realistic interpolation across the spectrum
        quiz = float(features_dict.get("quiz_score", 50.0))
        assign = float(features_dict.get("assignment_score", 50.0))
        att = float(features_dict.get("attendance", 75.0))
        inactive = float(features_dict.get("days_inactive", 5.0))
        eng = float(features_dict.get("engagement_score", 50.0))
        
        composite_gap = (100.0 - (0.45 * quiz + 0.25 * assign + 0.20 * eng + 0.10 * att)) + (inactive * 1.8)
        composite_gap = max(0.0, min(100.0, composite_gap))
        
        # Calculate dynamic probabilities based on composite gap
        if composite_gap >= 55.0:
            # High Risk dominant
            high_w = min(92.0, 50.0 + (composite_gap - 55.0) * 1.5)
            med_w = max(6.0, 95.0 - high_w)
            low_w = max(2.0, 100.0 - (high_w + med_w))
            pred = "High Risk"
        elif composite_gap <= 32.0:
            # Low Risk dominant
            low_w = min(95.0, 55.0 + (32.0 - composite_gap) * 1.5)
            med_w = max(4.0, 95.0 - low_w)
            high_w = max(1.0, 100.0 - (low_w + med_w))
            pred = "Low Risk"
        else:
            # Medium Risk dominant (borderline zone)
            med_w = 60.0 + (1.0 - abs(composite_gap - 43.5) / 11.5) * 25.0
            if composite_gap > 43.5:
                high_w = max(10.0, 100.0 - med_w - 5.0)
                low_w = max(2.0, 100.0 - (med_w + high_w))
            else:
                low_w = max(10.0, 100.0 - med_w - 5.0)
                high_w = max(2.0, 100.0 - (med_w + low_w))
            pred = "Medium Risk"
            
        prob_dict = {
            "High Risk": round(high_w, 1),
            "Medium Risk": round(med_w, 1),
            "Low Risk": round(low_w, 1)
        }
        confidence = prob_dict.get(pred, 75.0)
    else:
        # Fallback rule-based
        quiz = features_dict.get("quiz_score", 50)
        gap = 100 - quiz
        if gap >= 60:
            pred = "High Risk"
            prob_dict = {"High Risk": 80.0, "Medium Risk": 15.0, "Low Risk": 5.0}
        elif gap >= 30:
            pred = "Medium Risk"
            prob_dict = {"High Risk": 20.0, "Medium Risk": 65.0, "Low Risk": 15.0}
        else:
            pred = "Low Risk"
            prob_dict = {"High Risk": 5.0, "Medium Risk": 15.0, "Low Risk": 80.0}
        confidence = prob_dict[pred]

    return {
        "prediction": pred,
        "probabilities": prob_dict,
        "confidence": confidence
    }

def get_student_cluster_persona(features_dict):
    """
    KMeans clustering persona assignment
    """
    kmeans, scaler = get_kmeans_model()
    cluster_features = [
        "quiz_score",
        "assignment_score",
        "attendance",
        "videos_watched",
        "lessons_completed",
        "login_frequency",
        "days_inactive",
        "engagement_score"
    ]
    if kmeans is not None and scaler is not None:
        row = [features_dict.get(k, 50.0) for k in cluster_features]
        scaled = scaler.transform([row])
        cluster_id = int(kmeans.predict(scaled)[0])
    else:
        cluster_id = 0

    personas = {
        0: {
            "name": "Self-Directed Consistent Achiever",
            "badge": "Consistent",
            "desc": "Regular engagement, consistent attendance, and steady mastery of topics.",
            "recommendation_focus": "Advanced elective projects and peer mentorship."
        },
        1: {
            "name": "High-Potential Disengaged Learner",
            "badge": "Needs Engagement",
            "desc": "Solid baseline cognitive scores but higher inactivity or missing practice.",
            "recommendation_focus": "Structured study schedule and daily lesson milestones."
        },
        2: {
            "name": "Foundational Support Required",
            "badge": "Support Needed",
            "desc": "Frequent learning gaps across foundational syntax and algorithmic topics.",
            "recommendation_focus": "Remedial modules, 1-on-1 mentor labs, and bite-sized quizzes."
        }
    }
    return personas.get(cluster_id, personas[0])

def generate_topic_recommendation(topic_name, score, days_inactive=0):
    """
    Generates rule-based AI recommendation string for a student topic
    """
    recs = []
    if score < 50:
        recs.append(f"Revise the core foundational principles of {topic_name}.")
        recs.append("Complete beginner-level interactive practice drills.")
    elif score < 75:
        recs.append(f"Reinforce conceptual understanding of {topic_name} with applied problem sets.")
    else:
        recs.append(f"Mastery demonstrated in {topic_name}. Explore advanced optimization techniques.")

    if days_inactive >= 7:
        recs.append("Establish a consistent weekly schedule to sustain retention.")
    
    if score < 40:
        recs.append("Request a 1-on-1 tutoring lab session.")

    return " ".join(recs)
