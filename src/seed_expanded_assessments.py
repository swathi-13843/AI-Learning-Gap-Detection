"""
Seeds expanded question bank and diverse assessments for EduGap AI.
Includes:
- Initial Diagnostic Assessment (10 questions)
- Topic-wise MCQ Tests (SQL Joins, Python OOP, PCA, K-Means)
- Mid-Term Examination Mock
- Semester Final Examination Mock
- Multiple question formats: MCQ, True/False, Multiple Select, Subjective
"""

import sqlite3
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "database" / "learning_gap.db"


def seed_assessments():
    print(f"Connecting to {DB_PATH} to seed expanded assessments...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Ensure Assessment 7 has full 10 questions with proper options
    cursor.execute("SELECT id FROM assessments WHERE title LIKE '%Diagnostic Assessment%'")
    diag = cursor.fetchone()
    if diag:
        diag_id = diag[0]
        # Clean existing questions for this assessment to avoid duplicates
        cursor.execute("DELETE FROM assessment_questions WHERE assessment_id = ?", (diag_id,))

        diag_questions = [
            (diag_id, "In Python, which built-in data structure is immutable and cannot be modified post-instantiation?", "mcq", "List", "Tuple", "Dictionary", "Set", "B", 5.0, "Tuples are immutable sequences; once instantiated, their elements cannot be appended, removed, or reassigned."),
            (diag_id, "What is the time complexity of searching for a value in an unsorted array of size N?", "mcq", "O(1)", "O(log N)", "O(N)", "O(N^2)", "C", 5.0, "An unsorted array has no ordering guarantees, requiring a linear scan from index 0 to N-1 in the worst case."),
            (diag_id, "In relational database queries, which SQL clause is used to filter aggregated groups produced by GROUP BY?", "mcq", "WHERE", "HAVING", "ORDER BY", "FILTER", "B", 5.0, "WHERE filters rows before aggregation; HAVING filters grouped result sets after GROUP BY aggregation."),
            (diag_id, "What does an INNER JOIN between Table A and Table B return?", "mcq", "All rows from Table A only", "All rows from Table B only", "Only rows where the join condition matches in both tables", "The Cartesian product of all rows", "C", 5.0, "INNER JOIN returns exclusively the intersection of records where join keys match across both tables."),
            (diag_id, "True or False: In supervised learning, the training dataset consists of input feature vectors paired with known ground-truth target labels.", "true_false", "True", "False", "", "", "True", 5.0, "Supervised learning algorithms infer a function from labeled training data consisting of input-output pairs."),
            (diag_id, "Which evaluation metric is most appropriate for evaluating a classifier on a heavily imbalanced dataset where the positive class is rare (e.g. fraud detection or learning gaps)?", "mcq", "Raw Accuracy", "Precision-Recall F1-Score", "Mean Squared Error", "Adjusted R-Squared", "B", 5.0, "Accuracy can be deceptively high by predicting only the majority class. Precision, Recall, and Macro F1 assess minority class detection accurately."),
            (diag_id, "Which of the following are primary pillars of Object-Oriented Programming (OOP)? (Select all that apply)", "multiple_select", "Encapsulation", "Polymorphism", "Linear Scaling", "Inheritance", "A,B,D", 5.0, "The four classical pillars of OOP are Encapsulation, Abstraction, Inheritance, and Polymorphism."),
            (diag_id, "What is the primary function of the Update Gate in a Gated Recurrent Unit (GRU) neural network?", "mcq", "Determines how much historical memory to carry forward versus the candidate state", "Forces all weights to zero", "Performs batch normalization", "Replaces backward backpropagation", "A", 5.0, "The update gate z_t acts as a soft linear interpolation balancing historical state h_{t-1} with candidate state h_tilde."),
            (diag_id, "Explain the fundamental difference between overfitting and underfitting in predictive modeling.", "subjective", "", "", "", "", "Overfitting represents high variance and low bias where model memorizes noise; underfitting represents high bias where model fails to capture underlying patterns.", 5.0, "Overfitting fails on unseen test data despite low training error; underfitting produces high error on both training and test data."),
            (diag_id, "Describe the ACID properties in relational database management systems and why each is required for transactional integrity.", "subjective", "", "", "", "", "Atomicity (all-or-nothing), Consistency (state constraints maintained), Isolation (independent concurrent execution), Durability (committed changes persist).", 5.0, "ACID properties guarantee transactional reliability in relational database management engines.")
        ]

        for q in diag_questions:
            cursor.execute("""
                INSERT INTO assessment_questions (assessment_id, question_text, question_type, option_a, option_b, option_c, option_d, correct_answer, marks, explanation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, q)
        print("Successfully updated Diagnostic Assessment with 10 questions")

    # 2. Add Assessment 8: SQL Joins Topic-Wise Mastery Assessment
    cursor.execute("SELECT id FROM assessments WHERE title LIKE '%SQL Joins Topic-Wise Mastery%'")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO assessments (title, description, subject, topic, duration_minutes, passing_marks, total_marks, negative_marking, attempt_limit, shuffle_questions, shuffle_options, is_proctored, is_published)
            VALUES (
                'Topic-Wise Mastery: SQL Joins & Multi-Table Query Optimization',
                'Comprehensive concept and query execution test evaluating INNER, LEFT, RIGHT, FULL OUTER joins, nested loop joins, hash joins, and Cartesian products.',
                'Database Systems', 'SQL Joins', 30, 24, 60, 0.5, 3, 1, 1, 0, 1
            )
        """)
        a8_id = cursor.lastrowid
        print(f"Created Assessment 8 (ID {a8_id})")

        a8_questions = [
            (a8_id, "What is the result of a LEFT OUTER JOIN when a row in the left table has no matching foreign key in the right table?", "mcq", "The left row is omitted from the output", "The left row is returned with NULL in all right table columns", "An SQL runtime exception is thrown", "A Cartesian product is generated", "B", 6.0, "LEFT JOIN guarantees all left table rows are preserved; missing right table columns are populated with NULL values."),
            (a8_id, "Which join condition produces M * N rows when Table A has M rows and Table B has N rows?", "mcq", "NATURAL JOIN", "CROSS JOIN without ON clause", "INNER JOIN on Primary Key", "FULL OUTER JOIN with WHERE clause", "B", 6.0, "CROSS JOIN produces the Cartesian product, pairing every row of Table A with every row of Table B."),
            (a8_id, "What is the primary difference between a Hash Join and a Nested Loop Join?", "mcq", "Hash Join builds an in-memory hash table on the smaller relation; Nested Loop probes each row sequentially", "Hash Join can only be used on strings", "Nested Loop is always faster on large tables", "Hash Join requires sorted inputs", "A", 6.0, "Hash Join hashes the join key of the smaller table in O(M+N) time; Nested Loop probes rows with O(M*N) cost."),
            (a8_id, "True or False: A Self-Join is an operation where a table is joined with itself using table aliases to model hierarchical relationships.", "true_false", "True", "False", "", "", "True", 6.0, "Self-joins use table aliases (e.g. Employee e JOIN Employee m ON e.manager_id = m.id) to traverse parent-child hierarchies."),
            (a8_id, "Which query correctly retrieves all students who have NEVER submitted any assessment?", "mcq", "SELECT * FROM students s INNER JOIN attempts a ON s.id = a.student_id", "SELECT * FROM students s LEFT JOIN attempts a ON s.id = a.student_id WHERE a.id IS NULL", "SELECT * FROM students s RIGHT JOIN attempts a ON s.id = a.student_id", "SELECT * FROM students s CROSS JOIN attempts a", "B", 6.0, "LEFT JOIN with a 'WHERE right_table.key IS NULL' clause is the standard pattern for finding non-matching anti-join records."),
            (a8_id, "Which of the following join algorithms require the input relations to be sorted on the join key beforehand?", "mcq", "Nested Loop Join", "Block Nested Loop Join", "Sort-Merge Join", "Grace Hash Join", "C", 6.0, "Sort-Merge Join requires both input relations to be ordered by join key, achieving O(M+N) merge time if pre-sorted."),
            (a8_id, "In SQL, what is the consequence of joining on a non-indexed column in a high-volume production table?", "mcq", "The query optimizer forces a Full Table Scan on the unindexed relation causing severe I/O degradation", "The database automatically aborts the query", "The query runs in constant O(1) time", "Data becomes corrupt", "A", 6.0, "Lacking an index, the database engine must scan every page of the table sequentially, increasing execution latency drastically."),
            (a8_id, "Which of the following are valid SQL Join types supported by ANSI SQL standards? (Select all that apply)", "multiple_select", "INNER JOIN", "LEFT OUTER JOIN", "CROSS JOIN", "DIAGONAL JOIN", "A,B,C", 6.0, "ANSI SQL recognizes INNER, LEFT OUTER, RIGHT OUTER, FULL OUTER, and CROSS joins. DIAGONAL JOIN does not exist."),
            (a8_id, "Explain why an unindexed multi-table JOIN can cause memory exhaustion in an RDBMS query engine.", "subjective", "", "", "", "", "Without indexes, the optimizer may spill hash tables or temporary sort buffers to disk or allocate excessive memory buffers, leading to memory pressure and query throttling.", 6.0, "Unindexed joins force expensive hash joins or full-scan nested loops that overwhelm buffer pools."),
            (a8_id, "Write a standard SQL query joining 'students' and 'learning_gaps' to identify all students with a gap score greater than 50 in 'SQL Joins'.", "subjective", "", "", "", "", "SELECT s.student_id, s.name, lg.learning_gap_score FROM students s JOIN learning_gaps lg ON s.student_id = lg.student_id WHERE lg.topic = 'SQL Joins' AND lg.learning_gap_score > 50;", 6.0, "Standard equijoin with WHERE filter on topic name and numerical threshold.")
        ]
        for q in a8_questions:
            cursor.execute("""
                INSERT INTO assessment_questions (assessment_id, question_text, question_type, option_a, option_b, option_c, option_d, correct_answer, marks, explanation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, q)

    # 3. Add Assessment 9: Mid-Term Examination Mock (Data Science & Statistics)
    cursor.execute("SELECT id FROM assessments WHERE title LIKE '%Mid-Term Examination Mock%'")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO assessments (title, description, subject, topic, duration_minutes, passing_marks, total_marks, negative_marking, attempt_limit, shuffle_questions, shuffle_options, is_proctored, is_published)
            VALUES (
                'Mid-Term Examination Mock: Data Science & Inferential Statistics',
                'Curriculum benchmark covering descriptive statistics, Central Limit Theorem, hypothesis testing, probability distributions, and Z-score transformations.',
                'Data Science & Mathematics', 'Statistics', 35, 20, 50, 0.25, 2, 1, 1, 0, 1
            )
        """)
        a9_id = cursor.lastrowid
        print(f"Created Assessment 9 (ID {a9_id})")

        a9_questions = [
            (a9_id, "What does the Central Limit Theorem state regarding the distribution of sample means from non-normal populations?", "mcq", "The sample mean distribution becomes uniform", "The sample mean distribution approaches a Normal Distribution as sample size N increases (N >= 30)", "The variance increases exponentially", "The mean becomes zero", "B", 5.0, "CLT guarantees that sample means asymptotically follow a normal distribution regardless of population distribution shape."),
            (a9_id, "Which measure of dispersion is calculated as the square root of the variance?", "mcq", "Interquartile Range", "Standard Deviation", "Mean Absolute Deviation", "Range", "B", 5.0, "Standard Deviation (\\sigma) is the positive square root of variance, expressing spread in the same measurement units as the data."),
            (a9_id, "True or False: The median of a numerical distribution is sensitive to extreme outliers.", "true_false", "True", "False", "", "", "False", 5.0, "The median is robust against extreme values because it depends on the middle rank order rather than numerical magnitudes."),
            (a9_id, "If a student has a test score of 82 in a class with mean 70 and standard deviation 6, what is their Z-score?", "mcq", "+1.5", "+2.0", "+2.5", "+1.2", "B", 5.0, "Z = (82 - 70) / 6 = 12 / 6 = +2.0 standard deviations above the mean."),
            (a9_id, "In a standard normal distribution, what percentage of observations falls within 2 standard deviations of the mean (\\mu \\pm 2\\sigma)?", "mcq", "68.2%", "90.0%", "95.4%", "99.7%", "C", 5.0, "The empirical 68-95-99.7 rule states 95.4% of probability mass lies within 2 standard deviations."),
            (a9_id, "Which of the following distributions is appropriate for modeling the count of independent events occurring in a fixed interval of time?", "mcq", "Poisson Distribution", "Normal Distribution", "Uniform Distribution", "Bernoulli Distribution", "A", 5.0, "Poisson distribution models discrete event occurrence counts over continuous intervals with constant rate \\lambda."),
            (a9_id, "What is Bayes' Theorem used for in probabilistic reasoning?", "mcq", "Calculating the exact arithmetic mean of a dataset", "Updating the posterior probability of an event given observed evidence and prior belief", "Sorting an array in linear time", "Inverting a non-square matrix", "B", 5.0, "Bayes' Theorem formalizes how prior probability is conditionally updated into posterior probability after observing evidence."),
            (a9_id, "Which of the following properties describe a valid Probability Density Function (PDF) f(x)? (Select all that apply)", "multiple_select", "f(x) >= 0 for all x", "Integral of f(x) over all x equals 1", "f(x) <= 0 for negative x", "f(x) must be discrete", "A,B", 5.0, "A valid continuous PDF must be non-negative everywhere and integrate to exactly 1 over its domain."),
            (a9_id, "Explain the difference between Type I error (alpha) and Type II error (beta) in statistical hypothesis testing.", "subjective", "", "", "", "", "Type I error is a False Positive (rejecting a true null hypothesis); Type II error is a False Negative (failing to reject a false null hypothesis).", 5.0, "Alpha is significance level; Power of test is 1 - beta."),
            (a9_id, "Explain how the Interquartile Range (IQR) is used to detect outliers in boxplot analysis.", "subjective", "", "", "", "", "IQR = Q3 - Q1. Any observation below Q1 - 1.5 * IQR or above Q3 + 1.5 * IQR is categorized as an outlier.", 5.0, "Standard 1.5 IQR multiplier defines outlier fence boundaries.")
        ]
        for q in a9_questions:
            cursor.execute("""
                INSERT INTO assessment_questions (assessment_id, question_text, question_type, option_a, option_b, option_c, option_d, correct_answer, marks, explanation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, q)

    # 4. Add Assessment 10: Semester Final Mock Examination (Machine Learning & AI)
    cursor.execute("SELECT id FROM assessments WHERE title LIKE '%Semester Final Examination Mock%'")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO assessments (title, description, subject, topic, duration_minutes, passing_marks, total_marks, negative_marking, attempt_limit, shuffle_questions, shuffle_options, is_proctored, is_published)
            VALUES (
                'Semester Final Examination Mock: Applied Machine Learning & Neural Modeling',
                'Comprehensive end-of-semester mock examination covering supervised regression, classification, decision tree splitting, ensemble methods, and unsupervised clustering.',
                'Machine Learning', 'Machine Learning', 40, 25, 60, 0.5, 2, 1, 1, 0, 1
            )
        """)
        a10_id = cursor.lastrowid
        print(f"Created Assessment 10 (ID {a10_id})")

        a10_questions = [
            (a10_id, "Which impurity measure does the CART decision tree algorithm minimize during recursive node splitting for classification?", "mcq", "Gini Impurity", "Mean Squared Error", "Adjusted R^2", "Silhouette Score", "A", 6.0, "CART uses Gini Impurity for classification splits and Mean Squared Error for regression splits."),
            (a10_id, "How does Random Forest achieve lower generalization variance compared to an individual Decision Tree?", "mcq", "By training a single very deep tree with no stopping criteria", "By averaging multiple de-correlated trees trained on bootstrap samples with random feature subspaces", "By pruning all leaf nodes", "By converting decision boundaries to linear functions", "B", 6.0, "Bagging plus feature subspace randomization de-correlates individual trees, reducing ensemble variance by 1/B."),
            (a10_id, "True or False: In K-Means clustering, feature scaling (StandardScaler) is mandatory because Euclidean distance is sensitive to feature magnitudes.", "true_false", "True", "False", "", "", "True", 6.0, "Features with larger numerical ranges dominate Euclidean distance calculations without normalization."),
            (a10_id, "In Principal Component Analysis (PCA), how are the principal component axes oriented with respect to one another?", "mcq", "Parallel to each other", "Orthogonal (perpendicular and uncorrelated) to each other", "At a 45 degree angle", "Randomly distributed", "B", 6.0, "All principal components are orthogonal eigenvectors of the covariance matrix, guaranteeing zero linear correlation between components."),
            (a10_id, "Which regularization technique adds a penalty proportional to the absolute values of weights (|w|_1), driving non-informative coefficients strictly to zero?", "mcq", "Ridge Regularization (L2)", "Lasso Regularization (L1)", "Dropout", "Early Stopping", "B", 6.0, "Lasso (L1) regularization generates sparse models by driving coefficients of redundant features to zero."),
            (a10_id, "What is the primary role of SHAP (SHapley Additive exPlanations) in the EduGap AI platform?", "mcq", "To train neural network weights faster", "To explain feature attribution and quantify each feature's contribution to a student's learning gap prediction", "To encrypt student database passwords", "To render HTML templates", "B", 6.0, "SHAP utilizes cooperative game theory (Shapley values) to provide mathematically grounded local and global feature attribution."),
            (a10_id, "In the proposed TAT-KG hybrid architecture, which algorithm estimates the latent concept mastery probability P(L_t)?", "mcq", "K-Means", "Bayesian Knowledge Tracing (BKT)", "Ordinary Least Squares", "Principal Component Analysis", "B", 6.0, "BKT tracks student concept understanding as a Hidden Markov Model based on sequential correct and incorrect responses."),
            (a10_id, "Which of the following are components of the proposed TAT-KG hybrid architecture? (Select all that apply)", "multiple_select", "Bayesian Knowledge Tracing (BKT)", "PyTorch Gated Recurrent Unit (GRU)", "LightGBM Late Feature Fusion", "Naive Bayes Classifier", "A,B,C", 6.0, "TAT-KG combines BKT for cognitive mastery, PyTorch GRU for temporal sequences, and LightGBM for late feature fusion."),
            (a10_id, "Explain why Macro F1-score is preferred over Raw Accuracy when evaluating learning gap severity classification.", "subjective", "", "", "", "", "Macro F1 calculates unweighted arithmetic mean across classes, ensuring high-gap and medium-gap minority classes are not overwhelmed by abundant low-gap observations.", 6.0, "Raw accuracy rewards majority class bias; Macro F1 penalizes failures on rare high learning gap observations."),
            (a10_id, "Explain how the Gated Recurrent Unit (GRU) processes chronological student activity telemetry to capture temporal learning decay.", "subjective", "", "", "", "", "The GRU takes timestamped sequential activity records (quizzes, attendance, engagement, login regularity) across curriculum modules and updates its hidden state h_t via reset and update gates, encoding behavioral trajectories into a 32-dimensional latent representation.", 6.0, "GRU captures longitudinal dynamics, fatigue, and declining quiz trends without vanishing gradients.")
        ]
        for q in a10_questions:
            cursor.execute("""
                INSERT INTO assessment_questions (assessment_id, question_text, question_type, option_a, option_b, option_c, option_d, correct_answer, marks, explanation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, q)

    conn.commit()
    conn.close()
    print("All expanded assessments and question bank seeded successfully!")


if __name__ == "__main__":
    seed_assessments()
