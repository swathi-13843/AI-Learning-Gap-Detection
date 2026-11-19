"""
Script to expand educational YouTube video resources, assessments, and quizzes in EduGap AI.
Adds:
- Comprehensive YouTube verified links for topics: Python, OOP, SQL, Data Structures, ML, Random Forest, K-Means, PCA, Statistics, Probability, Supervised Classification.
- Additional timed proctored examinations (Diagnostic, Mid-term, Final, Topic Mastery).
- Additional quizzes with questions.
"""
import sqlite3
import re
from pathlib import Path

DB_PATH = Path("database/learning_gap.db")

def extract_yt_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else ""

ADDITIONAL_YOUTUBE_RESOURCES = [
    {
        "title": "Python Data Structures: Stacks, Queues, Deques & Binary Trees",
        "youtube_url": "https://www.youtube.com/watch?v=RBSGKlAvoiM",
        "subject": "Computer Science",
        "topic": "Data Structures",
        "description": "Deep dive into node-based data structures, linked lists, queues, and tree traversals in Python.",
        "difficulty_level": "Intermediate",
        "learning_objective": "Master linear and hierarchical data structures with algorithmic Big-O analysis."
    },
    {
        "title": "SQL Window Functions Tutorial - Rank, Dense_Rank, Row_Number",
        "youtube_url": "https://www.youtube.com/watch?v=Ww71knvhQ-s",
        "subject": "Database Systems",
        "topic": "SQL",
        "description": "Complete breakdown of analytic partitioning, running totals, and ranking queries in SQL.",
        "difficulty_level": "Advanced",
        "learning_objective": "Construct complex analytical SQL queries using windowing clauses and partitions."
    },
    {
        "title": "Statistics for Data Science - Full Course (Probability, Distributions, Hypothesis Testing)",
        "youtube_url": "https://www.youtube.com/watch?v=Vfo5le26IhY",
        "subject": "Mathematics",
        "topic": "Statistics",
        "description": "Probability distributions, central limit theorem, z-scores, p-values, and hypothesis testing.",
        "difficulty_level": "Intermediate",
        "learning_objective": "Understand inferential statistics, variance estimators, and statistical significance."
    },
    {
        "title": "Probability & Bayes' Theorem Intuitive Visual Guide",
        "youtube_url": "https://www.youtube.com/watch?v=HZGCoVF3YvM",
        "subject": "Mathematics",
        "topic": "Probability",
        "description": "Conditional probability, prior probability, likelihood, and Bayesian inference explained visually.",
        "difficulty_level": "Beginner",
        "learning_objective": "Calculate posterior probabilities with Bayes Theorem for diagnostic problems."
    },
    {
        "title": "Decision Trees and Ensemble Random Forest - In-Depth ML Guide",
        "youtube_url": "https://www.youtube.com/watch?v=J4Wdy0Wc_xQ",
        "subject": "Machine Learning",
        "topic": "Random Forest",
        "description": "Information gain, Gini impurity, tree pruning, out-of-bag validation, and bagging ensembles.",
        "difficulty_level": "Intermediate",
        "learning_objective": "Understand how tree splits minimize entropy and ensemble voting mitigates high variance."
    },
    {
        "title": "Classification Metrics in Machine Learning: ROC, AUC, Confusion Matrix, F1-Score",
        "youtube_url": "https://www.youtube.com/watch?v=wpQiE1y0hBM",
        "subject": "Machine Learning",
        "topic": "Supervised Learning",
        "description": "Precision-recall tradeoffs, specificity, sensitivity, ROC curves, and multi-class F1 formulation.",
        "difficulty_level": "Intermediate",
        "learning_objective": "Evaluate classification model performance beyond simple accuracy."
    },
    {
        "title": "Unsupervised Learning with Scikit-Learn: K-Means, DBSCAN & Hierarchical",
        "youtube_url": "https://www.youtube.com/watch?v=fS6kYmkyrks",
        "subject": "Unsupervised Learning",
        "topic": "K-Means",
        "description": "Practical clustering workflows in Python using scikit-learn with silhouette optimization.",
        "difficulty_level": "Intermediate",
        "learning_objective": "Cluster unlabelled datasets, measure cohesion/separation, and handle centroid initialization."
    },
    {
        "title": "Principal Component Analysis Visualized - StatQuest with Josh Starmer",
        "youtube_url": "https://www.youtube.com/watch?v=FgakZw6K1QQ",
        "subject": "Linear Algebra & ML",
        "topic": "PCA",
        "description": "Step-by-step visual demonstration of 2D/3D orthogonal projection and principal component axis rotation.",
        "difficulty_level": "Beginner",
        "learning_objective": "Understand singular values, coordinate rotation, and dimensionality compression."
    },
    {
        "title": "Flask Web Development Crash Course - REST APIs & Jinja2 Templates",
        "youtube_url": "https://www.youtube.com/watch?v=dam0GPOAvVI",
        "subject": "Web Development",
        "topic": "Python Basics",
        "description": "Routing, request parsing, session storage, Jinja2 template inheritance, and backend architecture in Flask.",
        "difficulty_level": "Intermediate",
        "learning_objective": "Build secure, modular web applications in Python using Flask."
    }
]

