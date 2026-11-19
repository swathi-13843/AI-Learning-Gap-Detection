"""
Adaptive Learning, Mastery Heatmap, and Future Gap Prediction Engine for EduGap AI.
Implements:
1. Topic-Wise Knowledge Mastery Heatmap (Green, Yellow, Red, Grey)
2. Personalized 6-Step Adaptive Learning Path Generation
3. Future Learning Gap Prediction (Prerequisite-Aware & Temporal Without Data Leakage)
4. Intervention Recovery & Mastery Improvement Tracking
"""

import sqlite3
import json
from pathlib import Path
import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "database" / "learning_gap.db"

from src.knowledge_tracing import BayesianKnowledgeTracer
from src.curriculum_data import CURRICULUM_ROADMAP

# Canonical list of 12 curriculum topics
CURRICULUM_TOPICS = [
    {"name": "Python Basics", "subject": "Python", "unit": "Unit 1", "prereq": None, "difficulty": "Beginner"},
    {"name": "OOP", "subject": "Python", "unit": "Unit 2", "prereq": "Python Basics", "difficulty": "Intermediate"},
    {"name": "SQL", "subject": "Database", "unit": "Unit 1", "prereq": None, "difficulty": "Beginner"},
    {"name": "SQL Joins", "subject": "Database", "unit": "Unit 2", "prereq": "SQL", "difficulty": "Intermediate"},
    {"name": "Statistics", "subject": "Data Science", "unit": "Unit 1", "prereq": None, "difficulty": "Beginner"},
    {"name": "Probability", "subject": "Data Science", "unit": "Unit 2", "prereq": "Statistics", "difficulty": "Intermediate"},
    {"name": "Regression", "subject": "Machine Learning", "unit": "Unit 1", "prereq": "Statistics", "difficulty": "Intermediate"},
    {"name": "Classification", "subject": "Machine Learning", "unit": "Unit 2", "prereq": "Statistics", "difficulty": "Intermediate"},
    {"name": "Decision Trees", "subject": "Machine Learning", "unit": "Unit 3", "prereq": "Classification", "difficulty": "Intermediate"},
    {"name": "Random Forest", "subject": "Machine Learning", "unit": "Unit 4", "prereq": "Decision Trees", "difficulty": "Advanced"},
    {"name": "K-Means", "subject": "Machine Learning", "unit": "Unit 5", "prereq": "Statistics", "difficulty": "Intermediate"},
    {"name": "PCA", "subject": "Data Science", "unit": "Unit 6", "prereq": "Statistics", "difficulty": "Advanced"}
]


