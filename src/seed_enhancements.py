"""
Seeds initial comprehensive, verified educational YouTube video resources
across Python, OOP, SQL, Data Structures, Machine Learning, and Mathematics topics,
plus initial sample assessments with objective and subjective questions for testing.
"""
import sqlite3
import re
from pathlib import Path

DB_PATH = Path("database/learning_gap.db")

def extract_yt_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else ""

SAMPLE_YOUTUBE_RESOURCES = [
    {
        "title": "Python for Beginners - Full Course (Variables, Loops, Data Structures)",
        "youtube_url": "https://www.youtube.com/watch?v=rfscVS0vtbw",
        "subject": "Programming",
        "topic": "Python Basics",
        "description": "Essential Python concepts including control flow, functions, dictionaries, and list slicing.",
        "difficulty_level": "Beginner",
        "learning_objective": "Master foundational Python syntax, mutable vs immutable structures, and functional loops.",
        "assigned_to_student_id": None
    },
    {
        "title": "Object Oriented Programming (OOP) in Python - Full Course",
        "youtube_url": "https://www.youtube.com/watch?v=Ej_02ICOIgs",
        "subject": "Programming",
        "topic": "OOP",
        "description": "Comprehensive classes, inheritance, dunder methods, encapsulation, and classmethods.",
        "difficulty_level": "Intermediate",
        "learning_objective": "Understand object composition, inheritance hierarchy, and polymorphism in Python.",
        "assigned_to_student_id": None
    },
    {
        "title": "Data Structures & Algorithms in Python - Full Tutorial",
        "youtube_url": "https://www.youtube.com/watch?v=pkYVOmU3MgA",
        "subject": "Computer Science",
        "topic": "Data Structures",
        "description": "Linked lists, binary search trees, stacks, queues, hash tables, and algorithm complexity.",
        "difficulty_level": "Intermediate",
        "learning_objective": "Analyze Big-O runtime, traverse data structures, and implement recursive searches.",
        "assigned_to_student_id": None
    },
    {
        "title": "SQL Tutorial - Full Database Course for Beginners",
        "youtube_url": "https://www.youtube.com/watch?v=HXV3zeQKqGY",
        "subject": "Database Systems",
        "topic": "SQL",
        "description": "Relational schema design, queries, JOIN operations, GROUP BY, aggregations, and subqueries.",
        "difficulty_level": "Beginner",
        "learning_objective": "Write clean multi-table joins, aggregated queries, and understand database constraints.",
        "assigned_to_student_id": None
    },
    {
        "title": "Machine Learning for Everybody - Full Course",
        "youtube_url": "https://www.youtube.com/watch?v=i_LwzRVP7bg",
        "subject": "Machine Learning",
        "topic": "Machine Learning",
        "description": "Supervised learning, classification, regression, model evaluation metrics, and overfitting.",
        "difficulty_level": "Intermediate",
        "learning_objective": "Understand loss functions, cross-validation, precision, recall, and decision boundaries.",
        "assigned_to_student_id": None
    },
    {
        "title": "Random Forest Algorithm Explained with Intuition",
        "youtube_url": "https://www.youtube.com/watch?v=v6VJ2RO66Ag",
        "subject": "Machine Learning",
        "topic": "Random Forest",
        "description": "Bagging, bootstrapping, decision trees ensemble, out-of-bag error, and feature importance.",
        "difficulty_level": "Advanced",
        "learning_objective": "Grasp how ensemble methods reduce variance and construct randomized decision boundaries.",
        "assigned_to_student_id": None
    },
    {
        "title": "K-Means Clustering Algorithm - Step-by-Step Explanation",
        "youtube_url": "https://www.youtube.com/watch?v=4b5d3muPQmA",
        "subject": "Unsupervised Learning",
        "topic": "K-Means",
        "description": "Centroid initialization, Euclidean metric, WCSS convergence, and the Elbow method heuristic.",
        "difficulty_level": "Intermediate",
        "learning_objective": "Implement cluster convergence and evaluate cohesion via silhouette metrics.",
        "assigned_to_student_id": None
    },
    {
        "title": "Principal Component Analysis (PCA) Step-by-Step",
        "youtube_url": "https://www.youtube.com/watch?v=FgakZw6K1QQ",
        "subject": "Linear Algebra & ML",
        "topic": "PCA",
        "description": "Eigenvectors, eigenvalues, covariance matrix decomposition, and dimensionality projection.",
        "difficulty_level": "Advanced",
        "learning_objective": "Calculate variance retention across orthogonal components for high-dimensional compression.",
        "assigned_to_student_id": None
    }
]