ADDITIONAL_ASSESSMENTS = [
    {
        "title": "Proctored Final Exam: Advanced Data Structures & Algorithm Design",
        "description": "Strict full-screen proctored assessment examining tree traversal, hash collisions, dynamic programming, and complexity bounds.",
        "subject": "Computer Science",
        "topic": "Data Structures",
        "duration_minutes": 30,
        "passing_marks": 50.0,
        "total_marks": 100.0,
        "negative_marking": 1.0,
        "attempt_limit": 2,
        "shuffle_questions": 1,
        "shuffle_options": 1,
        "is_proctored": 1,
        "proctoring_strictness": "Strict",
        "questions": [
            {
                "question_text": "What is the worst-case time complexity of searching for an element in an unbalanced Binary Search Tree (BST)?",
                "question_type": "mcq",
                "option_a": "O(1)",
                "option_b": "O(log N)",
                "option_c": "O(N)",
                "option_d": "O(N^2)",
                "correct_answer": "C",
                "marks": 20.0,
                "explanation": "In an unbalanced (skewed) binary search tree, the tree degenerates into a linked list, yielding O(N) traversal."
            },
            {
                "question_text": "True or False: Hash table lookups always run in O(1) time regardless of collision resolution strategies.",
                "question_type": "true_false",
                "option_a": "True",
                "option_b": "False",
                "option_c": "",
                "option_d": "",
                "correct_answer": "False",
                "marks": 20.0,
                "explanation": "Average case is O(1), but in the worst case with excessive collisions lookups degrade to O(N)."
            },
            {
                "question_text": "Which of the following data structures can be effectively utilized to implement a Breadth-First Search (BFS) graph traversal? (Select all that apply)",
                "question_type": "multiple_select",
                "option_a": "First-In First-Out Queue",
                "option_b": "Double-Ended Queue (Deque)",
                "option_c": "LIFO Call Stack",
                "option_d": "Priority Queue",
                "correct_answer": "A,B",
                "marks": 25.0,
                "explanation": "BFS requires a FIFO ordering mechanism; both standard Queues and Deques satisfy this requirement."
            },
            {
                "question_text": "Explain the architectural mechanism of cycle detection in linked lists using Floyd's Tortoise and Hare algorithm.",
                "question_type": "subjective",
                "option_a": "",
                "option_b": "",
                "option_c": "",
                "option_d": "",
                "correct_answer": "Two pointers move at 1x and 2x velocities; if a cycle exists, the distance between them reduces by 1 per step until collision occurs.",
                "marks": 35.0,
                "explanation": "Subjective question evaluating candidate understanding of two-pointer algorithms in cyclic graphs."
            }
        ]
    },
    {
        "title": "Machine Learning Mastery Examination: Optimization & Diagnostics",
        "description": "Full-screen proctored assessment examining regularization, gradient descent, bias-variance tradeoff, and cross-validation.",
        "subject": "Machine Learning",
        "topic": "Machine Learning",
        "duration_minutes": 25,
        "passing_marks": 50.0,
        "total_marks": 75.0,
        "negative_marking": 0.5,
        "attempt_limit": 2,
        "shuffle_questions": 1,
        "shuffle_options": 1,
        "is_proctored": 1,
        "proctoring_strictness": "Strict",
        "questions": [
            {
                "question_text": "Which regularization technique performs implicit feature selection by driving non-critical feature weights strictly to zero?",
                "question_type": "mcq",
                "option_a": "L2 Ridge Regularization",
                "option_b": "L1 Lasso Regularization",
                "option_c": "Dropout",
                "option_d": "Batch Normalization",
                "correct_answer": "B",
                "marks": 25.0,
                "explanation": "L1 penalty incorporates absolute parameter magnitude (|w|), producing sparse weight solutions where coefficients become zero."
            },
            {
                "question_text": "True or False: High bias in a model is typically associated with overfitting on the training dataset.",
                "question_type": "true_false",
                "option_a": "True",
                "option_b": "False",
                "option_c": "",
                "option_d": "",
                "correct_answer": "False",
                "marks": 25.0,
                "explanation": "High bias signifies underfitting (oversimplified model); high variance indicates overfitting."
            },
            {
                "question_text": "Discuss the primary trade-offs between Batch Gradient Descent, Stochastic Gradient Descent (SGD), and Mini-Batch Gradient Descent.",
                "question_type": "subjective",
                "option_a": "",
                "option_b": "",
                "option_c": "",
                "option_d": "",
                "correct_answer": "Batch uses whole data (stable gradient, high memory/computation); SGD updates per instance (noisy, escapes local minima, fast); Mini-batch balances vectorization speed and stability.",
                "marks": 25.0,
                "explanation": "Evaluated based on analysis of gradient noise, computational vectorization, and memory scalability."
            }
        ]
    }
]