def get_topic_mastery_heatmap(student_id):
    """
    Computes visual knowledge mastery for all 12 curriculum topics.
    Returns:
    - Green (Strong: Mastery >= 70%)
    - Yellow (Moderate: Mastery 40% - 69%)
    - Red (Needs Improvement: Mastery < 40%)
    - Grey (Not Evaluated: 0 attempts / insufficient data)
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    tracer = BayesianKnowledgeTracer()
    heatmap_data = []

    for topic_info in CURRICULUM_TOPICS:
        t_name = topic_info["name"]

        # Check completed quiz attempts and assessment attempts
        q_attempts = cursor.execute("""
            SELECT qa.score, qa.percentage
            FROM quiz_attempts qa
            JOIN quizzes q ON qa.quiz_id = q.id
            JOIN topics t ON q.topic_id = t.id
            WHERE qa.student_id = ? AND t.topic_name = ?
            ORDER BY qa.id ASC
        """, (student_id, t_name)).fetchall()

        ass_attempts = cursor.execute("""
            SELECT aa.score, aa.percentage
            FROM assessment_attempts aa
            JOIN assessments a ON aa.assessment_id = a.id
            WHERE aa.student_id = ? AND a.topic = ? AND (aa.status = 'evaluated' OR aa.score IS NOT NULL)
            ORDER BY aa.id ASC
        """, (student_id, t_name)).fetchall()

        total_attempts = len(q_attempts) + len(ass_attempts)

        if total_attempts == 0:
            # Not Evaluated / Grey
            heatmap_data.append({
                "topic": t_name,
                "subject": topic_info["subject"],
                "unit": topic_info["unit"],
                "difficulty": topic_info["difficulty"],
                "prerequisite": topic_info["prereq"],
                "status": "Not Evaluated",
                "tier": "not_evaluated",
                "color": "#64748b",
                "badge_class": "badge-neutral",
                "mastery_prob": None,
                "mastery_pct": None,
                "attempts_count": 0,
                "learning_gap_score": None,
                "is_evaluated": False,
                "action_prompt": f"Start initial quiz on {t_name}"
            })
        else:
            # Construct binary response trial sequence for BKT
            responses = []
            for qa in q_attempts:
                pct = float(qa["percentage"] or 0.0)
                responses.extend([1 if pct >= 60 else 0])
            for aa in ass_attempts:
                pct = float(aa["percentage"] or 0.0)
                responses.extend([1 if pct >= 60 else 0])

            if not responses:
                responses = [1 if float(q_attempts[0]["percentage"]) >= 50 else 0]

            p_mastery = tracer.predict_mastery_probability(responses, t_name)
            mastery_pct = int(round(p_mastery * 100))
            gap_score = max(0.0, min(100.0, 100.0 - mastery_pct))

            if mastery_pct >= 70:
                tier = "strong"
                color = "#10b981"
                status = "Strong Mastery"
                badge_class = "badge-low"
            elif mastery_pct >= 40:
                tier = "moderate"
                color = "#f59e0b"
                status = "Moderate Understanding"
                badge_class = "badge-medium"
            else:
                tier = "weak"
                color = "#ef4444"
                status = "Needs Improvement"
                badge_class = "badge-high"

            heatmap_data.append({
                "topic": t_name,
                "subject": topic_info["subject"],
                "unit": topic_info["unit"],
                "difficulty": topic_info["difficulty"],
                "prerequisite": topic_info["prereq"],
                "status": status,
                "tier": tier,
                "color": color,
                "badge_class": badge_class,
                "mastery_prob": round(p_mastery, 3),
                "mastery_pct": mastery_pct,
                "attempts_count": total_attempts,
                "learning_gap_score": gap_score,
                "is_evaluated": True,
                "action_prompt": "Review theory & practice" if tier == "weak" else "Solid performance"
            })

    conn.close()
    return heatmap_data


def get_or_create_learning_path(student_id):
    """
    Generates or retrieves a personalized 6-step adaptive learning path:
    1. Identify weak topic (e.g. SQL Joins)
    2. Step 1: Read Theory Material
    3. Step 2: Analyze Conceptual Diagram
    4. Step 3: Watch Curated YouTube Lecture
    5. Step 4: Complete Beginner Practice Quiz
    6. Step 5: Complete Intermediate/Advanced Assessment
    7. Step 6: Recalculate Mastery & Verify Gap Recovery
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Check if active path exists
    active_path = cursor.execute("""
        SELECT * FROM student_learning_paths
        WHERE student_id = ? AND status = 'In Progress'
        ORDER BY id DESC LIMIT 1
    """, (student_id,)).fetchone()

    if active_path:
        steps = json.loads(active_path["steps_json"])
        conn.close()
        return {
            "id": active_path["id"],
            "student_id": student_id,
            "topic_name": active_path["topic_name"],
            "current_step": active_path["current_step"],
            "total_steps": active_path["total_steps"],
            "steps": steps,
            "status": active_path["status"],
            "initial_mastery": active_path["initial_mastery"],
            "reassessed_mastery": active_path["reassessed_mastery"]
        }

    # Otherwise identify candidate weak topic from heatmap or learning_gaps
    heatmap = get_topic_mastery_heatmap(student_id)
    weak_candidates = [h for h in heatmap if h["is_evaluated"] and h["tier"] == "weak"]
    if not weak_candidates:
        moderate_candidates = [h for h in heatmap if h["is_evaluated"] and h["tier"] == "moderate"]
        target_topic = moderate_candidates[0]["topic"] if moderate_candidates else "SQL Joins"
        initial_m = moderate_candidates[0]["mastery_pct"] if moderate_candidates else 35.0
    else:
        # Pick weakest evaluated topic
        weak_candidates.sort(key=lambda x: x["mastery_pct"] if x["mastery_pct"] is not None else 0)
        target_topic = weak_candidates[0]["topic"]
        initial_m = float(weak_candidates[0]["mastery_pct"] or 25.0)

    # Build 6-step learning sequence
    steps = [
        {
            "step": 1,
            "title": f"Study Theory: {target_topic}",
            "description": f"Read the comprehensive definition, core formulas, advantages, and exam questions for {target_topic}.",
            "action_url": f"/theory/{target_topic}",
            "action_label": "Read Theory Concepts",
            "is_completed": False
        },
        {
            "step": 2,
            "title": f"Analyze Conceptual Diagram: {target_topic}",
            "description": f"Examine the architectural workflow and data flow diagrams in the theory module.",
            "action_url": f"/theory/{target_topic}#diagram",
            "action_label": "View Visual Architecture",
            "is_completed": False
        },
        {
            "step": 3,
            "title": f"Watch Educational Video Lecture: {target_topic}",
            "description": f"Watch the verified tutorial lecture on {target_topic} and mark as completed.",
            "action_url": f"/video-learning?topic={target_topic}",
            "action_label": "Stream Lecture Video",
            "is_completed": False
        },
        {
            "step": 4,
            "title": f"Complete Beginner Practice Quiz: {target_topic}",
            "description": f"Solve 5 foundational questions to reinforce core terminology and syntax.",
            "action_url": "/quizzes",
            "action_label": "Take Practice Quiz",
            "is_completed": False
        },
        {
            "step": 5,
            "title": f"Sit for Intermediate Proctored Assessment: {target_topic}",
            "description": "Demonstrate concept proficiency under timed evaluation conditions.",
            "action_url": "/assessments",
            "action_label": "Take Assessment",
            "is_completed": False
        },
        {
            "step": 6,
            "title": f"Recalculate Mastery & Verify Gap Recovery",
            "description": "Execute AI BKT updating to confirm concept mastery elevation and gap closure.",
            "action_url": "/learning-path/reassess",
            "action_label": "Verify Mastery Recovery",
            "is_completed": False
        }
    ]

    cursor.execute("""
        INSERT INTO student_learning_paths (student_id, topic_name, current_step, total_steps, steps_json, status, initial_mastery, reassessed_mastery)
        VALUES (?, ?, 1, 6, ?, 'In Progress', ?, ?)
    """, (student_id, target_topic, json.dumps(steps), initial_m, initial_m))
    conn.commit()
    path_id = cursor.lastrowid
    conn.close()

    return {
        "id": path_id,
        "student_id": student_id,
        "topic_name": target_topic,
        "current_step": 1,
        "total_steps": 6,
        "steps": steps,
        "status": "In Progress",
        "initial_mastery": initial_m,
        "reassessed_mastery": initial_m
    }


