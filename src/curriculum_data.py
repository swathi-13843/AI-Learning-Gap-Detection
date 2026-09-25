"""
Detailed Curriculum Roadmap and Subtopic Checklist for all 12 Core Topics in EduGap AI.
"""

CURRICULUM_ROADMAP = {
    "Python Basics": {
        "title": "Python Programming",
        "description": "Comprehensive journey from foundational syntax to practical industry implementations.",
        "levels": {
            "Beginner": [
                "Introduction to Python & Interpreted Execution",
                "Installing Python and using modern IDEs (VS Code / PyCharm)",
                "Variables, dynamically typed assignments & memory references",
                "Input and output operations (input(), print(), f-strings)",
                "Operators (Arithmetic, Relational, Logical, Bitwise)",
                "Strings, slicing, indexing & string methods",
                "Lists, mutability, indexing and list operations",
                "Tuples and immutability guarantees",
                "Sets, set mathematics (Union, Intersection, Difference)",
                "Dictionaries, key-value mappings & hash tables",
                "Conditional statements (if, elif, else)",
                "for loops, range() and nested loops",
                "while loops, break, continue and pass",
                "Functions, parameter passing, *args and **kwargs",
                "Modules, packages and namespace management",
                "Exception handling with try, except, else and finally"
            ],
            "Intermediate": [
                "File handling (Read, Write, Append, Context Management)",
                "List, set, and dictionary comprehensions",
                "Lambda anonymous functions",
                "Higher-order functions: map(), filter(), and zip()",
                "Object-oriented programming (OOP) paradigms",
                "Classes, object instantiation, attributes and self",
                "Inheritance, method overriding and polymorphism",
                "Iterators, __iter__(), __next__() and generators (yield)",
                "Decorators and function wrapping",
                "Regular expressions (re module pattern matching)",
                "Working with JSON parsing and serialization",
                "Date, time and timezone management with datetime",
                "Virtual environments (venv) isolation",
                "pip and dependency management (requirements.txt)",
                "Testing and debugging with unittest and pdb"
            ],
            "Advanced": [
                "Custom context managers using __enter__ and __exit__",
                "Type hints, static analysis and typing module",
                "Dataclasses and immutable records",
                "Functional programming concepts (itertools, functools)",
                "Multithreading and the Global Interpreter Lock (GIL)",
                "Multiprocessing and inter-process communication",
                "Asynchronous programming with asyncio, async and await",
                "Memory management, garbage collection and weakref",
                "Design patterns in Python (Singleton, Factory, Observer)",
                "Performance optimization with cProfile and Cython"
            ],
            "Practical Python": [
                "Numerical computation with NumPy",
                "Data wrangling and transformations with Pandas",
                "Visualizations and charts with Matplotlib & Seaborn",
                "Web scraping with BeautifulSoup and Scrapy",
                "REST API integration with requests and httpx",
                "Database programming with SQLite and SQLAlchemy ORM",
                "Web application development with Flask / FastAPI / Django",
                "Task automation, cron jobs and system scripting",
                "Exploratory data analysis on real-world datasets",
                "Applied machine learning with Scikit-learn",
                "End-to-end production Python application projects"
            ]
        }
    },
    "OOP": {
        "title": "Object-Oriented Programming (OOP)",
        "description": "Architectural object design, SOLID principles, and clean class hierarchies.",
        "levels": {
            "Beginner": [
                "Introduction to Object-Oriented paradigm vs Procedural",
                "Defining Classes and Instantiating Objects",
                "The __init__ constructor and self reference",
                "Instance Variables vs Class/Static Variables",
                "Defining and calling instance methods",
                "String representation: __str__ and __repr__",
                "Basic Encapsulation and Data Hiding"
            ],
            "Intermediate": [
                "Single and Multiple Inheritance hierarchies",
                "Method Overriding and the super() function",
                "Method Resolution Order (MRO) & C3 Linearization",
                "Polymorphism, Duck Typing and dynamic dispatch",
                "Getters, Setters and the @property decorator",
                "Class Methods (@classmethod) and Static Methods (@staticmethod)",
                "Abstract Base Classes (abc module and @abstractmethod)",
                "Operator Overloading and Python Special (Dunder) Methods",
                "Composition and Aggregation vs Inheritance"
            ],
            "Advanced": [
                "SOLID Architecture Principles in Object Design",
                "Metaclasses and Dynamic Class Creation (__new__)",
                "Slots (__slots__) for Memory Optimization",
                "Creational Patterns: Factory, Builder, Singleton",
                "Structural Patterns: Adapter, Facade, Decorator",
                "Behavioral Patterns: Strategy, Observer, Command",
                "Dependency Injection and Inversion of Control",
                "Thread-safety in object state mutations"
            ],
            "Practical Applications": [
                "Building an Extensible Banking / Account System",
                "Custom ORM Model Architecture from scratch",
                "Event-driven GUI or Game Entity hierarchy",
                "Enterprise Service Layer & Repository Pattern"
            ]
        }
    },
    "SQL": {
        "title": "Relational Databases & SQL Fundamentals",
        "description": "Data Definition, Manipulation, Aggregations, and Transaction Integrity.",
        "levels": {
            "Beginner": [
                "Relational Database Management System (RDBMS) Concepts",
                "Tables, Columns, Primary Keys & Foreign Keys",
                "DDL: CREATE, ALTER, DROP, TRUNCATE tables",
                "DML: INSERT, UPDATE, DELETE records",
                "Basic Queries: SELECT, FROM, WHERE filtering",
                "Comparison and Logical Operators (AND, OR, NOT, IN, BETWEEN)",
                "Pattern matching with LIKE and wildcards",
                "Sorting results using ORDER BY (ASC, DESC)",
                "Limiting and Paging with LIMIT and OFFSET",
                "Handling NULL values (IS NULL, IS NOT NULL, COALESCE)"
            ],
            "Intermediate": [
                "Aggregate Functions (COUNT, SUM, AVG, MIN, MAX)",
                "Grouping records using GROUP BY",
                "Filtering grouped records using HAVING",
                "Scalar and String functions (UPPER, LOWER, SUBSTR, CONCAT)",
                "Date and Time functions (NOW, DATEADD, DATEDIFF)",
                "Conditional query logic with CASE WHEN THEN ELSE END",
                "Single-row and multi-row subqueries",
                "Correlated subqueries and EXISTS / NOT EXISTS",
                "Set Operations (UNION, UNION ALL, INTERSECT, EXCEPT)",
                "Creating and Managing Views"
            ],
            "Advanced": [
                "ACID Properties (Atomicity, Consistency, Isolation, Durability)",
                "Transactions management (BEGIN, COMMIT, ROLLBACK, SAVEPOINT)",
                "Database Indexing (B-Tree, Hash, Unique, Composite Indexes)",
                "Query Execution Plans and EXPLAIN / EXPLAIN ANALYZE",
                "Common Table Expressions (CTEs) and Recursive CTEs",
                "Database Normalization (1NF, 2NF, 3NF, BCNF)",
                "Stored Procedures, User-Defined Functions and Triggers",
                "Database Security, Roles, GRANT and REVOKE permissions"
            ],
            "Practical SQL": [
                "Designing an E-commerce Relational Schema",
                "Financial ledger accounting with atomic transactions",
                "Building complex analytical reporting queries",
                "Optimizing slow enterprise SQL queries",
                "Database migrations and schema versioning"
            ]
        }
    },
    "SQL Joins": {
        "title": "Relational Joins & Advanced Querying",
        "description": "Multi-table data relational algebra, join mechanics, and window analytics.",
        "levels": {
            "Beginner": [
                "Relational data normalization and foreign key references",
                "Cartesian Product and CROSS JOIN mechanics",
                "INNER JOIN: Syntax, ON conditions and matching rules",
                "Joining two tables with alias prefixes",
                "Filtering joined datasets using WHERE clauses"
            ],
            "Intermediate": [
                "LEFT (OUTER) JOIN: Preserving left-table records",
                "RIGHT (OUTER) JOIN mechanics and symmetry",
                "FULL OUTER JOIN: Combining left and right unmatched rows",
                "Self Joins: Joining a table to itself (hierarchical data)",
                "Multi-table joins: Joining 3 or more tables in a single query",
                "Joining on multiple compound conditions (AND / OR)",
                "Non-Equi Joins (using <, >, BETWEEN in ON conditions)"
            ],
            "Advanced": [
                "Join algorithms under the hood (Nested Loop, Hash Join, Merge Join)",
                "Window Functions: OVER(), PARTITION BY, and ORDER BY",
                "Ranking functions (ROW_NUMBER, RANK, DENSE_RANK, NTILE)",
                "Value window functions (LAG, LEAD, FIRST_VALUE, LAST_VALUE)",
                "Window aggregate frames (ROWS BETWEEN UNBOUNDED PRECEDING)",
                "Optimizing Joins: Indexing foreign key join columns",
                "Mitigating duplicate row explosions in 1-to-Many joins"
            ],
            "Practical Joins": [
                "Customer Cohort Retention & Churn SQL pipelines",
                "Sales attribution across multi-touch marketing campaigns",
                "Year-over-Year (YoY) revenue growth analytics with LAG",
                "Organizational Employee-Manager Hierarchy traversal"
            ]
        }
    },
    "Statistics": {
        "title": "Statistical Analysis & Inference",
        "description": "Descriptive statistics, continuous distributions, and hypothesis testing.",
        "levels": {
            "Beginner": [
                "Types of Data: Qualitative vs Quantitative, Nominal, Ordinal, Interval, Ratio",
                "Measures of Central Tendency: Mean, Median, Mode",
                "Measures of Dispersion: Range, Interquartile Range (IQR), Variance, Standard Deviation",
                "Five-number summary and Box Plots",
                "Visualizing distributions: Histograms, Frequency Polygons, Bar Charts",
                "Skewness, Kurtosis and Modality of data"
            ],
            "Intermediate": [
                "Population parameters vs Sample statistics",
                "Covariance and Pearson Correlation Coefficient",
                "Spearman Rank Correlation for non-linear relationships",
                "Normal Distribution, Empirical Rule (68-95-99.7) and Z-Scores",
                "Standard Normal Distribution and Z-Tables",
                "Sampling methods: Simple Random, Stratified, Cluster, Systematic",
                "Central Limit Theorem (CLT) and Standard Error"
            ],
            "Advanced": [
                "Hypothesis Testing framework: Null (H0) vs Alternative (H1) Hypotheses",
                "Type I error (Alpha), Type II error (Beta) and Statistical Power",
                "p-values, Significance Levels and Decision Thresholds",
                "One-sample and Two-sample Student t-Tests",
                "Paired t-Test for dependent observations",
                "Analysis of Variance (One-Way and Two-Way ANOVA)",
                "Chi-Square Test of Independence and Goodness-of-Fit",
                "Confidence Intervals estimation (Mean and Proportions)",
                "Non-parametric tests (Mann-Whitney U, Wilcoxon Signed-Rank)"
            ],
            "Practical Applications": [
                "A/B Testing design and conversion experiment analysis",
                "Anomaly and Outlier detection via IQR and Z-Score fences",
                "Statistical process control and quality telemetry",
                "Hypothesis validation in empirical research studies"
            ]
        }
    },
    "Probability": {
        "title": "Probability Theory & Stochastic Processes",
        "description": "Combinatorics, conditional distributions, random variables, and Bayes theorem.",
        "levels": {
            "Beginner": [
                "Random Experiments, Sample Spaces, and Events",
                "Classical, Empirical, and Subjective Probability definitions",
                "Axioms of Probability (Kolmogorov's Axioms)",
                "Complement Rule, Addition Rule for Mutually Exclusive Events",
                "General Addition Rule for arbitrary events",
                "Independent vs Dependent Events",
                "Multiplication Rule of Probability"
            ],
            "Intermediate": [
                "Conditional Probability: P(A|B) formulation",
                "Law of Total Probability",
                "Bayes' Theorem: Prior, Likelihood, Evidence and Posterior",
                "Discrete Random Variables and Probability Mass Function (PMF)",
                "Continuous Random Variables and Probability Density Function (PDF)",
                "Cumulative Distribution Function (CDF)",
                "Expected Value (Mean) and Variance of a Random Variable",
                "Uniform and Bernoulli Distributions"
            ],
            "Advanced": [
                "Binomial Distribution and Pascal's Triangle",
                "Poisson Distribution for rare event modeling",
                "Geometric and Negative Binomial Distributions",
                "Exponential Distribution and Memoryless Property",
                "Joint, Marginal and Conditional Distributions",
                "Markov's and Chebyshev's Inequalities",
                "Law of Large Numbers (Weak and Strong laws)",
                "Maximum Likelihood Estimation (MLE)",
                "Markov Chains, Transition Matrices and Stationary Distributions"
            ],
            "Practical Applications": [
                "Spam Filter implementation using Naive Bayes Classifier",
                "Risk modeling and default probability estimation in credit",
                "Monte Carlo simulations for pricing and forecasting",
                "Reliability engineering and time-to-failure modeling"
            ]
        }
    },
    "Regression": {
        "title": "Supervised Learning: Regression Algorithms",
        "description": "Continuous target prediction, cost function optimization, and regularization.",
        "levels": {
            "Beginner": [
                "Introduction to Supervised Learning & Regression Tasks",
                "Simple Linear Regression: Hypothesis function (y = mx + b)",
                "Dependent variable vs Independent explanatory predictors",
                "Scatter plots and Best-Fit regression lines",
                "Ordinary Least Squares (OLS) objective",
                "Residuals and Sum of Squared Errors (SSE)",
                "Evaluation Metrics: Mean Absolute Error (MAE), Mean Squared Error (MSE)"
            ],
            "Intermediate": [
                "Multiple Linear Regression with vector notations",
                "Assumptions of Linear Regression (Linearity, Independence, Homoscedasticity, Normality)",
                "Root Mean Squared Error (RMSE) and R-Squared (Coefficient of Determination)",
                "Adjusted R-Squared for penalizing redundant features",
                "Gradient Descent Optimization (Batch, Stochastic, Mini-Batch)",
                "Learning Rate selection, convergence criteria and feature scaling",
                "Multicollinearity detection using Variance Inflation Factor (VIF)",
                "Polynomial Regression for capturing non-linear curves"
            ],
            "Advanced": [
                "Overfitting vs Underfitting: Bias-Variance Tradeoff",
                "Regularization: L2 Regularization (Ridge Regression)",
                "Regularization: L1 Regularization (Lasso Regression) & Sparsity",
                "Elastic Net: Combining L1 and L2 penalties",
                "Support Vector Regression (SVR) and Kernel Trick",
                "Decision Tree Regressors and Random Forest Regressors",
                "Gradient Boosted Regressors (XGBoost, LightGBM, CatBoost)",
                "Residual Analysis and Q-Q plots for homoscedasticity validation",
                "Hyperparameter tuning using GridSearchCV and Cross-Validation"
            ],
            "Practical Regression": [
                "Real Estate House Price Valuation model",
                "Sales and Demand Forecasting with macro trends",
                "Customer Lifetime Value (LTV) predictive estimation",
                "Stock Price volatility and risk regression modeling"
            ]
        }
    },
    "Classification": {
        "title": "Supervised Learning: Classification Methods",
        "description": "Categorical decision boundaries, loss functions, and classification evaluation.",
        "levels": {
            "Beginner": [
                "Classification Problem Formulation: Binary vs Multiclass",
                "Introduction to Logistic Regression & the Sigmoid Function",
                "Decision Thresholds and probability calibration",
                "K-Nearest Neighbors (KNN) classification algorithm",
                "Distance metrics (Euclidean, Manhattan, Minkowski)",
                "Confusion Matrix: True Positives, False Positives, True Negatives, False Negatives",
                "Accuracy metric and when Accuracy is misleading"
            ],
            "Intermediate": [
                "Precision, Recall (Sensitivity) and Specificity",
                "F1-Score and Weighted Harmonic Mean",
                "Receiver Operating Characteristic (ROC) Curve",
                "Area Under the ROC Curve (AUC-ROC)",
                "Log-Loss (Binary Cross-Entropy Loss function)",
                "Multiclass Classification strategies (One-vs-Rest, One-vs-One, Softmax)",
                "Support Vector Machines (SVM): Hyperplanes and Maximal Margin",
                "Kernel functions (Linear, RBF, Polynomial) in SVM",
                "Naive Bayes Classifier (Gaussian, Multinomial, Bernoulli)"
            ],
            "Advanced": [
                "Handling Imbalanced Datasets (SMOTE, Class Weights, Under-sampling)",
                "Precision-Recall Curves for highly imbalanced fraud cases",
                "Cost-sensitive learning and asymmetric misclassification penalties",
                "Ensemble Voting Classifiers (Hard vs Soft voting)",
                "Calibration of predicted probabilities (Platt Scaling, Isotonic)",
                "Multilabel classification and ranking metrics",
                "Threshold optimization for maximal business utility"
            ],
            "Practical Classification": [
                "Credit Card Fraud Detection with imbalanced sampling",
                "Customer Churn Prediction and proactive intervention",
                "Medical Disease Diagnosis from clinical lab markers",
                "Sentiment Analysis on customer feedback reviews"
            ]
        }
    },
    "Decision Trees": {
        "title": "Tree-Based Learning & Recursive Partitioning",
        "description": "Entropy, Gini impurity, tree pruning, and interpretable decision rules.",
        "levels": {
            "Beginner": [
                "Introduction to Tree structures (Root node, Decision nodes, Leaf nodes)",
                "How Decision Trees split feature space recursively",
                "Classification Trees vs Regression Trees",
                "Visualizing and Interpreting Decision Tree logic",
                "Handling categorical and numerical features in splits",
                "Advantages: Non-linear handling and zero feature scaling required"
            ],
            "Intermediate": [
                "Information Theory & Shannon Entropy",
                "Information Gain and the ID3 Algorithm",
                "Gini Impurity and the CART (Classification and Regression Trees) Algorithm",
                "Variance Reduction for Regression splits",
                "Decision boundaries of orthogonal axis-aligned splits",
                "Tree stopping criteria (max_depth, min_samples_split, min_samples_leaf)",
                "Susceptibility to High Variance and Overfitting"
            ],
            "Advanced": [
                "Cost-Complexity Pruning (Minimal Cost-Complexity alpha pruning)",
                "Pre-pruning vs Post-pruning strategies",
                "Feature Importance calculation via Gini Importance",
                "Surrogate splits for handling missing values",
                "Instability of Decision Trees (sensitivity to training perturbations)",
                "Exporting Decision Trees to Graphviz, PMML and ONNX"
            ],
            "Practical Decision Trees": [
                "Credit Approval Rule Engine with white-box explanations",
                "Medical Triage Protocol mapping",
                "Customer Loan default underwriting workflow",
                "Benchmarking Single Tree vs Ensemble accuracy"
            ]
        }
    },
    "Random Forest": {
        "title": "Ensemble Learning: Random Forests",
        "description": "Bagging, bootstrap aggregation, out-of-bag validation, and feature importance.",
        "levels": {
            "Beginner": [
                "Concept of Ensemble Learning: Wisdom of the Crowd",
                "Ensemble methods overview: Bagging vs Boosting",
                "What is a Random Forest?",
                "Bootstrapping: Sampling with replacement",
                "Aggregating predictions: Majority voting and averaging",
                "Why Random Forest dramatically outperforms single Decision Trees"
            ],
            "Intermediate": [
                "Bagging (Bootstrap Aggregation) mechanics",
                "Random Subspace Method (feature bagging at each tree split)",
                "Hyperparameter: n_estimators (number of decision trees)",
                "Hyperparameter: max_features (sqrt, log2, fraction)",
                "Out-Of-Bag (OOB) error estimation and validation without test sets",
                "Variance reduction proof without increasing model bias",
                "Parallelization and distributed training (n_jobs parameter)"
            ],
            "Advanced": [
                "Mean Decrease in Impurity (MDI) vs Permutation Feature Importance",
                "Extremely Randomized Trees (ExtraTrees) algorithm",
                "Proximity matrices and unsupervised Random Forests",
                "Handling correlated features in Random Forest importance scores",
                "SHAP (SHapley Additive exPlanations) values on TreeExplainer",
                "Tree pruning in ensembles and memory footprint reduction",
                "Random Forest model compression for edge deployment"
            ],
            "Practical Random Forest": [
                "Student Academic Risk Classification (Current Production Model)",
                "Customer Churn Prediction in SaaS platforms",
                "Bioinformatics Gene Expression feature selection",
                "Sensor Fault Detection in Industrial IoT"
            ]
        }
    },
    "K-Means": {
        "title": "Unsupervised Learning: K-Means Clustering",
        "description": "Centroid-based geometric clustering, distance metrics, and cluster evaluation.",
        "levels": {
            "Beginner": [
                "Supervised vs Unsupervised Learning paradigms",
                "What is Clustering and grouping unlabeled data?",
                "K-Means algorithm high-level workflow",
                "Step 1: Random Centroid Initialization",
                "Step 2: Assign data points to nearest centroid",
                "Step 3: Recompute centroids as mean of assigned points",
                "Convergence criteria (centroids stop moving)"
            ],
            "Intermediate": [
                "Euclidean Distance and Manhattan Distance formulations",
                "Importance of Feature Standardization (StandardScaler)",
                "Inertia (Within-Cluster Sum of Squares - WCSS)",
                "Choosing K: The Elbow Method heuristic",
                "Silhouette Score and Silhouette Plots for cluster cohesion/separation",
                "Sensitivity to Outliers and initial centroid placement",
                "K-Means++ initialization algorithm and its mathematical guarantees"
            ],
            "Advanced": [
                "Voronoi Diagrams and partitioning of metric spaces",
                "Mini-Batch K-Means for massive web-scale datasets",
                "Limitations: Inability to cluster non-spherical or varied-density manifolds",
                "Alternatives comparison: DBSCAN, Hierarchical Clustering, GMM",
                "Davies-Bouldin Index and Calinski-Harabasz Index metrics",
                "Dimensionality reduction preprocessing (PCA + K-Means pipeline)"
            ],
            "Practical K-Means": [
                "Student Behavioral Persona Segmentation (Current Model)",
                "Customer Market Basket and RFM Segmentation",
                "Image Color Quantization and Compression",
                "Geographical Store Location optimization"
            ]
        }
    },
    "PCA": {
        "title": "Dimensionality Reduction: Principal Component Analysis",
        "description": "Eigenvectors, variance maximization, orthogonal projections, and compression.",
        "levels": {
            "Beginner": [
                "Curse of Dimensionality: Challenges of high-dimensional feature spaces",
                "What is Dimensionality Reduction?",
                "Feature Selection vs Feature Extraction",
                "Geometric intuition: Finding the axis of maximum variance",
                "Orthogonality: Uncorrelated Principal Components",
                "Visualizing multi-dimensional data in 2D and 3D scatter plots"
            ],
            "Intermediate": [
                "Mean Centering and Feature Scaling necessity",
                "Covariance Matrix computation",
                "Linear Algebra foundations: Eigenvalues and Eigenvectors",
                "Eigen-decomposition of the Covariance Matrix",
                "Singular Value Decomposition (SVD) connection to PCA",
                "Projecting high-dimensional data onto Principal Component axes",
                "Explained Variance Ratio and Cumulative Explained Variance plot"
            ],
            "Advanced": [
                "Choosing the number of components (e.g. 95% variance threshold)",
                "Factor Loadings and interpreting original feature contributions",
                "Reconstruction Error and lossy data compression",
                "Kernel PCA for capturing non-linear manifold structures",
                "Incremental PCA for streaming and out-of-core datasets",
                "Sparse PCA for improved feature interpretability",
                "Using PCA as a pre-processing step to combat multicollinearity in ML"
            ],
            "Practical PCA": [
                "Facial Recognition Eigenfaces decomposition",
                "High-frequency financial market portfolio factor modeling",
                "Single-cell RNA sequencing visualization in genomics",
                "Accelerating Machine Learning pipeline training speeds"
            ]
        }
    }
}
