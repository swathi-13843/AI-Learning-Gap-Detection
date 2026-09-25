import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash

DATABASE = Path("database/learning_gap.db")

def upgrade_and_seed():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # 1. Upgrade students table if columns are missing
    cursor.execute("PRAGMA table_info(students)")
    columns = [col[1] for col in cursor.fetchall()]

    new_cols = [
        ("name", "TEXT"),
        ("email", "TEXT"),
        ("department", "TEXT DEFAULT 'Computer Science & Engineering'"),
        ("enrollment_date", "TEXT DEFAULT '2025-08-01'")
    ]
    for col_name, col_type in new_cols:
        if col_name not in columns:
            cursor.execute(f"ALTER TABLE students ADD COLUMN {col_name} {col_type}")

    # Populate names for existing students
    first_names = ["Aarav", "Aditi", "Ananya", "Arjun", "Dev", "Diya", "Ishan", "Kavya", "Meera", "Neha", "Rohan", "Siddharth", "Swathi", "Varun", "Pooja", "Vikram", "Sneha", "Rahul", "Priya", "Nikhil"]
    last_names = ["Sharma", "Verma", "Patel", "Reddy", "Rao", "Nair", "Iyer", "Maloth", "Gupta", "Singh", "Joshi", "Bose", "Das", "Choudhury", "Mishra"]
    departments = ["Computer Science & Engineering", "Data Science & AI", "Information Technology", "Software Engineering"]

    cursor.execute("SELECT student_id FROM students")
    student_ids = [row[0] for row in cursor.fetchall()]

    for idx, sid in enumerate(student_ids):
        fn = first_names[idx % len(first_names)]
        ln = last_names[(idx * 3) % len(last_names)]
        dept = departments[idx % len(departments)]
        email = f"{fn.lower()}.{ln.lower()}{idx+1}@university.edu"
        full_name = f"{fn} {ln}"
        cursor.execute("""
            UPDATE students
            SET name = ?, email = ?, department = ?
            WHERE student_id = ?
        """, (full_name, email, dept, sid))

    # 2. Seed Users table (Admin & Students)
    admin_hash = generate_password_hash("admin123")
    student_hash = generate_password_hash("password123")

    # Add or update admin
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO users (username, email, password, role, student_id)
            VALUES (?, ?, ?, ?, ?)
        """, ("admin", "admin@edulearn.ai", admin_hash, "admin", None))

    # Ensure swathi (S001) and maloth (S002) have known passwords
    cursor.execute("""
        UPDATE users SET password = ?, role = 'student', student_id = 'S001' WHERE username = 'swathi'
    """, (student_hash,))
    cursor.execute("""
        UPDATE users SET password = ?, role = 'student', student_id = 'S002' WHERE username = 'maloth'
    """, (student_hash,))

    # Seed 12 Core Topics if missing
    topics_list = [
        ("Python Basics", "Python", "Syntax, data types, control flow, functions and modules."),
        ("OOP", "Python", "Classes, inheritance, encapsulation, polymorphism and design patterns."),
        ("SQL", "Database", "DDL, DML, aggregations, grouping, subqueries and transactions."),
        ("SQL Joins", "Database", "INNER, LEFT, RIGHT, FULL OUTER joins and query optimization."),
        ("Statistics", "Data Science", "Measures of central tendency, variance, distributions, hypothesis testing."),
        ("Probability", "Data Science", "Conditional probability, Bayes Theorem, random variables and expectation."),
        ("Regression", "Machine Learning", "Linear, polynomial, ridge and lasso regression algorithms."),
        ("Classification", "Machine Learning", "Logistic regression, SVM, KNN and classification metrics (ROC/AUC)."),
        ("Decision Trees", "Machine Learning", "Information gain, Gini impurity, tree pruning and entropy."),
        ("Random Forest", "Machine Learning", "Ensemble methods, bagging, bootstrap aggregation and feature importance."),
        ("K-Means", "Machine Learning", "Unsupervised clustering, centroids, inertia and elbow evaluation."),
        ("PCA", "Data Science", "Dimensionality reduction, eigenvectors, eigenvalues and variance explained.")
    ]
    for name, subj, desc in topics_list:
        cursor.execute("""
            INSERT OR IGNORE INTO topics (topic_name, subject, description)
            VALUES (?, ?, ?)
        """, (name, subj, desc))

    # 3. Seed Quizzes & Questions
    cursor.execute("SELECT id, topic_name FROM topics")
    topic_map = {row[1]: row[0] for row in cursor.fetchall()}

    quizzes_data = [
        {
            "topic": "Python Basics",
            "title": "Python Fundamentals Assessment",
            "description": "Evaluate basic syntax, list comprehensions, mutability, and dictionary operations.",
            "duration": 15,
            "questions": [
                ("What is the output of bool([]) in Python?", "True", "False", "None", "Error", "B"),
                ("Which data structure is immutable in Python?", "List", "Dictionary", "Tuple", "Set", "C"),
                ("What does the 'is' operator evaluate?", "Value equality", "Memory identity", "Type equivalence", "Length equality", "B"),
                ("Which keyword is used to create a generator in Python?", "generate", "return", "yield", "async", "C"),
                ("What is the time complexity of dictionary lookup on average in Python?", "O(n)", "O(log n)", "O(1)", "O(n^2)", "C")
            ]
        },
        {
            "topic": "OOP",
            "title": "Object-Oriented Architecture Quiz",
            "description": "Test understanding of encapsulation, inheritance, polymorphism, and class decorators.",
            "duration": 15,
            "questions": [
                ("Which method is called automatically during object initialization?", "__new__", "__init__", "__str__", "__call__", "B"),
                ("What mechanism in Python provides method resolution order?", "MRO (C3 Linearization)", "FIFO", "LIFO", "Depth-First Search", "A"),
                ("Which decorator prevents a method from modifying class or instance state?", "@classmethod", "@property", "@staticmethod", "@abstractmethod", "C"),
                ("In OOP, wrapping data and methods into a single unit is known as:", "Polymorphism", "Abstraction", "Encapsulation", "Inheritance", "C"),
                ("What does the super() function do?", "Calls the parent class constructor/method", "Creates a superuser instance", "Overrides all methods", "Restarts the runtime", "A")
            ]
        },
        {
            "topic": "SQL Joins",
            "title": "Relational Joins & Subqueries Exam",
            "description": "Evaluate proficiency in multi-table queries, join mechanics, and aggregation filters.",
            "duration": 20,
            "questions": [
                ("Which JOIN returns all rows from the left table and matched rows from the right table?", "INNER JOIN", "RIGHT JOIN", "LEFT JOIN", "CROSS JOIN", "C"),
                ("What clause is used to filter aggregated data in SQL?", "WHERE", "HAVING", "GROUP BY", "ORDER BY", "B"),
                ("What is the result of a CROSS JOIN between a table with 5 rows and a table with 4 rows?", "9 rows", "1 row", "20 rows", "0 rows", "C"),
                ("Which constraint uniquely identifies each record in a database table?", "FOREIGN KEY", "UNIQUE", "CHECK", "PRIMARY KEY", "D"),
                ("What does the SQL COALESCE function return?", "The maximum non-null value", "The first non-null expression in the list", "The row count", "Null", "B")
            ]
        },
        {
            "topic": "Regression",
            "title": "Supervised Learning: Regression Analysis",
            "description": "Assess knowledge of loss functions, regularization (L1/L2), and model evaluation metrics.",
            "duration": 15,
            "questions": [
                ("Which regularization technique adds absolute magnitude of coefficient penalties (L1)?", "Ridge", "Lasso", "Elastic Net", "Dropout", "B"),
                ("What does R-squared measure in linear regression?", "Root Mean Squared Error", "Proportion of variance explained by model", "Residual variance only", "Classification accuracy", "B"),
                ("Which metric is most sensitive to large outlier errors?", "MAE (Mean Absolute Error)", "MSE (Mean Squared Error)", "MAPE", "Median Error", "B"),
                ("What happens when multicollinearity is present among regression predictors?", "Coefficients become unstable and variance inflates", "Accuracy is guaranteed to be 100%", "Residuals become zero", "R-squared drops to zero", "A"),
                ("Gradient Descent uses which mathematical construct to update model weights?", "Hessian matrix", "Negative Gradient of the Loss Function", "Eigenvalues", "Determinant", "B")
            ]
        },
        {
            "topic": "Random Forest",
            "title": "Ensemble Methods & Random Forests",
            "description": "Understand bagging, out-of-bag error, hyperparameter tuning, and feature importances.",
            "duration": 15,
            "questions": [
                ("Random Forest builds multiple decision trees using which ensemble technique?", "Boosting", "Bagging (Bootstrap Aggregating)", "Stacking", "Cascading", "B"),
                ("What feature subset selection method is used at each split in Random Forest?", "Random feature sub-sampling", "All available features", "Only top correlated feature", "Principal components only", "A"),
                ("What does 'Out-Of-Bag' (OOB) score approximate?", "Training error", "Generalization / Validation error", "Tree depth", "Leaf purity", "B"),
                ("Increasing the number of trees (n_estimators) in Random Forest typically:", "Causes severe overfitting", "Reduces variance without increasing bias", "Increases bias exponentially", "Reduces tree diversity to zero", "B"),
                ("How is feature importance typically calculated in Random Forest?", "Mean Decrease in Impurity (Gini/MSE)", "Tree depth count", "Alphabetical order", "Dataset row count", "A")
            ]
        },
        {
            "topic": "K-Means",
            "title": "Unsupervised Clustering & K-Means",
            "description": "Assess knowledge of distance metrics, centroid initialization, and cluster evaluation.",
            "duration": 15,
            "questions": [
                ("How does the standard K-Means algorithm determine cluster assignments?", "Minimum Euclidean distance to centroid", "Cosine similarity only", "Random assignment", "Density estimation", "A"),
                ("Which heuristic method is commonly used to choose the optimal number of clusters K?", "Silhouette method and Elbow method", "Gradient Descent", "Confusion Matrix", "ROC Curve", "A"),
                ("What is a primary limitation of standard K-Means?", "Sensitivity to initial centroid placement and non-spherical clusters", "Cannot work on numbers", "Only works for 2 clusters", "Guaranteed global optimum", "A"),
                ("What does the K-Means++ initialization algorithm solve?", "Spreads out initial centroids to avoid poor local minima", "Removes outlier data points automatically", "Forces clusters to have equal sample counts", "Normalizes feature scales", "A"),
                ("Inertia in K-Means represents:", "Sum of squared distances of samples to their closest cluster center", "Number of iterations", "Average feature variance", "Model training latency", "A")
            ]
        }
    ]

    for qz in quizzes_data:
        t_id = topic_map.get(qz["topic"])
        if not t_id:
            continue
        cursor.execute("SELECT id FROM quizzes WHERE title = ?", (qz["title"],))
        existing_q = cursor.fetchone()
        if not existing_q:
            cursor.execute("""
                INSERT INTO quizzes (topic_id, title, description, total_questions, duration, due_date)
                VALUES (?, ?, ?, ?, ?, '2026-10-15')
            """, (t_id, qz["title"], qz["description"], len(qz["questions"]), qz["duration"]))
            quiz_id = cursor.lastrowid
        else:
            quiz_id = existing_q[0]

        for q_text, op_a, op_b, op_c, op_d, ans in qz["questions"]:
            cursor.execute("SELECT id FROM questions WHERE quiz_id = ? AND question = ?", (quiz_id, q_text))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO questions (quiz_id, question, option_a, option_b, option_c, option_d, correct_answer)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (quiz_id, q_text, op_a, op_b, op_c, op_d, ans))

    # 4. Seed Assignments
    assignments_data = [
        ("Python Basics", "Mini Project: Command Line Task Engine", "Build an automated task scheduling CLI tool using object-oriented Python, file persistence, and robust exception handling.", 100, "2026-10-10"),
        ("SQL Joins", "Enterprise Database Optimization Case Study", "Write complex multi-table joins, subqueries, and window functions to compute customer retention cohorts.", 100, "2026-10-18"),
        ("Regression", "Predictive House Pricing Model", "Preprocess housing features, eliminate multicollinearity, train Ridge/Lasso models, and report R2 and RMSE metrics.", 100, "2026-10-25"),
        ("Random Forest", "Customer Churn Classifier Implementation", "Train a tuned Random Forest model on tabular telemetry data, plot confusion matrix, and analyze SHAP values.", 100, "2026-11-05")
    ]
    for topic_name, title, desc, max_sc, due in assignments_data:
        t_id = topic_map.get(topic_name)
        if t_id:
            cursor.execute("SELECT id FROM assignments WHERE title = ?", (title,))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO assignments (topic_id, title, description, max_score, due_date)
                    VALUES (?, ?, ?, ?, ?)
                """, (t_id, title, desc, max_sc, due))

    # 5. Seed Interventions for High Risk Students
    cursor.execute("SELECT student_id, average_learning_gap FROM students WHERE overall_risk = 'High Risk' LIMIT 15")
    high_risk_students = cursor.fetchall()
    for sid, gap in high_risk_students:
        cursor.execute("SELECT id FROM interventions WHERE student_id = ?", (sid,))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO interventions (student_id, intervention_type, description, status)
                VALUES (?, '1-on-1 Mentorship', ?, 'In Progress')
            """, (sid, f"Assigned personalized peer tutor and remedial lab exercises due to high learning gap ({round(gap, 1)}%)."))

    # 6. Seed student_topics records for S001 and S002 if empty
    cursor.execute("SELECT COUNT(*) FROM student_topics WHERE student_id = 'S001'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("SELECT topic, learning_gap_score, gap_category, priority FROM learning_gaps WHERE student_id = 'S001'")
        gaps_s001 = cursor.fetchall()
        for t_name, gap_sc, cat, prio in gaps_s001:
            t_id = topic_map.get(t_name)
            if t_id:
                score = round(max(0.0, 100.0 - gap_sc), 2)
                cursor.execute("""
                    INSERT INTO student_topics (student_id, topic_id, score, learning_gap_score, gap_category, priority)
                    VALUES ('S001', ?, ?, ?, ?, ?)
                """, (t_id, score, gap_sc, cat, prio))

    connection.commit()
    connection.close()
    print("Database upgrade and seeding completed successfully!")

if __name__ == "__main__":
    upgrade_and_seed()