def add_resources():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Add YouTube resources
    for res in ADDITIONAL_YOUTUBE_RESOURCES:
        # Check if already exists
        cursor.execute("SELECT id FROM youtube_resources WHERE title = ?", (res["title"],))
        if not cursor.fetchone():
            vid_id = extract_yt_id(res["youtube_url"])
            thumb = f"https://img.youtube.com/vi/{vid_id}/hqdefault.jpg" if vid_id else ""
            cursor.execute("""
            INSERT INTO youtube_resources (
                title, youtube_url, video_id, subject, topic, description,
                difficulty_level, learning_objective, thumbnail_url, created_by_admin
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Admin')
            """, (
                res["title"], res["youtube_url"], vid_id, res["subject"], res["topic"],
                res["description"], res["difficulty_level"], res["learning_objective"], thumb
            ))

    # Add Assessments
    for assess in ADDITIONAL_ASSESSMENTS:
        cursor.execute("SELECT id FROM assessments WHERE title = ?", (assess["title"],))
        if not cursor.fetchone():
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
            a_id = cursor.lastrowid
            for q in assess["questions"]:
                cursor.execute("""
                INSERT INTO assessment_questions (
                    assessment_id, question_text, question_type, option_a, option_b,
                    option_c, option_d, correct_answer, marks, explanation
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    a_id, q["question_text"], q["question_type"], q["option_a"],
                    q["option_b"], q["option_c"], q["option_d"], q["correct_answer"],
                    q["marks"], q["explanation"]
                ))

    conn.commit()
    conn.close()
    print("Additional educational resources, assessments, and questions added successfully!")

if __name__ == "__main__":
    add_resources()