def predict_future_learning_gaps(student_id):
    """
    Predicts future topic-level difficulty using historical data only.
    Prevents data leakage by relying solely on prerequisite mastery and temporal pace.
    """
    heatmap = get_topic_mastery_heatmap(student_id)
    mastery_map = {h["topic"]: (h["mastery_prob"] if h["is_evaluated"] else 0.50) for h in heatmap}
    evaluated_topics = {h["topic"] for h in heatmap if h["is_evaluated"]}

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    st = cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,)).fetchone()
    conn.close()

    overall_avg = float(st["average_quiz_score"]) if st and st["average_quiz_score"] is not None else 50.0
    overall_att = float(st["average_attendance"]) if st and st["average_attendance"] is not None else 75.0

    future_predictions = []

    for topic_info in CURRICULUM_TOPICS:
        t_name = topic_info["name"]
        prereq = topic_info["prereq"]

        # Only predict for topics not yet mastered or upcoming
        is_already_mastered = (t_name in evaluated_topics and (mastery_map.get(t_name, 0) >= 0.70))

        prereq_mastery = mastery_map.get(prereq, 0.55) if prereq else 0.75
        diff_factor = 0.85 if topic_info["difficulty"] == "Advanced" else (0.95 if topic_info["difficulty"] == "Intermediate" else 1.05)

        # Mathematical forecast: P(Future Mastery) = 0.55 * Prereq + 0.35 * (Overall_Avg / 100) * diff_factor - penalty
        pred_mastery = float(np.clip(
            0.55 * prereq_mastery + 0.35 * (overall_avg / 100.0) * diff_factor + (overall_att / 100.0) * 0.10,
            0.10,
            0.95
        ))
        pred_gap_prob = round((1.0 - pred_mastery) * 100.0, 1)

        if pred_gap_prob >= 55.0:
            risk_level = "High Future Risk"
            badge = "badge-high"
            preventive_advice = f"Strong prerequisite deficit detected in {prereq or 'foundational theory'}. Complete {prereq or 'basics'} review prior to advancing."
        elif pred_gap_prob >= 35.0:
            risk_level = "Moderate Future Risk"
            badge = "badge-medium"
            preventive_advice = f"Review foundational materials and practice questions for {t_name} to reinforce understanding."
        else:
            risk_level = "Low Future Risk"
            badge = "badge-low"
            preventive_advice = f"Good academic readiness expected based on strong {prereq or 'baseline'} mastery."

        future_predictions.append({
            "topic": t_name,
            "subject": topic_info["subject"],
            "difficulty": topic_info["difficulty"],
            "prerequisite": prereq,
            "prereq_mastery": int(round(prereq_mastery * 100)) if prereq else None,
            "predicted_mastery_pct": int(round(pred_mastery * 100)),
            "predicted_gap_probability": pred_gap_prob,
            "risk_level": risk_level,
            "badge_class": badge,
            "preventive_advice": preventive_advice,
            "is_already_mastered": is_already_mastered
        })

    return future_predictions