SAMPLE_ASSESSMENTS = [
    {
        "title": "Comprehensive Mid-Term Examination: Python & Applied Machine Learning",
        "description": "Proctored academic assessment evaluating foundational programming concepts, algorithmic reasoning, and machine learning model validation.",
        "subject": "Computer Science & AI",
        "topic": "Python Basics",
        "duration_minutes": 25,
        "passing_marks": 50.0,
        "total_marks": 100.0,
        "negative_marking": 1.0,
        "attempt_limit": 2,
        "shuffle_questions": 1,
        "shuffle_options": 1,
        "is_proctored": 1,
        "proctoring_strictness": "Standard",
        "questions": [
            {
                "question_text": "In Python, which of the following data structures is immutable?",
                "question_type": "mcq",
                "option_a": "List",
                "option_b": "Tuple",
                "option_c": "Dictionary",
                "option_d": "Set",
                "correct_answer": "B",
                "marks": 15.0,
                "explanation": "Tuples in Python cannot have their elements modified after creation, guaranteeing immutability."
            },
            {
                "question_text": "Is the statement true or false: A Random Forest model trains multiple decision trees independently using bootstrap aggregation (bagging).",
                "question_type": "true_false",
                "option_a": "True",
                "option_b": "False",
                "option_c": "",
                "option_d": "",
                "correct_answer": "True",
                "marks": 15.0,
                "explanation": "Random Forest is an ensemble method built upon bagging bootstrap samples and random feature subsets."
            },
            {
                "question_text": "Which of the following techniques are commonly utilized to prevent overfitting in supervised machine learning models? (Select all that apply)",
                "question_type": "multiple_select",
                "option_a": "L1 / L2 Regularization",
                "option_b": "K-Fold Cross-Validation",
                "option_c": "Increasing training epochs infinitely",
                "option_d": "Pruning decision tree max_depth",
                "correct_answer": "A,B,D",
                "marks": 20.0,
                "explanation": "Regularization, cross-validation, and tree depth constraints directly combat high model variance."
            },
            {
                "question_text": "In K-Means clustering, what is the role of the Within-Cluster Sum of Squares (WCSS), and how is the Elbow Method used to choose the optimal value of K?",
                "question_type": "subjective",
                "option_a": "",
                "option_b": "",
                "option_c": "",
                "option_d": "",
                "correct_answer": "WCSS measures compactness; Elbow method identifies diminishing returns point where WCSS reduction flattens.",
                "marks": 25.0,
                "explanation": "Subjective question evaluated by Admin based on explanation of intra-cluster distance and curvature heuristic."
            },
            {
                "question_text": "Explain the architectural difference between method overriding and method overloading in object-oriented Python.",
                "question_type": "subjective",
                "option_a": "",
                "option_b": "",
                "option_c": "",
                "option_d": "",
                "correct_answer": "Overriding redefines parent class method in subclass; overloading handles varied signatures in same scope (emulated via default args/*args in Python).",
                "marks": 25.0,
                "explanation": "Subjective evaluation reviewing student comprehension of inheritance hierarchy and dynamic dispatch."
            }
        ]
    },
    {
        "title": "Diagnostic Assessment: Algorithms & Relational Databases",
        "description": "Standard diagnostic test evaluating student competency in SQL joins and basic algorithmic complexity.",
        "subject": "Data Engineering",
        "topic": "SQL",
        "duration_minutes": 20,
        "passing_marks": 40.0,
        "total_marks": 50.0,
        "negative_marking": 0.0,
        "attempt_limit": 3,
        "shuffle_questions": 0,
        "shuffle_options": 1,
        "is_proctored": 1,
        "proctoring_strictness": "Standard",
        "questions": [
            {
                "question_text": "Which SQL JOIN returns all rows from the left table, and the matched rows from the right table?",
                "question_type": "mcq",
                "option_a": "INNER JOIN",
                "option_b": "LEFT OUTER JOIN",
                "option_c": "RIGHT OUTER JOIN",
                "option_d": "FULL OUTER JOIN",
                "correct_answer": "B",
                "marks": 25.0,
                "explanation": "LEFT JOIN ensures every row from the left table appears, filling missing right table values with NULL."
            },
            {
                "question_text": "True or False: The time complexity of accessing an element in an array by index is O(1).",
                "question_type": "true_false",
                "option_a": "True",
                "option_b": "False",
                "option_c": "",
                "option_d": "",
                "correct_answer": "True",
                "marks": 25.0,
                "explanation": "Contiguous memory layout allows constant-time direct pointer arithmetic."
            }
        ]
    }
]

def seed_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Seed YouTube resources if empty
    cursor.execute("SELECT COUNT(*) FROM youtube_resources")
    yt_count = cursor.fetchone()[0]
    if yt_count == 0:
        for res in SAMPLE_YOUTUBE_RESOURCES:
            vid_id = extract_yt_id(res["youtube_url"])
            thumb = f"https://img.youtube.com/vi/{vid_id}/hqdefault.jpg" if vid_id else ""
            cursor.execute("""
            INSERT INTO youtube_resources (
                title, youtube_url, video_id, subject, topic, description,
                difficulty_level, learning_objective, thumbnail_url, assigned_to_student_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                res["title"], res["youtube_url"], vid_id, res["subject"], res["topic"],
                res["description"], res["difficulty_level"], res["learning_objective"],
                thumb, res["assigned_to_student_id"]
            ))
        print(f"Seeded {len(SAMPLE_YOUTUBE_RESOURCES)} YouTube educational resources.")

    # Seed assessments if empty
    cursor.execute("SELECT COUNT(*) FROM assessments")
    assess_count = cursor.fetchone()[0]
    if assess_count == 0:
        for assess in SAMPLE_ASSESSMENTS:
            cursor.execute("""
            INSERT INTO assessments (
                title, description, subject, topic, duration_minutes, passing_marks,
                total_marks, negative_marking, attempt_limit, shuffle_questions,
                shuffle_options, is_proctored, proctoring_strictness
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                assess["title"], assess["description"], assess["subject"], assess["topic"],
                assess["duration_minutes"], assess["passing_marks"], assess["total_marks"],
                assess["negative_marking"], assess["attempt_limit"], assess["shuffle_questions"],
                assess["shuffle_options"], assess["is_proctored"], assess["proctoring_strictness"]
            ))
            assessment_id = cursor.lastrowid
            for q in assess["questions"]:
                cursor.execute("""
                INSERT INTO assessment_questions (
                    assessment_id, question_text, question_type, option_a, option_b,
                    option_c, option_d, correct_answer, marks, explanation
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    assessment_id, q["question_text"], q["question_type"], q["option_a"],
                    q["option_b"], q["option_c"], q["option_d"], q["correct_answer"],
                    q["marks"], q["explanation"]
                ))
        print(f"Seeded {len(SAMPLE_ASSESSMENTS)} initial assessments with questions.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    seed_data()
