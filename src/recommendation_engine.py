"""
Personalized Recommendation Engine for EduGap AI.
Generates multi-tiered actionable learning interventions based on detected topic learning gaps:
1. YouTube Video Lectures (targeted matching from database)
2. Curriculum Roadmap Subtopics & Revision Directives
3. Interactive Practice Assessments
4. Mentor Tutoring / Intervention Escalations for High Priority gaps
"""

import sys
import sqlite3
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pandas as pd
from src.curriculum_data import CURRICULUM_ROADMAP

DATABASE_PATH = ROOT_DIR / "database" / "learning_gap.db"


def get_db_connection():
    if not DATABASE_PATH.exists():
        return None
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_youtube_videos_for_topic(topic_name, limit=3):
    """
    Fetches matching YouTube resources from SQLite database.
    """
    conn = get_db_connection()
    if conn is None:
        return []

    try:
        # Search by exact topic, partial match, or subject
        rows = conn.execute("""
            SELECT id, title, youtube_url, video_id, topic, description, difficulty_level, thumbnail_url
            FROM youtube_resources
            WHERE LOWER(topic) = LOWER(?) OR LOWER(topic) LIKE LOWER(?)
            ORDER BY id DESC LIMIT ?
        """, (topic_name, f"%{topic_name}%", limit)).fetchall()

        if not rows:
            # Fallback to general programming / DS / ML resources
            rows = conn.execute("""
                SELECT id, title, youtube_url, video_id, topic, description, difficulty_level, thumbnail_url
                FROM youtube_resources
                ORDER BY id DESC LIMIT ?
            """, (limit,)).fetchall()

        return [dict(r) for r in rows]
    except Exception as e:
        print(f"[Recommendation Engine] Error fetching videos: {e}")
        return []
    finally:
        conn.close()


def get_curriculum_revision_points(topic_name, gap_category="Medium Gap", max_items=4):
    """
    Pulls targeted subtopics and revision items from CURRICULUM_ROADMAP.
    """
    topic_data = CURRICULUM_ROADMAP.get(topic_name)
    if not topic_data or "levels" not in topic_data:
        return [
            f"Review foundational principles and syntax of {topic_name}.",
            f"Solve beginner-level coding drills on {topic_name}.",
            f"Complete practical implementation exercises for {topic_name}."
        ]

    levels = topic_data.get("levels", {})
    if gap_category == "High Gap":
        # Pull from Beginner level
        items = levels.get("Beginner", [])[:max_items]
    elif gap_category == "Medium Gap":
        # Pull from Intermediate level
        items = levels.get("Intermediate", [])[:max_items]
    else:
        # Pull from Advanced or Practical
        items = levels.get("Advanced", levels.get("Practical Python", []))[:max_items]

    return items if items else [f"Review core principles of {topic_name}."]


def generate_personalized_topic_recommendation(
    student_id,
    topic_name,
    gap_category,
    bkt_mastery=0.5,
    quiz_score=50.0,
    overall_avg=75.0,
    is_hidden_gap=False
):
    """
    Generates structured, comprehensive personalized recommendation payload for student portal.
    """
    videos = get_youtube_videos_for_topic(topic_name, limit=2)
    revision_points = get_curriculum_revision_points(topic_name, gap_category, max_items=3)

    # Narrative explanation of WHY the gap was detected
    explanation_parts = []
    if is_hidden_gap:
        explanation_parts.append(
            f"Hidden Learning Gap Detected: Your overall cohort performance is strong ({overall_avg:.1f}%), "
            f"but your mastery in {topic_name} ({quiz_score:.1f}%) is significantly below your typical performance."
        )
    elif gap_category == "High Gap":
        explanation_parts.append(
            f"High Severity Learning Gap: Bayesian Knowledge Tracing estimated a critical mastery probability of "
            f"{bkt_mastery * 100:.1f}% with repeated assessment deficits in {topic_name}."
        )
    elif gap_category == "Medium Gap":
        explanation_parts.append(
            f"Moderate Learning Gap: Conceptual foundation in {topic_name} is developing but demonstrates inconsistencies "
            f"in recent quiz attempts (mastery: {bkt_mastery * 100:.1f}%)."
        )
    else:
        explanation_parts.append(
            f"Mastery Achieved: You have demonstrated strong competency in {topic_name} "
            f"with a high knowledge probability of {bkt_mastery * 100:.1f}%."
        )

    # Actionable guidance
    action_plan = []
    if gap_category in ["High Gap", "Medium Gap"] or is_hidden_gap:
        action_plan.append(f"Watch the recommended video lecture: '{videos[0]['title'] if videos else topic_name}'.")
        action_plan.append(f"Review core topics: {', '.join(revision_points[:2])}.")
        action_plan.append(f"Retake the {topic_name} diagnostic quiz to improve your knowledge mastery probability.")
        if gap_category == "High Gap":
            action_plan.append("Schedule a 1-on-1 tutoring review session with your assigned academic mentor.")
    else:
        action_plan.append(f"Explore advanced optimizations and applied projects in {topic_name}.")

    return {
        "student_id": student_id,
        "topic": topic_name,
        "gap_category": gap_category,
        "bkt_mastery_pct": round(bkt_mastery * 100.0, 1),
        "is_hidden_gap": is_hidden_gap,
        "diagnostic_explanation": " ".join(explanation_parts),
        "revision_points": revision_points,
        "recommended_videos": videos,
        "action_plan": action_plan
    }
