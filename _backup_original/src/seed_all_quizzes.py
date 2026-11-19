import sqlite3
from pathlib import Path

DATABASE = Path("database/learning_gap.db")

def seed_remaining_quizzes():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT id, topic_name FROM topics")
    topic_map = {row[1]: row[0] for row in cursor.fetchall()}

    new_quizzes = [
        {
            "topic": "SQL",
            "title": "SQL Querying & Data Definition Fundamentals",
            "description": "Assess proficiency in table structures, DDL/DML transactions, aggregations, and subqueries.",
            "duration": 15,
            "questions": [
                ("Which SQL command is used to remove all records from a table without logging individual row deletions?", "DELETE", "TRUNCATE", "DROP", "REMOVE", "B"),
                ("What is the default sorting order of the ORDER BY clause in SQL?", "DESC", "ASC", "RANDOM", "NONE", "B"),
                ("Which aggregate function ignores NULL values when calculating counts?", "COUNT(*)", "COUNT(column_name)", "SUM(NULL)", "TOTAL()", "B"),
                ("What does the DDL command ALTER TABLE accomplish?", "Modifies data rows in a table", "Modifies the schema definition of an existing table", "Deletes table contents", "Indexes table data automatically", "B"),
                ("Which clause must be used to filter rows before any GROUP BY aggregation takes place?", "HAVING", "WHERE", "LIMIT", "QUALIFY", "B")
            ]
        },
        {
            "topic": "Statistics",
            "title": "Descriptive & Inferential Statistics Examination",
            "description": "Evaluate core mastery over central tendency, dispersion, normal distributions, and hypothesis tests.",
            "duration": 20,
            "questions": [
                ("Which measure of central tendency is least affected by extreme outlier values?", "Mean", "Median", "Mode", "Variance", "B"),
                ("According to the Empirical Rule, what percentage of data falls within 2 standard deviations in a normal distribution?", "68.2%", "95.4%", "99.7%", "50.0%", "B"),
                ("What type of error occurs when the null hypothesis is rejected when it is actually true?", "Type I Error (Alpha)", "Type II Error (Beta)", "Standard Error", "Sampling Bias", "A"),
                ("What does a p-value less than 0.05 typically indicate in hypothesis testing?", "Accept the null hypothesis with certainty", "Reject the null hypothesis as statistically significant", "Test is invalid due to high variance", "Data is completely uniform", "B"),
                ("The Central Limit Theorem asserts that the sampling distribution of the mean approaches normal if:", "Sample size is sufficiently large (n >= 30)", "Population variance is zero", "Data has no outliers", "Mean equals median", "A")
            ]
        },
        {
            "topic": "Probability",
            "title": "Probability Foundations & Bayes Theorem Test",
            "description": "Test understanding of sample spaces, conditional probability distributions, and random variables.",
            "duration": 15,
            "questions": [
                ("If events A and B are mutually exclusive, what is P(A and B)?", "1.0", "P(A) * P(B)", "0.0", "P(A) + P(B)", "C"),
                ("In Bayes theorem P(A|B) = [P(B|A) * P(A)] / P(B), what is P(A) referred to as?", "Posterior probability", "Prior probability", "Likelihood", "Marginal evidence", "B"),
                ("What is the sum of probabilities of all possible elementary events in a discrete sample space?", "0.5", "Infinity", "1.0", "Depends on event count", "C"),
                ("Which discrete probability distribution models the number of successes in n independent Bernoulli trials?", "Poisson", "Binomial", "Geometric", "Exponential", "B"),
                ("The memoryless property is a unique characteristic of which continuous distribution?", "Normal", "Exponential", "Uniform", "Chi-Square", "B")
            ]
        },
        {
            "topic": "Classification",
            "title": "Supervised Classification & Model Diagnostics",
            "description": "Assess concepts in logistic regression, decision boundaries, ROC-AUC, and precision-recall trade-offs.",
            "duration": 20,
            "questions": [
                ("Which activation function squashes real-valued inputs into probabilities between 0 and 1?", "ReLU", "Sigmoid", "Tanh", "Leaky ReLU", "B"),
                ("In a confusion matrix, which metric calculates True Positives / (True Positives + False Positives)?", "Recall (Sensitivity)", "Precision (Positive Predictive Value)", "Accuracy", "Specificity", "B"),
                ("When evaluating a highly imbalanced dataset (e.g., 99% negative cases), which metric is most misleading?", "F1-Score", "Precision-Recall AUC", "Accuracy", "Cohen Kappa", "C"),
                ("What does the area under the ROC curve (AUC-ROC) quantify?", "Model inference latency", "Classifier capability to distinguish between binary classes across all thresholds", "Feature correlation to target", "Training loss rate", "B"),
                ("Which classification algorithm calculates distances using Euclidean or Manhattan metrics to classify instances?", "K-Nearest Neighbors (KNN)", "Decision Tree", "Naive Bayes", "Linear Discriminant Analysis", "A")
            ]
        },
        {
            "topic": "Decision Trees",
            "title": "Tree-Based Partitioning & Entropy Assessment",
            "description": "Evaluate recursive splitting, Shannon entropy, Gini impurity, and pruning mechanisms.",
            "duration": 15,
            "questions": [
                ("What metric measures the degree of randomness or impurity in a dataset during Decision Tree splitting?", "Information Gain", "Entropy", "Covariance", "Residual Variance", "B"),
                ("What value of Gini impurity indicates a pure node where all elements belong to a single class?", "1.0", "0.5", "0.0", "Infinity", "C"),
                ("What is the primary risk of an unpruned Decision Tree grown to maximum depth?", "High bias / underfitting", "High variance / overfitting", "Slow convergence", "Vanishing gradients", "B"),
                ("Which splitting algorithm is standardly used by scikit-learn for constructing classification trees?", "ID3", "C4.5", "CART", "CHAID", "C"),
                ("Cost-complexity pruning controls tree size using which parameter to penalize complex subtrees?", "Alpha (ccp_alpha)", "Learning rate", "Batch size", "Momentum", "A")
            ]
        },
        {
            "topic": "PCA",
            "title": "Dimensionality Reduction & PCA Diagnostics",
            "description": "Test understanding of principal component projections, eigenvalues, eigenvectors, and variance preservation.",
            "duration": 15,
            "questions": [
                ("What mathematical construct represents the direction of maximum variance in Principal Component Analysis?", "Eigenvalues", "Eigenvectors", "Covariance scalars", "Residual vectors", "B"),
                ("Why is feature standardization (mean=0, variance=1) critical before fitting PCA?", "PCA requires all values to be positive", "Features with larger variances artificially dominate the principal components", "PCA only converges on binary inputs", "Standardization prevents matrix inversion", "B"),
                ("Are principal components orthogonal to one another?", "No, they share high correlation", "Yes, they are mutually uncorrelated and orthogonal", "Only when dimension count is even", "Only for normalized data", "B"),
                ("What does the Explained Variance Ratio of the first principal component indicate?", "Model accuracy score", "Proportion of total dataset variance captured by the first component", "Noise level in the features", "Reconstruction loss percentage", "B"),
                ("Which matrix decomposition technique can be used directly to compute Principal Components efficiently?", "LU Decomposition", "QR Decomposition", "Singular Value Decomposition (SVD)", "Cholesky Decomposition", "C")
            ]
        }
    ]

    for qz in new_quizzes:
        t_id = topic_map.get(qz["topic"])
        if not t_id:
            print(f"Topic {qz['topic']} not found")
            continue
        cursor.execute("SELECT id FROM quizzes WHERE title = ?", (qz["title"],))
        existing = cursor.fetchone()
        if not existing:
            cursor.execute("""
                INSERT INTO quizzes (topic_id, title, description, total_questions, duration, due_date)
                VALUES (?, ?, ?, ?, ?, '2026-10-25')
            """, (t_id, qz["title"], qz["description"], len(qz["questions"]), qz["duration"]))
            quiz_id = cursor.lastrowid
            print(f"Inserted Quiz: {qz['title']} (ID: {quiz_id})")
        else:
            quiz_id = existing[0]
            print(f"Quiz already exists: {qz['title']} (ID: {quiz_id})")

        for q_text, op_a, op_b, op_c, op_d, ans in qz["questions"]:
            cursor.execute("SELECT id FROM questions WHERE quiz_id = ? AND question = ?", (quiz_id, q_text))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO questions (quiz_id, question, option_a, option_b, option_c, option_d, correct_answer)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (quiz_id, q_text, op_a, op_b, op_c, op_d, ans))

    conn.commit()
    conn.close()
    print("All 12 topic adaptive quizzes successfully provisioned.")

if __name__ == "__main__":
    seed_remaining_quizzes()
