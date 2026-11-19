"""
Theory Content and Conceptual Diagrams Repository for EduGap AI.
Covers all 12 B.Tech Curriculum Topics:
1. Python Basics
2. Object-Oriented Programming (OOP)
3. SQL & Relational Models
4. SQL Joins & Multi-Table Queries
5. Descriptive Statistics & Analytics
6. Probability & Distributions
7. Linear & Logistic Regression
8. Classification & Performance Metrics
9. Decision Trees & Impurity Metrics
10. Random Forest & Ensemble Learning
11. K-Means & Unsupervised Clustering
12. PCA & Dimensionality Reduction
"""

import sqlite3
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "database" / "learning_gap.db"

THEORY_DATA = [
    {
        "subject": "Python Programming",
        "unit": "Unit 1: Fundamentals & Control Structures",
        "topic_name": "Python Basics",
        "definition": "Python is a high-level, dynamically typed, interpreted programming language known for its clean syntax, readability, and multi-paradigm support across procedural, object-oriented, and functional styles.",
        "detailed_explanation": "Python source code (.py) is compiled into an intermediate bytecode (.pyc) executed by the Python Virtual Machine (PVM). Memory management is managed automatically through reference counting and a generational cyclic garbage collector. In CPython, execution is synchronized across CPU cores via the Global Interpreter Lock (GIL). Key data primitives include immutable scalars (int, float, bool, str) and collection structures (lists, tuples, sets, dictionaries). Control flow relies on PEP-8 standard 4-space indentation rather than curly brackets.",
        "important_points": json.dumps([
            "Dynamic typing: variable types are bound at runtime rather than compile time.",
            "Immutable vs Mutable: Tuples, strings, and integers are immutable; lists, dicts, and sets are mutable.",
            "List comprehensions provide concise syntax for sequence transformation: [expr for item in iterable if condition].",
            "Exception handling utilizes try-except-else-finally blocks for resilient runtime fault isolation."
        ]),
        "advantages": json.dumps([
            "Exceptional developer productivity and rapid prototyping velocity.",
            "Vast scientific ecosystem including NumPy, Pandas, Scikit-Learn, PyTorch, and SciPy.",
            "Cross-platform execution across Linux, Windows, macOS, and embedded architectures."
        ]),
        "disadvantages": json.dumps([
            "Slower raw execution speed compared to compiled languages like C++ or Rust.",
            "Global Interpreter Lock (GIL) limits native multithreaded CPU-bound parallelism in CPython.",
            "Dynamic typing can introduce runtime type errors if not strictly guarded by type hints."
        ]),
        "real_world_examples": "Automated backend microservices (Flask, FastAPI), scientific data processing pipelines in astronomy and genomics, and machine learning training harnesses.",
        "applications": "Web Development, Artificial Intelligence & Machine Learning, Data Analytics, Cybersecurity Scripting, DevOps Automation.",
        "short_questions": json.dumps([
            {"q": "What is the difference between a list and a tuple in Python?", "a": "Lists are mutable sequences defined with square brackets []; tuples are immutable sequences defined with parentheses () that cannot be altered post-instantiation."},
            {"q": "What is the role of the Global Interpreter Lock (GIL)?", "a": "The GIL is a mutex in CPython that prevents multiple native threads from executing Python bytecode simultaneously, simplifying thread-safe memory management."},
            {"q": "Explain the purpose of the 'pass' statement in Python.", "a": "The 'pass' statement is a syntactic null-operation placeholder used where a statement is syntactically required but no action should be executed."}
        ]),
        "long_questions": json.dumps([
            {"q": "Explain Python's memory management model, including reference counting, cyclic garbage collection, and memory pools.", "a": "CPython manages memory primarily through reference counting: each object tracks how many pointers refer to it. When an object's reference counter drops to zero, its memory is deallocated immediately. To resolve circular references (where Object A points to B and B points to A, keeping counts > 0), Python uses a generational garbage collector with three generations (0, 1, 2) that periodically scans objects for unreachable cycles. Furthermore, PyMalloc allocates small objects (< 512 bytes) in pre-allocated 256KB arenas subdivided into 4KB pools to reduce system allocator overhead."},
            {"q": "Discuss the internal execution model of Python from source script (.py) to bytecode (.pyc) and execution on the Python Virtual Machine (PVM).", "a": "When a Python script executes, the source code undergoes lexical analysis, tokenization, and parsing into an Abstract Syntax Tree (AST). The AST is compiled into portable bytecode (.pyc stored in __pycache__). The Python Virtual Machine (PVM), which is a stack-based software emulation of a computer, reads the bytecode instructions (e.g., LOAD_FAST, BINARY_ADD, STORE_FAST) and executes them inside an evaluation loop, interfacing with the operating system."}
        ]),
        "formulas": "List Indexing: idx \\in [0, N-1] \\cup [-N, -1]; Slice: [start:stop:step]; Time Complexity of Dict Lookup: O(1) average, O(N) worst case.",
        "key_takeaways": "Mastering Python fundamentals, collection mutability, memory references, and list comprehensions is an indispensable prerequisite for all downstream data structures and machine learning implementations.",
        "diagram_title": "Python Compilation and PVM Execution Architecture",
        "diagram_type": "Architecture Diagram",
        "diagram_svg": """<svg viewBox="0 0 780 240" xmlns="http://www.w3.org/2000/svg" style="background:#0f172a; border-radius:12px; font-family:sans-serif;">
  <rect x="20" y="70" width="130" height="90" rx="8" fill="#1e293b" stroke="#6366f1" stroke-width="2"/>
  <text x="85" y="110" fill="#f8fafc" font-size="14" font-weight="bold" text-anchor="middle">Source Code</text>
  <text x="85" y="132" fill="#94a3b8" font-size="12" text-anchor="middle">script.py</text>
  
  <path d="M 150 115 L 210 115" stroke="#6366f1" stroke-width="2" marker-end="url(#arrow)"/>
  
  <rect x="210" y="70" width="140" height="90" rx="8" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
  <text x="280" y="105" fill="#f8fafc" font-size="14" font-weight="bold" text-anchor="middle">Python Compiler</text>
  <text x="280" y="125" fill="#38bdf8" font-size="11" text-anchor="middle">Lex / Parse / AST</text>
  <text x="280" y="142" fill="#94a3b8" font-size="11" text-anchor="middle">Generates Bytecode</text>
  
  <path d="M 350 115 L 410 115" stroke="#38bdf8" stroke-width="2"/>
  
  <rect x="410" y="70" width="140" height="90" rx="8" fill="#1e293b" stroke="#10b981" stroke-width="2"/>
  <text x="480" y="110" fill="#f8fafc" font-size="14" font-weight="bold" text-anchor="middle">Bytecode Cache</text>
  <text x="480" y="132" fill="#10b981" font-size="12" text-anchor="middle">.pyc (__pycache__)</text>
  
  <path d="M 550 115 L 610 115" stroke="#10b981" stroke-width="2"/>
  
  <rect x="610" y="55" width="150" height="120" rx="8" fill="#1e293b" stroke="#f59e0b" stroke-width="2"/>
  <text x="685" y="95" fill="#f8fafc" font-size="14" font-weight="bold" text-anchor="middle">Python VM (PVM)</text>
  <text x="685" y="118" fill="#f59e0b" font-size="11" text-anchor="middle">Evaluation Loop</text>
  <text x="685" y="136" fill="#94a3b8" font-size="11" text-anchor="middle">Stack &amp; Garbage Collector</text>
  <text x="685" y="154" fill="#34d399" font-size="11" font-weight="bold" text-anchor="middle">Native Machine Execution</text>
  
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#6366f1"/>
    </marker>
  </defs>
</svg>"""
    },
    {
        "subject": "Python Programming",
        "unit": "Unit 2: Object-Oriented Design Paradigms",
        "topic_name": "OOP",
        "definition": "Object-Oriented Programming (OOP) is a software design paradigm structured around 'objects' that encapsulate state (attributes) and behavior (methods) adhering to encapsulation, inheritance, polymorphism, and abstraction.",
        "detailed_explanation": "In Python, everything is an object, including functions and primitives. Classes act as blueprints defined with the class keyword. The dunder method __init__(self, ...) initializes object state. Encapsulation is achieved by convention: public members (name), protected members (_name), and private name-mangled members (__name). Python supports multiple inheritance resolved through the C3 Superclass Linearization algorithm (Method Resolution Order, MRO accessible via cls.__mro__). Polymorphism allows uniform method invocation across distinct class hierarchies through duck typing.",
        "important_points": json.dumps([
            "Four Pillars: Encapsulation (data hiding), Abstraction (simplifying complex reality), Inheritance (code reuse), Polymorphism (multiple forms).",
            "MRO (Method Resolution Order): Deterministic inheritance resolution order calculated with C3 linearization.",
            "Special / Magic Dunder Methods: __repr__, __str__, __len__, __getitem__, and __eq__ allow operator overloading and protocol adherence.",
            "Composition over inheritance: Favoring 'has-a' object composition over deep 'is-a' inheritance trees produces more maintainable systems."
        ]),
        "advantages": json.dumps([
            "Modular software architecture with clear separation of responsibilities.",
            "High code reusability through inheritance and modular component composition.",
            "Information hiding protects internal invariants from external corruption."
        ]),
        "disadvantages": json.dumps([
            "Higher memory footprint due to per-instance dictionary (__dict__) overhead (can be mitigated with __slots__).",
            "Can lead to over-engineering and steep learning curves when deep class hierarchies are used.",
            "Slight runtime overhead from dynamic method dispatch."
        ]),
        "real_world_examples": "PyTorch nn.Module hierarchy, Django Model ORM classes, and GUI widget frameworks like PyQt and Tkinter.",
        "applications": "Enterprise Software Engineering, Simulation Engines, Game Development, Scalable Framework Development.",
        "short_questions": json.dumps([
            {"q": "What is the purpose of 'self' in Python class methods?", "a": "'self' is an explicit reference to the current instance of the class upon which a method is invoked, allowing access to instance attributes and methods."},
            {"q": "What is the Diamond Problem and how does Python resolve it?", "a": "The Diamond Problem occurs in multiple inheritance when a class inherits from two classes that share a common ancestor. Python resolves this deterministically using the C3 Linearization algorithm to generate the Method Resolution Order (MRO)."},
            {"q": "What is the difference between class methods and static methods in Python?", "a": "@classmethod receives the class 'cls' as its first parameter and can access class state; @staticmethod receives neither 'self' nor 'cls' and behaves as an isolated utility function grouped under the class namespace."}
        ]),
        "long_questions": json.dumps([
            {"q": "Detail the Four Pillars of OOP with concrete Python code examples illustrating Encapsulation, Abstraction, Inheritance, and Polymorphism.", "a": "Encapsulation bundles data and methods while restricting direct access via name mangling (e.g. self.__balance). Abstraction hides complex underlying details, implemented using the abc module's ABC and @abstractmethod decorators. Inheritance enables a derived class (e.g., class SavingsAccount(Account)) to inherit and extend base attributes and methods. Polymorphism enables heterogeneous objects to respond to the same interface (e.g., calling calculate_interest() on different account instances)."},
            {"q": "Explain the role of Dunder (Magic) methods in Python and how they enable Operator Overloading and Context Management.", "a": "Dunder methods (double underscore) allow classes to emulate built-in types. For operator overloading, __add__(self, other) maps to the '+' operator, while __eq__ maps to '=='. For context management (the 'with' statement), classes implement __enter__ to acquire resources and __exit__ to guarantee resource teardown even in the presence of unhandled exceptions."}
        ]),
        "formulas": "C3 MRO Linearization: L(C) = C + merge(L(B_1), L(B_2), ..., L(B_n), B_1 B_2 ... B_n); Instance Size Reduction: __slots__ = ('attr1', 'attr2')",
        "key_takeaways": "OOP provides the architectural scaffolding for industrial Python systems, with special emphasis on encapsulation, duck typing, and protocol-based polymorphism.",
        "diagram_title": "The Four Pillars of Object-Oriented Programming",
        "diagram_type": "Concept Diagram",
        "diagram_svg": """<svg viewBox="0 0 780 260" xmlns="http://www.w3.org/2000/svg" style="background:#0f172a; border-radius:12px; font-family:sans-serif;">
  <rect x="30" y="40" width="160" height="180" rx="10" fill="#1e293b" stroke="#6366f1" stroke-width="2"/>
  <circle cx="110" cy="80" r="24" fill="rgba(99,102,241,0.2)"/>
  <text x="110" y="86" fill="#818cf8" font-size="16" font-weight="bold" text-anchor="middle">1</text>
  <text x="110" y="130" fill="#f8fafc" font-size="15" font-weight="bold" text-anchor="middle">Encapsulation</text>
  <text x="110" y="155" fill="#94a3b8" font-size="11.5" text-anchor="middle">Data Hiding</text>
  <text x="110" y="175" fill="#94a3b8" font-size="11.5" text-anchor="middle">Private Attributes</text>
  <text x="110" y="195" fill="#6366f1" font-size="11" text-anchor="middle">_protected, __private</text>

  <rect x="220" y="40" width="160" height="180" rx="10" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
  <circle cx="300" cy="80" r="24" fill="rgba(56,189,248,0.2)"/>
  <text x="300" y="86" fill="#38bdf8" font-size="16" font-weight="bold" text-anchor="middle">2</text>
  <text x="300" y="130" fill="#f8fafc" font-size="15" font-weight="bold" text-anchor="middle">Abstraction</text>
  <text x="300" y="155" fill="#94a3b8" font-size="11.5" text-anchor="middle">Hiding Complexity</text>
  <text x="300" y="175" fill="#94a3b8" font-size="11.5" text-anchor="middle">Clean Interface</text>
  <text x="300" y="195" fill="#38bdf8" font-size="11" text-anchor="middle">abc.ABC, @abstract</text>

  <rect x="410" y="40" width="160" height="180" rx="10" fill="#1e293b" stroke="#10b981" stroke-width="2"/>
  <circle cx="490" cy="80" r="24" fill="rgba(16,185,129,0.2)"/>
  <text x="490" y="86" fill="#10b981" font-size="16" font-weight="bold" text-anchor="middle">3</text>
  <text x="490" y="130" fill="#f8fafc" font-size="15" font-weight="bold" text-anchor="middle">Inheritance</text>
  <text x="490" y="155" fill="#94a3b8" font-size="11.5" text-anchor="middle">Code Reuse</text>
  <text x="490" y="175" fill="#94a3b8" font-size="11.5" text-anchor="middle">Parent &amp; Child</text>
  <text x="490" y="195" fill="#10b981" font-size="11" text-anchor="middle">super(), C3 MRO</text>

  <rect x="600" y="40" width="160" height="180" rx="10" fill="#1e293b" stroke="#f59e0b" stroke-width="2"/>
  <circle cx="680" cy="80" r="24" fill="rgba(245,158,11,0.2)"/>
  <text x="680" y="86" fill="#f59e0b" font-size="16" font-weight="bold" text-anchor="middle">4</text>
  <text x="680" y="130" fill="#f8fafc" font-size="15" font-weight="bold" text-anchor="middle">Polymorphism</text>
  <text x="680" y="155" fill="#94a3b8" font-size="11.5" text-anchor="middle">Multiple Forms</text>
  <text x="680" y="175" fill="#94a3b8" font-size="11.5" text-anchor="middle">Duck Typing</text>
  <text x="680" y="195" fill="#f59e0b" font-size="11" text-anchor="middle">Method Overriding</text>
</svg>"""
    },
    {
        "subject": "Database Management Systems",
        "unit": "Unit 1: Relational Model & SQL DDL/DML",
        "topic_name": "SQL",
        "definition": "Structured Query Language (SQL) is the standard declarative language for defining, querying, manipulating, and controlling data in Relational Database Management Systems (RDBMS).",
        "detailed_explanation": "SQL operates on relational algebra primitives (selection, projection, Cartesian product, union, set difference). It is partitioned into sublanguages: DDL (Data Definition Language: CREATE, ALTER, DROP, TRUNCATE), DML (Data Manipulation Language: SELECT, INSERT, UPDATE, DELETE), DCL (Data Control Language: GRANT, REVOKE), and TCL (Transaction Control Language: COMMIT, ROLLBACK, SAVEPOINT). Relational integrity is enforced through constraints: Primary Keys (PK, uniqueness + NOT NULL), Foreign Keys (FK, referential integrity), Unique, Check, and Not Null constraints.",
        "important_points": json.dumps([
            "Declarative nature: SQL queries specify *what* data to retrieve, while the query optimizer determines *how* to retrieve it.",
            "ACID properties: Atomicity, Consistency, Isolation, and Durability guarantee reliable transactional execution.",
            "Logical Query Execution Order: FROM -> WHERE -> GROUP BY -> HAVING -> SELECT -> DISTINCT -> ORDER BY -> LIMIT.",
            "Indexes (B-Tree and Hash) drastically accelerate read performance from O(N) to O(log N) at the cost of slower write throughput."
        ]),
        "advantages": json.dumps([
            "Strict schema enforcement ensures reliable data integrity across enterprise domains.",
            "Standardized declarative syntax supported by all major vendors (PostgreSQL, MySQL, SQLite, Oracle).",
            "Powerful aggregate and analytical capabilities (WINDOW functions, CTEs, subqueries)."
        ]),
        "disadvantages": json.dumps([
            "Vertical scalability limits compared to distributed NoSQL key-value stores.",
            "Rigid table schemas require costly schema migrations for rapidly evolving polymorphic data.",
            "Improperly indexed queries can cause severe Cartesian products and table lock contention."
        ]),
        "real_world_examples": "Banking transactional ledgers, e-commerce order management systems, and academic student information systems.",
        "applications": "Financial Accounting, Telecommunications Billing, Healthcare Records, Inventory Logistics.",
        "short_questions": json.dumps([
            {"q": "What is the difference between WHERE and HAVING in SQL?", "a": "WHERE filters individual rows before aggregation occurs; HAVING filters aggregated groups produced by GROUP BY."},
            {"q": "Explain the difference between DROP, TRUNCATE, and DELETE.", "a": "DELETE is a DML statement that removes rows conditionally and can be rolled back; TRUNCATE is a DDL statement that deallocates data pages rapidly without per-row logging; DROP completely removes the table schema and data."},
            {"q": "What is referential integrity?", "a": "Referential integrity is a relational database constraint that prevents foreign key values from existing without a corresponding primary key in the referenced parent table."}
        ]),
        "long_questions": json.dumps([
            {"q": "Explain the ACID properties of relational database transactions and how Write-Ahead Logging (WAL) ensures Durability.", "a": "Atomicity ensures all statements in a transaction commit successfully or all are rolled back. Consistency guarantees database transitions between valid states respecting all constraints. Isolation ensures concurrent transactions do not interfere (managed via isolation levels: Read Uncommitted, Read Committed, Repeatable Read, Serializable). Durability ensures committed changes survive crashes. Write-Ahead Logging (WAL) guarantees Durability by writing transaction log records to persistent storage before data pages are flushed from volatile buffer pools to disk."},
            {"q": "Detail the logical query processing order of an SQL SELECT statement and why understanding it is critical for writing valid queries.", "a": "Unlike procedural languages that execute top-to-bottom, an SQL engine processes clauses logically: 1. FROM & JOIN (constructs base Cartesian set), 2. WHERE (filters rows), 3. GROUP BY (aggregates into groups), 4. HAVING (filters groups), 5. SELECT (evaluates projections and expressions), 6. DISTINCT (removes duplicate rows), 7. ORDER BY (sorts final result), 8. LIMIT / OFFSET (truncates output). This explains why column aliases defined in SELECT cannot be referenced in WHERE, but can be used in ORDER BY."}
        ]),
        "formulas": "Relational Selection: \\sigma_{\\text{condition}}(R); Relational Projection: \\pi_{\\text{attributes}}(R); Cartesian Product: R \\times S; Index Lookup: O(\\log_B N)",
        "key_takeaways": "Understanding logical query processing phases and relational constraints is essential for designing high-performance database queries and avoiding costly table scans.",
        "diagram_title": "SQL Logical Query Execution Processing Pipeline",
        "diagram_type": "Process Flowchart",
        "diagram_svg": """<svg viewBox="0 0 780 180" xmlns="http://www.w3.org/2000/svg" style="background:#0f172a; border-radius:12px; font-family:sans-serif;">
  <g transform="translate(10, 30)">
    <rect x="0" y="20" width="85" height="70" rx="6" fill="#1e293b" stroke="#6366f1" stroke-width="2"/>
    <text x="42" y="50" fill="#6366f1" font-size="12" font-weight="bold" text-anchor="middle">Step 1</text>
    <text x="42" y="70" fill="#f8fafc" font-size="13" font-weight="bold" text-anchor="middle">FROM</text>
    
    <path d="M 85 55 L 105 55" stroke="#64748b" stroke-width="2"/>
    
    <rect x="105" y="20" width="85" height="70" rx="6" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
    <text x="147" y="50" fill="#38bdf8" font-size="12" font-weight="bold" text-anchor="middle">Step 2</text>
    <text x="147" y="70" fill="#f8fafc" font-size="13" font-weight="bold" text-anchor="middle">WHERE</text>
    
    <path d="M 190 55 L 210 55" stroke="#64748b" stroke-width="2"/>
    
    <rect x="210" y="20" width="95" height="70" rx="6" fill="#1e293b" stroke="#10b981" stroke-width="2"/>
    <text x="257" y="50" fill="#10b981" font-size="12" font-weight="bold" text-anchor="middle">Step 3</text>
    <text x="257" y="70" fill="#f8fafc" font-size="13" font-weight="bold" text-anchor="middle">GROUP BY</text>
    
    <path d="M 305 55 L 325 55" stroke="#64748b" stroke-width="2"/>
    
    <rect x="325" y="20" width="85" height="70" rx="6" fill="#1e293b" stroke="#f59e0b" stroke-width="2"/>
    <text x="367" y="50" fill="#f59e0b" font-size="12" font-weight="bold" text-anchor="middle">Step 4</text>
    <text x="367" y="70" fill="#f8fafc" font-size="13" font-weight="bold" text-anchor="middle">HAVING</text>
    
    <path d="M 410 55 L 430 55" stroke="#64748b" stroke-width="2"/>
    
    <rect x="430" y="20" width="85" height="70" rx="6" fill="#1e293b" stroke="#ec4899" stroke-width="2"/>
    <text x="472" y="50" fill="#ec4899" font-size="12" font-weight="bold" text-anchor="middle">Step 5</text>
    <text x="472" y="70" fill="#f8fafc" font-size="13" font-weight="bold" text-anchor="middle">SELECT</text>
    
    <path d="M 515 55 L 535 55" stroke="#64748b" stroke-width="2"/>
    
    <rect x="535" y="20" width="100" height="70" rx="6" fill="#1e293b" stroke="#8b5cf6" stroke-width="2"/>
    <text x="585" y="50" fill="#8b5cf6" font-size="12" font-weight="bold" text-anchor="middle">Step 6</text>
    <text x="585" y="70" fill="#f8fafc" font-size="13" font-weight="bold" text-anchor="middle">ORDER BY</text>
    
    <path d="M 635 55 L 655 55" stroke="#64748b" stroke-width="2"/>
    
    <rect x="655" y="20" width="95" height="70" rx="6" fill="#1e293b" stroke="#06b6d4" stroke-width="2"/>
    <text x="702" y="50" fill="#06b6d4" font-size="12" font-weight="bold" text-anchor="middle">Step 7</text>
    <text x="702" y="70" fill="#f8fafc" font-size="13" font-weight="bold" text-anchor="middle">LIMIT</text>
  </g>
  <text x="390" y="145" fill="#94a3b8" font-size="12" text-anchor="middle">Data flows through logical filter and projection gates sequentially</text>
</svg>"""
    },
    {
        "subject": "Database Management Systems",
        "unit": "Unit 2: Multi-Table Joins & Relational Algebra",
        "topic_name": "SQL Joins",
        "definition": "SQL Joins are binary relational operations that combine rows from two or more tables based on a related column predicate, enabling multi-table analytical queries.",
        "detailed_explanation": "Join operations correspond to relational theta-joins ($R \\bowtie_\\theta S$) or equijoins. Major join types include: INNER JOIN (returns records with matching keys in both tables), LEFT (OUTER) JOIN (returns all records from the left table and matched records from the right table, filling non-matches with NULL), RIGHT (OUTER) JOIN (returns all from right and matches from left), and FULL (OUTER) JOIN (returns all rows from both tables, filling unmatched columns with NULL). Physical execution engines use three primary join algorithms: Nested Loop Join (O(M * N)), Hash Join (O(M + N)), and Sort-Merge Join (O(M log M + N log N)).",
        "important_points": json.dumps([
            "INNER JOIN: Intersection of both tables based on join condition.",
            "LEFT JOIN: All rows from Left table preserved; missing Right table values are populated with NULL.",
            "CROSS JOIN: Cartesian product yielding M x N rows without any predicate.",
            "Self Join: A table joined with itself to model recursive hierarchies (e.g., Employee-Manager)."
        ]),
        "advantages": json.dumps([
            "Enables database normalization (3NF/BCNF) by avoiding data redundancy and update anomalies.",
            "Highly optimized by query planners utilizing table statistics and index access paths.",
            "Supports flexible ad-hoc multi-dimensional business reporting."
        ]),
        "disadvantages": json.dumps([
            "Multi-table joins across unindexed columns cause severe performance degradation.",
            "Outer joins can generate massive result sets and unexpected NULL propagation.",
            "Distributed joins across partitioned shards require costly network data shuffling."
        ]),
        "real_world_examples": "Joining student demography with assessment attempts, linking e-commerce orders with customer records, and joining bank accounts with transaction ledgers.",
        "applications": "Business Intelligence Dashboards, Enterprise Resource Planning (ERP), Data Warehousing, Reporting.",
        "short_questions": json.dumps([
            {"q": "What is the difference between an INNER JOIN and a LEFT JOIN?", "a": "INNER JOIN returns only rows where the join predicate matches in both tables. LEFT JOIN returns all rows from the left table regardless of whether a matching record exists in the right table."},
            {"q": "What occurs when joining two tables without an ON clause?", "a": "Omitting the ON clause produces a Cartesian Product (CROSS JOIN) where every row of the first table is paired with every row of the second table, resulting in N x M rows."},
            {"q": "How can you query only rows that exist in Table A but NOT in Table B using a JOIN?", "a": "Perform a LEFT JOIN from Table A to Table B on the primary/foreign key and add a WHERE clause checking 'WHERE B.key IS NULL'."}
        ]),
        "long_questions": json.dumps([
            {"q": "Compare the three physical join algorithms used by modern relational database engines: Nested Loop Join, Hash Join, and Sort-Merge Join.", "a": "1. Nested Loop Join: Iterates over the outer table and probes the inner table for each row. Cost is O(M * N) without index, or O(M * log N) if the inner table has an index. Ideal for small outer tables. 2. Hash Join: Builds an in-memory hash table on the smaller table's join keys (Build Phase) and then streams the larger table to probe matches (Probe Phase). Cost is O(M + N). Highly efficient for large equijoins without pre-existing sort orders. 3. Sort-Merge Join: Sorts both tables on the join keys if not already ordered, then walks pointers through both tables in tandem. Cost is O(M log M + N log N) for sorting, plus O(M + N) for merging. Ideal when inputs are already sorted via clustered index."},
            {"q": "Explain how EduGap AI detects a Hidden Learning Gap in SQL Joins for students with high overall academic performance.", "a": "In EduGap AI, a student may maintain an overall quiz GPA of 85%, attendance of 90%, and assignment grades of 80%, while scoring only 30% in SQL Joins. Standard aggregate tracking flags them as 'Good Standing'. The TAT-KG hybrid engine calculates the Topic Performance Differential (Δ = 85% - 30% = +55%), recognizes the student as an 'is_hidden_gap_candidate', updates the Bayesian Knowledge Tracing (BKT) concept mastery down to 16.5%, and encodes the localized sequence dip via the GRU temporal model. Fused LightGBM overrides the high attendance bias and accurately flags the isolated topic gap for targeted video remediation."}
        ]),
        "formulas": "Equijoin: R \\bowtie_{R.A = S.B} S; Left Outer Join: R \\mathbin{\\unicode{x27D5}} S; Cartesian Product: |R \\times S| = |R| \\cdot |S|",
        "key_takeaways": "SQL Joins represent a critical conceptual threshold in database curriculum; mastery requires understanding both set-theoretic Venn semantics and relational execution engine costs.",
        "diagram_title": "Visual Venn Diagrams of Core SQL Join Operations",
        "diagram_type": "Comparison Diagram",
        "diagram_svg": """<svg viewBox="0 0 780 260" xmlns="http://www.w3.org/2000/svg" style="background:#0f172a; border-radius:12px; font-family:sans-serif;">
  <!-- INNER JOIN -->
  <g transform="translate(40, 20)">
    <circle cx="60" cy="90" r="50" fill="none" stroke="#64748b" stroke-width="2"/>
    <circle cx="110" cy="90" r="50" fill="none" stroke="#64748b" stroke-width="2"/>
    <path d="M 85 53 A 50 50 0 0 1 110 90 A 50 50 0 0 1 85 127 A 50 50 0 0 1 60 90 A 50 50 0 0 1 85 53 Z" fill="#6366f1" opacity="0.85"/>
    <text x="85" y="165" fill="#f8fafc" font-size="14" font-weight="bold" text-anchor="middle">INNER JOIN</text>
    <text x="85" y="185" fill="#94a3b8" font-size="11" text-anchor="middle">Only Matching Rows</text>
    <text x="45" y="95" fill="#94a3b8" font-size="12">Table A</text>
    <text x="115" y="95" fill="#94a3b8" font-size="12">Table B</text>
  </g>

  <!-- LEFT JOIN -->
  <g transform="translate(230, 20)">
    <circle cx="60" cy="90" r="50" fill="#38bdf8" opacity="0.85"/>
    <circle cx="110" cy="90" r="50" fill="#0f172a" stroke="#64748b" stroke-width="2"/>
    <path d="M 85 53 A 50 50 0 0 1 110 90 A 50 50 0 0 1 85 127 A 50 50 0 0 1 60 90 A 50 50 0 0 1 85 53 Z" fill="#38bdf8" opacity="0.85"/>
    <circle cx="60" cy="90" r="50" fill="none" stroke="#38bdf8" stroke-width="2"/>
    <text x="85" y="165" fill="#f8fafc" font-size="14" font-weight="bold" text-anchor="middle">LEFT JOIN</text>
    <text x="85" y="185" fill="#94a3b8" font-size="11" text-anchor="middle">All A + Matches in B</text>
    <text x="40" y="95" fill="#0f172a" font-weight="bold" font-size="12">Table A</text>
    <text x="115" y="95" fill="#94a3b8" font-size="12">Table B</text>
  </g>

  <!-- RIGHT JOIN -->
  <g transform="translate(420, 20)">
    <circle cx="60" cy="90" r="50" fill="#0f172a" stroke="#64748b" stroke-width="2"/>
    <circle cx="110" cy="90" r="50" fill="#10b981" opacity="0.85"/>
    <circle cx="110" cy="90" r="50" fill="none" stroke="#10b981" stroke-width="2"/>
    <circle cx="60" cy="90" r="50" fill="none" stroke="#64748b" stroke-width="2"/>
    <text x="85" y="165" fill="#f8fafc" font-size="14" font-weight="bold" text-anchor="middle">RIGHT JOIN</text>
    <text x="85" y="185" fill="#94a3b8" font-size="11" text-anchor="middle">All B + Matches in A</text>
    <text x="45" y="95" fill="#94a3b8" font-size="12">Table A</text>
    <text x="115" y="95" fill="#0f172a" font-weight="bold" font-size="12">Table B</text>
  </g>

  <!-- FULL OUTER JOIN -->
  <g transform="translate(610, 20)">
    <circle cx="60" cy="90" r="50" fill="#f59e0b" opacity="0.75"/>
    <circle cx="110" cy="90" r="50" fill="#f59e0b" opacity="0.75"/>
    <circle cx="60" cy="90" r="50" fill="none" stroke="#f59e0b" stroke-width="2"/>
    <circle cx="110" cy="90" r="50" fill="none" stroke="#f59e0b" stroke-width="2"/>
    <text x="85" y="165" fill="#f8fafc" font-size="14" font-weight="bold" text-anchor="middle">FULL OUTER JOIN</text>
    <text x="85" y="185" fill="#94a3b8" font-size="11" text-anchor="middle">All Rows from Both</text>
  </g>
</svg>"""
    },
    {
        "subject": "Data Science & Mathematics",
        "unit": "Unit 1: Descriptive Statistics & Spread Measures",
        "topic_name": "Statistics",
        "definition": "Statistics is the mathematical discipline concerning the collection, organization, analysis, interpretation, and presentation of quantitative data.",
        "detailed_explanation": "Statistics is divided into Descriptive Statistics (summarizing observed data) and Inferential Statistics (drawing population conclusions from samples). Central tendency is measured by Mean (arithmetic average, sensitive to outliers), Median (middle value in sorted data, robust to skewness), and Mode (most frequent value). Dispersion is quantified by Variance (mean squared deviation), Standard Deviation (square root of variance in native units), Interquartile Range (IQR = Q3 - Q1), and Range. Skewness measures distributional asymmetry, while Kurtosis quantifies tail heaviness.",
        "important_points": json.dumps([
            "Central Tendency: Mean, Median, Mode. In a symmetrical normal distribution, Mean = Median = Mode.",
            "Variance (\\sigma^2) and Standard Deviation (\\sigma) quantify how spread out observations are from the mean.",
            "IQR (Interquartile Range) is resistant to extreme outliers and is used in boxplot outlier thresholds [Q1 - 1.5*IQR, Q3 + 1.5*IQR].",
            "Central Limit Theorem (CLT): The sampling distribution of sample means approaches a normal distribution as sample size N >= 30, regardless of the underlying population shape."
        ]),
        "advantages": json.dumps([
            "Provides mathematical rigor to summarize massive telemetry datasets concisely.",
            "Essential for feature scaling (Z-score normalization), data cleaning, and outlier pruning.",
            "Enables hypothesis testing (t-tests, ANOVA) for statistically sound decision making."
        ]),
        "disadvantages": json.dumps([
            "Mean and standard deviation are severely distorted by extreme non-Gaussian outliers.",
            "Correlation does not imply causation (omitted variable bias, confounding factors).",
            "Misinterpreting p-values can lead to false discoveries (p-hacking)."
        ]),
        "real_world_examples": "Student test score distribution analysis, clinical drug efficacy trials, and A/B testing in web applications.",
        "applications": "Machine Learning Feature Preprocessing, Quality Control, Clinical Epidemiology, Quantitative Finance.",
        "short_questions": json.dumps([
            {"q": "Why is the median preferred over the mean for skewed distributions?", "a": "The median depends only on the rank order of values and is resistant to extreme outliers, whereas the mean is pulled heavily toward long tails."},
            {"q": "What is the formula for calculating Z-score and what does it represent?", "a": "Z = (X - \\mu) / \\sigma. It measures the number of standard deviations an observation X lies above or below the mean \\mu."},
            {"q": "State the 68-95-99.7 Empirical Rule for a Gaussian Normal Distribution.", "a": "In a normal distribution, approximately 68.2% of data falls within 1 standard deviation of the mean (\\mu \\pm \\sigma), 95.4% within 2 standard deviations (\\mu \\pm 2\\sigma), and 99.7% within 3 standard deviations (\\mu \\pm 3\\sigma)."}
        ]),
        "long_questions": json.dumps([
            {"q": "Explain the Central Limit Theorem (CLT) and why it forms the bedrock of statistical hypothesis testing and machine learning.", "a": "The Central Limit Theorem states that given a population with mean \\mu and finite variance \\sigma^2, the sampling distribution of the sample mean \\bar{X} computed from independent and identically distributed (i.i.d.) samples of size N will asymptotically converge to a normal distribution N(\\mu, \\sigma^2 / N) as N grows large (typically N >= 30), regardless of the underlying population's shape. This justifies assuming normality for parameter estimators, constructing confidence intervals, and performing t-tests."},
            {"q": "Discuss the mathematical mechanisms for detecting and handling outliers in feature engineering.", "a": "Outliers can be detected via parametric methods (Z-score > 3 or < -3 for Gaussian distributions) or non-parametric methods using the Interquartile Range (IQR = Q3 - Q1), defining outlier bounds as [Q1 - 1.5 * IQR, Q3 + 1.5 * IQR]. Outliers can be handled via Winsorization (capping at 5th/95th percentiles), logarithmic or Box-Cox power transformations, or robust scaling using median and IQR."}
        ]),
        "formulas": "Sample Mean: \\bar{X} = \\frac{1}{N}\\sum_{i=1}^N X_i; Sample Variance: S^2 = \\frac{1}{N-1}\\sum_{i=1}^N (X_i - \\bar{X})^2; Z = \\frac{X - \\mu}{\\sigma}",
        "key_takeaways": "Descriptive statistics define the initial exploratory data analysis (EDA) phase and provide the statistical scaling required for ML models like KNN, SVM, and Neural Networks.",
        "diagram_title": "Gaussian Normal Distribution and Empirical Standard Deviation Bands",
        "diagram_type": "Data Distribution Chart",
        "diagram_svg": """<svg viewBox="0 0 780 240" xmlns="http://www.w3.org/2000/svg" style="background:#0f172a; border-radius:12px; font-family:sans-serif;">
  <path d="M 60 200 C 200 200, 300 40, 390 40 C 480 40, 580 200, 720 200" fill="none" stroke="#6366f1" stroke-width="3"/>
  <line x1="390" y1="40" x2="390" y2="200" stroke="#f8fafc" stroke-width="2" stroke-dasharray="4"/>
  <text x="390" y="218" fill="#f8fafc" font-size="13" font-weight="bold" text-anchor="middle">Mean (μ)</text>
  
  <line x1="290" y1="95" x2="290" y2="200" stroke="#38bdf8" stroke-width="1.5" stroke-dasharray="3"/>
  <line x1="490" y1="95" x2="490" y2="200" stroke="#38bdf8" stroke-width="1.5" stroke-dasharray="3"/>
  <text x="290" y="218" fill="#38bdf8" font-size="12" text-anchor="middle">μ - 1σ</text>
  <text x="490" y="218" fill="#38bdf8" font-size="12" text-anchor="middle">μ + 1σ</text>
  <rect x="310" y="110" width="160" height="28" rx="4" fill="rgba(56,189,248,0.2)"/>
  <text x="390" y="128" fill="#38bdf8" font-size="12" font-weight="bold" text-anchor="middle">68.2% of Data</text>

  <line x1="190" y1="165" x2="190" y2="200" stroke="#10b981" stroke-width="1.5" stroke-dasharray="3"/>
  <line x1="590" y1="165" x2="590" y2="200" stroke="#10b981" stroke-width="1.5" stroke-dasharray="3"/>
  <text x="190" y="218" fill="#10b981" font-size="12" text-anchor="middle">μ - 2σ</text>
  <text x="590" y="218" fill="#10b981" font-size="12" text-anchor="middle">μ + 2σ</text>
  <text x="390" y="80" fill="#f59e0b" font-size="12" font-weight="bold" text-anchor="middle">95.4% within ± 2σ</text>
</svg>"""
    },
    {
        "subject": "Data Science & Mathematics",
        "unit": "Unit 2: Probability Theory & Bayesian Inference",
        "topic_name": "Probability",
        "definition": "Probability is the mathematical framework quantifying the likelihood of random events, formalizing uncertainty through axioms, conditional probability, and Bayes' Theorem.",
        "detailed_explanation": "Probability satisfies Kolmogorov's axioms: non-negativity (P(E) >= 0), unit measure (P(Omega) = 1), and countable additivity for disjoint events. Conditional probability P(A|B) measures the likelihood of event A given that B has occurred. Independent events satisfy P(A and B) = P(A) * P(B). Bayes' Theorem allows posterior belief updating by combining prior knowledge P(A) with observed evidence likelihood P(B|A). In EduGap AI, Bayesian Knowledge Tracing (BKT) leverages this theorem to update the latent concept mastery probability conditioned on whether a student answered a question correctly or incorrectly.",
        "important_points": json.dumps([
            "Bayes' Theorem: P(A|B) = [P(B|A) * P(A)] / P(B).",
            "Joint vs Marginal Probability: Marginal is the probability of a single event; joint is the probability of co-occurrence.",
            "Bayesian Knowledge Tracing (BKT) is an exact Hidden Markov Model applying Bayes' rule over sequential practice trials.",
            "Probability Distributions: Discrete (Bernoulli, Binomial, Poisson) and Continuous (Uniform, Gaussian, Exponential)."
        ]),
        "advantages": json.dumps([
            "Provides principled mathematical foundations for machine learning under uncertainty.",
            "Bayesian updating naturally handles streaming, incremental data without retraining from scratch.",
            "Directly yields calibrated probability estimates rather than uncalibrated binary decisions."
        ]),
        "disadvantages": json.dumps([
            "Requires selecting prior distributions, which can introduce subjective bias if poorly calibrated.",
            "Exact inference in high-dimensional Bayesian networks is NP-hard (requiring MCMC or variational approximations).",
            "Assumption of feature independence (e.g., Naive Bayes) is frequently violated in real data."
        ]),
        "real_world_examples": "Bayesian spam filtering, medical diagnostic test interpretation, and knowledge tracing in intelligent tutoring systems.",
        "applications": "Robotics Localization (Kalman Filters), Machine Learning Classification, Risk Analysis, Knowledge Tracing.",
        "short_questions": json.dumps([
            {"q": "State Bayes' Theorem and name each term.", "a": "P(A|B) = [P(B|A) * P(A)] / P(B), where P(A|B) is the Posterior, P(B|A) is the Likelihood, P(A) is the Prior, and P(B) is the Marginal Evidence."},
            {"q": "What does it mean for two events A and B to be mutually exclusive versus independent?", "a": "Mutually exclusive means they cannot occur simultaneously (P(A and B) = 0). Independent means the occurrence of one does not affect the probability of the other (P(A and B) = P(A) * P(B))."},
            {"q": "How does BKT update student knowledge mastery after an incorrect response?", "a": "BKT applies Bayes' rule using the slip probability P(S) in the numerator: P(L_t|incorrect) = [P(L_{t-1}) * P(S)] / [P(L_{t-1}) * P(S) + (1 - P(L_{t-1})) * (1 - P(G))]."}
        ]),
        "long_questions": json.dumps([
            {"q": "Derive Bayes' Theorem from the definition of conditional probability and explain its application in Bayesian Knowledge Tracing (BKT).", "a": "From the definition of conditional probability: P(A|B) = P(A and B) / P(B) and P(B|A) = P(A and B) / P(A). Solving for the joint probability: P(A and B) = P(B|A) * P(A). Substituting this into the first equation yields Bayes' Theorem: P(A|B) = [P(B|A) * P(A)] / P(B). In BKT, let L be the latent state 'student has mastered concept' and X be 'observed answer is correct'. The posterior mastery P(L_t | X=1) is updated after every observation using guess probability P(G) and slip probability P(S), driving dynamic mastery meters in EduGap AI."},
            {"q": "Discuss the difference between Frequentist and Bayesian interpretations of probability in academic evaluation systems.", "a": "The Frequentist approach views probability strictly as the long-run relative frequency of repeatable experiments, treating parameters as fixed unknown constants. The Bayesian perspective treats probability as a measure of degree of belief or certainty, representing parameters as random variables with probability distributions that update as new observations arrive. In EduGap AI, Bayesian tracking allows continuous belief updates from small question sequences without requiring hundreds of trials."}
        ]),
        "formulas": "Bayes' Rule: P(A \\mid B) = \\frac{P(B \\mid A) P(A)}{P(B)}; Law of Total Probability: P(B) = \\sum_{i} P(B \\mid A_i) P(A_i)",
        "key_takeaways": "Probability theory provides the mathematical bridge between deterministic data and uncertainty modeling, forming the core engine of Bayesian Knowledge Tracing in EduGap AI.",
        "diagram_title": "Bayesian Knowledge Tracing (BKT) Two-State HMM Architecture",
        "diagram_type": "Model Architecture Diagram",
        "diagram_svg": """<svg viewBox="0 0 780 240" xmlns="http://www.w3.org/2000/svg" style="background:#0f172a; border-radius:12px; font-family:sans-serif;">
  <!-- Unlearned State -->
  <circle cx="180" cy="120" r="55" fill="#1e293b" stroke="#f87171" stroke-width="3"/>
  <text x="180" y="115" fill="#f8fafc" font-size="14" font-weight="bold" text-anchor="middle">State 0</text>
  <text x="180" y="135" fill="#f87171" font-size="12" font-weight="bold" text-anchor="middle">Unlearned</text>
  
  <!-- Learned State -->
  <circle cx="600" cy="120" r="55" fill="#1e293b" stroke="#34d399" stroke-width="3"/>
  <text x="600" y="115" fill="#f8fafc" font-size="14" font-weight="bold" text-anchor="middle">State 1</text>
  <text x="600" y="135" fill="#34d399" font-size="12" font-weight="bold" text-anchor="middle">Mastered</text>

  <!-- Transition Arrow -->
  <path d="M 235 110 L 545 110" stroke="#38bdf8" stroke-width="2.5" marker-end="url(#bkt-arrow)"/>
  <text x="390" y="98" fill="#38bdf8" font-size="13" font-weight="bold" text-anchor="middle">Transition Probability P(T)</text>

  <!-- Observations -->
  <rect x="290" y="170" width="200" height="50" rx="8" fill="#1e293b" stroke="#6366f1" stroke-width="2"/>
  <text x="390" y="192" fill="#f8fafc" font-size="12" font-weight="bold" text-anchor="middle">Emission Probabilities</text>
  <text x="390" y="210" fill="#94a3b8" font-size="11" text-anchor="middle">Guess P(G) = 0.20 | Slip P(S) = 0.10</text>

  <defs>
    <marker id="bkt-arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#38bdf8"/>
    </marker>
  </defs>
</svg>"""
    },
    {
        "subject": "Machine Learning",
        "unit": "Unit 1: Supervised Learning & Continuous Prediction",
        "topic_name": "Regression",
        "definition": "Regression is a supervised learning methodology that models the relationship between independent input features and a continuous target variable.",
        "detailed_explanation": "Ordinary Least Squares (OLS) Linear Regression finds weight vector W that minimizes the Residual Sum of Squares (RSS). Regularization prevents overfitting: Ridge (L2 penalty) shrinks weights continuously toward zero; Lasso (L1 penalty) drives non-informative weights strictly to zero performing automatic feature selection; ElasticNet combines L1 and L2. Logistic Regression adapts the linear formulation to binary classification by passing the linear logit through the Sigmoid activation function to model probabilities.",
        "important_points": json.dumps([
            "OLS Cost Function: J(w) = (1 / 2N) * sum((y_pred - y_true)^2).",
            "Assumptions of Linear Regression: Linearity, Independence of errors, Homoscedasticity (constant variance), Normality of residuals, No multicollinearity.",
            "Ridge Regression (L2) prevents extreme weights; Lasso Regression (L1) creates sparse models.",
            "Evaluation Metrics: Mean Absolute Error (MAE), Mean Squared Error (MSE), Root Mean Squared Error (RMSE), and R-squared (R^2)."
        ]),
        "advantages": json.dumps([
            "Highly interpretable: feature coefficients directly indicate magnitude and direction of influence.",
            "Low computational complexity: O(D^3) closed-form normal equation or O(N * D) gradient descent.",
            "Provides closed-form statistical inference (p-values, confidence intervals for coefficients)."
        ]),
        "disadvantages": json.dumps([
            "Incapable of modeling complex non-linear relationships without manual polynomial feature expansion.",
            "Severely degraded by multicollinearity (high correlation between input features).",
            "Sensitive to extreme leverage outliers in the input space."
        ]),
        "real_world_examples": "Predicting student final exam scores based on quiz history and attendance, real estate pricing, and stock volatility forecasting.",
        "applications": "Academic Performance Forecasting, Econometrics, Sales Forecasting, Algorithmic Trading.",
        "short_questions": json.dumps([
            {"q": "What is the key difference between Ridge (L2) and Lasso (L1) regularization?", "a": "Ridge shrinks coefficients asymptotically toward zero but never makes them zero; Lasso shrinks coefficients to absolute zero, performing automatic feature selection."},
            {"q": "What does an R-squared value of 0.85 indicate?", "a": "It indicates that 85% of the total variance in the target dependent variable is explained by the independent features in the regression model."},
            {"q": "Why is Mean Absolute Error (MAE) more robust than Mean Squared Error (MSE)?", "a": "MSE squares errors, penalizing large outliers quadratically, whereas MAE scales linearly with error magnitude."}
        ]),
        "long_questions": json.dumps([
            {"q": "Derive the closed-form Normal Equation for Ordinary Least Squares (OLS) Linear Regression.", "a": "Let X be the N x D feature matrix and Y be the N x 1 target vector. The Residual Sum of Squares cost function in matrix form is J(W) = (Y - XW)^T (Y - XW) = Y^T Y - 2 W^T X^T Y + W^T X^T X W. Setting the gradient with respect to W to zero: dJ/dW = -2 X^T Y + 2 X^T X W = 0 => X^T X W = X^T Y. Assuming (X^T X) is non-singular and invertible, multiplying by its inverse yields the Normal Equation: W = (X^T X)^{-1} X^T Y."},
            {"q": "Explain the Bias-Variance Tradeoff in the context of regularized linear regression.", "a": "Total expected generalization error decomposes into Bias^2 + Variance + Irreducible Noise. High bias stems from overly simplistic models (underfitting) failing to capture true trends. High variance stems from excessively complex models (overfitting) modeling random sample noise. Regularization (via parameter \\lambda in Ridge/Lasso) introduces a controlled amount of bias to dramatically decrease variance, minimizing overall out-of-sample prediction error."}
        ]),
        "formulas": "Hypothesis: \\hat{y} = w^T x + b; Normal Equation: w = (X^T X)^{-1} X^T y; Ridge Cost: J(w) = \\text{MSE} + \\lambda \\|w\\|_2^2; Lasso Cost: J(w) = \\text{MSE} + \\lambda \\|w\\|_1",
        "key_takeaways": "Regression models establish fundamental understanding of cost function minimization, gradient descent optimization, and regularization principles applied across all machine learning.",
        "diagram_title": "Ordinary Least Squares Residual Minimization",
        "diagram_type": "Process Diagram",
        "diagram_svg": """<svg viewBox="0 0 780 240" xmlns="http://www.w3.org/2000/svg" style="background:#0f172a; border-radius:12px; font-family:sans-serif;">
  <line x1="80" y1="200" x2="720" y2="200" stroke="#64748b" stroke-width="2"/>
  <line x1="80" y1="200" x2="80" y2="30" stroke="#64748b" stroke-width="2"/>
  <text x="730" y="205" fill="#94a3b8" font-size="12">Feature (X)</text>
  <text x="75" y="20" fill="#94a3b8" font-size="12">Target (y)</text>
  
  <!-- Best Fit Line -->
  <line x1="100" y1="180" x2="680" y2="50" stroke="#6366f1" stroke-width="3"/>
  <text x="640" y="40" fill="#6366f1" font-size="13" font-weight="bold">y = wx + b</text>

  <!-- Data Points and Residuals -->
  <circle cx="200" cy="130" r="5" fill="#38bdf8"/>
  <line x1="200" y1="130" x2="200" y2="158" stroke="#f87171" stroke-width="2" stroke-dasharray="3"/>

  <circle cx="340" cy="150" r="5" fill="#38bdf8"/>
  <line x1="340" y1="150" x2="340" y2="126" stroke="#f87171" stroke-width="2" stroke-dasharray="3"/>

  <circle cx="480" cy="70" r="5" fill="#38bdf8"/>
  <line x1="480" y1="70" x2="480" y2="95" stroke="#f87171" stroke-width="2" stroke-dasharray="3"/>

  <circle cx="600" cy="85" r="5" fill="#38bdf8"/>
  <line x1="600" y1="85" x2="600" y2="68" stroke="#f87171" stroke-width="2" stroke-dasharray="3"/>

  <rect x="280" y="15" width="220" height="35" rx="6" fill="#1e293b" stroke="#f87171" stroke-width="1.5"/>
  <text x="390" y="37" fill="#f87171" font-size="12" font-weight="bold" text-anchor="middle">Residuals: e_i = y_i - ŷ_i (Minimizing RSS)</text>
</svg>"""
    },
    {
        "subject": "Machine Learning",
        "unit": "Unit 2: Discrete Target Prediction & Metric Evaluation",
        "topic_name": "Classification",
        "definition": "Classification is a supervised machine learning task that maps input feature vectors to discrete categorical class labels.",
        "detailed_explanation": "Classification algorithms determine decision boundaries separating classes in feature space. In binary classification, decision thresholds convert continuous probabilities into classes. Multi-class settings use One-vs-Rest (OvR) or Softmax cross-entropy loss. Model performance must be evaluated using a Confusion Matrix consisting of True Positives (TP), True Negatives (TN), False Positives (FP, Type I error), and False Negatives (FN, Type II error). From these, Precision, Recall (Sensitivity), Specificity, Macro F1, Weighted F1, ROC-AUC, and PR-AUC are computed.",
        "important_points": json.dumps([
            "Accuracy is misleading on class-imbalanced datasets; Precision, Recall, and Macro F1 provide reliable assessment.",
            "Precision = TP / (TP + FP): Proportion of predicted positives that were truly positive (minimizes False Alarms).",
            "Recall = TP / (TP + FN): Proportion of actual positives correctly identified (critical in medical and learning gap detection).",
            "ROC-AUC evaluates ranking quality across all classification thresholds; PR-AUC is superior when positive class is rare."
        ]),
        "advantages": json.dumps([
            "Directly solves core decision problems: Risk categorization, fraud detection, medical triage.",
            "Probabilistic outputs enable decision threshold optimization based on asymmetric misclassification costs.",
            "Wide variety of algorithmic families: Linear (Logistic), Margin-based (SVM), Tree-based (RF, LightGBM), Non-parametric (KNN)."
        ]),
        "disadvantages": json.dumps([
            "Class imbalance causes classifiers to predict majority class exclusively if not mitigated by SMOTE or class weights.",
            "Calibration mismatch: raw predicted scores may not reflect true empirical probabilities.",
            "Higher-dimensional feature spaces suffer from the curse of dimensionality."
        ]),
        "real_world_examples": "EduGap AI learning gap severity categorization (Low, Medium, High Gap), spam detection, and medical imaging diagnosis.",
        "applications": "Academic At-Risk Classification, Credit Risk Scoring, Medical Diagnostics, Fraud Detection.",
        "short_questions": json.dumps([
            {"q": "What is the difference between Macro F1 and Weighted F1?", "a": "Macro F1 calculates the arithmetic mean of F1 scores across classes giving equal weight to each class regardless of frequency. Weighted F1 weights each class's F1 by its support, which can mask poor performance on small minority classes."},
            {"q": "What is a Type I error versus a Type II error?", "a": "Type I error is a False Positive (rejecting a true null hypothesis); Type II error is a False Negative (failing to detect an actual positive condition)."},
            {"q": "Why is Recall crucial in learning gap detection?", "a": "A False Negative means a student with a severe learning gap is missed by the system, denying them critical remedial intervention."}
        ]),
        "long_questions": json.dumps([
            {"q": "Construct a complete Confusion Matrix and define Precision, Recall, Specificity, and F1-score mathematically.", "a": "A Confusion Matrix cross-tabulates actual vs. predicted labels with TP, FP, FN, TN. Precision = TP / (TP + FP) measures predictive purity. Recall (Sensitivity) = TP / (TP + FN) measures completeness. Specificity = TN / (TN + FP) measures true negative rate. F1-score is the harmonic mean: 2 * (Precision * Recall) / (Precision + Recall). The harmonic mean penalizes extreme divergence between Precision and Recall more heavily than the arithmetic mean."},
            {"q": "Discuss strategies for handling severe class imbalance in machine learning classification pipelines.", "a": "1. Resampling: SMOTE (Synthetic Minority Over-sampling Technique) creates interpolated feature vectors for minority classes on training data only. Random undersampling prunes majority class instances. 2. Algorithmic adjustments: Cost-sensitive learning uses class weights inversely proportional to class frequencies in the loss function. 3. Threshold tuning: Lowering the decision threshold from 0.5 to increase sensitivity for critical classes. 4. Evaluation metric alignment: Relying on Macro F1 and PR-AUC instead of raw Accuracy."}
        ]),
        "formulas": "\\text{Precision} = \\frac{TP}{TP + FP}; \\text{Recall} = \\frac{TP}{TP + FN}; F_1 = 2 \\cdot \\frac{\\text{Precision} \\cdot \\text{Recall}}{\\text{Precision} + \\text{Recall}}",
        "key_takeaways": "Selecting appropriate evaluation metrics and loss functions is critical for classification integrity, especially when identifying vulnerable students in educational data.",
        "diagram_title": "Binary Classification Confusion Matrix and Core Metrics",
        "diagram_type": "Data Matrix Diagram",
        "diagram_svg": """<svg viewBox="0 0 780 250" xmlns="http://www.w3.org/2000/svg" style="background:#0f172a; border-radius:12px; font-family:sans-serif;">
  <g transform="translate(80, 30)">
    <!-- Header Labels -->
    <text x="210" y="20" fill="#f8fafc" font-size="14" font-weight="bold" text-anchor="middle">Predicted Positive</text>
    <text x="370" y="20" fill="#f8fafc" font-size="14" font-weight="bold" text-anchor="middle">Predicted Negative</text>
    
    <text x="50" y="85" fill="#f8fafc" font-size="14" font-weight="bold" text-anchor="middle">Actual Pos</text>
    <text x="50" y="165" fill="#f8fafc" font-size="14" font-weight="bold" text-anchor="middle">Actual Neg</text>

    <!-- Cells -->
    <rect x="130" y="45" width="160" height="70" rx="6" fill="#1e293b" stroke="#34d399" stroke-width="2"/>
    <text x="210" y="75" fill="#34d399" font-size="16" font-weight="bold" text-anchor="middle">True Positive (TP)</text>
    <text x="210" y="98" fill="#94a3b8" font-size="12" text-anchor="middle">Correct Detection</text>

    <rect x="290" y="45" width="160" height="70" rx="6" fill="#1e293b" stroke="#f87171" stroke-width="2"/>
    <text x="370" y="75" fill="#f87171" font-size="16" font-weight="bold" text-anchor="middle">False Negative (FN)</text>
    <text x="370" y="98" fill="#94a3b8" font-size="12" text-anchor="middle">Missed Case (Type II)</text>

    <rect x="130" y="125" width="160" height="70" rx="6" fill="#1e293b" stroke="#f87171" stroke-width="2"/>
    <text x="210" y="155" fill="#f87171" font-size="16" font-weight="bold" text-anchor="middle">False Positive (FP)</text>
    <text x="210" y="178" fill="#94a3b8" font-size="12" text-anchor="middle">False Alarm (Type I)</text>

    <rect x="290" y="125" width="160" height="70" rx="6" fill="#1e293b" stroke="#34d399" stroke-width="2"/>
    <text x="370" y="155" fill="#34d399" font-size="16" font-weight="bold" text-anchor="middle">True Negative (TN)</text>
    <text x="370" y="178" fill="#94a3b8" font-size="12" text-anchor="middle">Correct Rejection</text>
  </g>
  <text x="630" y="95" fill="#38bdf8" font-size="13" font-weight="bold">Precision = TP / (TP+FP)</text>
  <text x="630" y="135" fill="#10b981" font-size="13" font-weight="bold">Recall = TP / (TP+FN)</text>
  <text x="630" y="175" fill="#f59e0b" font-size="13" font-weight="bold">F1 = 2·(P·R) / (P+R)</text>
</svg>"""
    },
    {
        "subject": "Machine Learning",
        "unit": "Unit 3: Non-Linear Decision Trees & Impurity Metrics",
        "topic_name": "Decision Trees",
        "definition": "Decision Trees are non-parametric supervised algorithms that recursively partition feature space into axis-aligned rectangular regions using greedy impurity-reduction splits.",
        "detailed_explanation": "Decision Trees construct a top-down tree hierarchy starting from a root node. At each split, the algorithm evaluates all candidate features and split thresholds, choosing the one that maximizes Information Gain (using Entropy in ID3/C4.5) or minimizes Gini Impurity (in CART). Splitting terminates when stopping criteria are met (max_depth, min_samples_split, min_impurity_decrease). Unpruned trees easily memorize noise, resulting in deep, high-variance structures. Pre-pruning and post-pruning (Cost-Complexity Pruning, ccp_alpha) are essential to prevent catastrophic overfitting.",
        "important_points": json.dumps([
            "Gini Impurity: G = 1 - sum(p_i^2). Measures probability of incorrectly labeling a randomly chosen element.",
            "Entropy: H = -sum(p_i * log2(p_i)). Information-theoretic measure of uncertainty.",
            "Greedy top-down induction (CART) makes locally optimal choices at each node without backtracking.",
            "Cost-Complexity Pruning adds a tree size penalty (alpha * |T|) to the classification error."
        ]),
        "advantages": json.dumps([
            "Highly interpretable white-box models that mimic human deductive decision-making.",
            "Requires zero feature normalization or scaling (invariant to monotonic transformations).",
            "Naturally handles both numerical continuous features and categorical features."
        ]),
        "disadvantages": json.dumps([
            "Extremely high variance: minor variations in training data produce completely different tree structures.",
            "Prone to severe overfitting if depth is not constrained.",
            "Axis-aligned splits struggle to model smooth diagonal decision boundaries."
        ]),
        "real_world_examples": "Loan approval decision flows, medical diagnosis checklists, and initial baseline rule induction.",
        "applications": "Credit Risk Decision Trees, Diagnostic Triage, Explainable Clinical Pathways.",
        "short_questions": json.dumps([
            {"q": "What is the difference between Gini Impurity and Entropy?", "a": "Gini Impurity measures misclassification probability and avoids logarithmic computation, making it faster to compute; Entropy is an information-theoretic measure of unpredictability based on log2."},
            {"q": "What is Cost-Complexity Pruning (ccp_alpha)?", "a": "Cost-Complexity Pruning optimizes the objective function R_alpha(T) = R(T) + alpha * |T|, trading off misclassification error R(T) against tree complexity |T| to prune redundant leaf subtrees."},
            {"q": "Why are Decision Trees considered unstable?", "a": "Because greedy top-down splits at the root propagate hierarchically; a slight perturbation in training data can alter the root split, completely reconfiguring all descendant branches."}
        ]),
        "long_questions": json.dumps([
            {"q": "Explain the mathematical process of calculating Information Gain using Shannon Entropy for a binary split.", "a": "Given parent dataset D with class proportions p_i, the parent entropy is H(D) = -sum(p_i * log2(p_i)). When split on feature A into subsets D_1, D_2, ..., D_k with sizes |D_j|, the conditional entropy is H(D|A) = sum((|D_j| / |D|) * H(D_j)). Information Gain is IG(D, A) = H(D) - H(D|A). The CART or C4.5 algorithm computes IG across all possible split thresholds and selects the feature-threshold combination that maximizes IG."},
            {"q": "How does the instability and high variance of single Decision Trees motivate Ensemble methods like Random Forest?", "a": "Single decision trees are low bias, high variance estimators. Leo Breiman proved that by taking the average of B independent, identically distributed random variables each with variance \\sigma^2, the variance of the average drops to \\sigma^2 / B. Random Forest achieves this by generating hundreds of de-correlated decision trees trained on bootstrap samples with random feature subsets, dramatically reducing variance while preserving low bias."}
        ]),
        "formulas": "\\text{Entropy: } H(S) = -\\sum_{i=1}^C p_i \\log_2(p_i); \\quad \\text{Gini: } G(S) = 1 - \\sum_{i=1}^C p_i^2; \\quad \\text{IG} = H(S) - \\sum \\frac{|S_v|}{|S|} H(S_v)",
        "key_takeaways": "Decision Trees provide foundational split logic and impurity reduction concepts that directly power advanced ensemble architectures like Random Forests and LightGBM.",
        "diagram_title": "Binary Recursive Decision Tree Splitting Structure",
        "diagram_type": "Hierarchical Tree Diagram",
        "diagram_svg": """<svg viewBox="0 0 780 250" xmlns="http://www.w3.org/2000/svg" style="background:#0f172a; border-radius:12px; font-family:sans-serif;">
  <!-- Root Node -->
  <rect x="300" y="20" width="180" height="50" rx="8" fill="#1e293b" stroke="#6366f1" stroke-width="2"/>
  <text x="390" y="42" fill="#f8fafc" font-size="13" font-weight="bold" text-anchor="middle">Quiz Score &lt;= 50%?</text>
  <text x="390" y="60" fill="#6366f1" font-size="11" text-anchor="middle">Gini = 0.48 | N = 3600</text>

  <!-- Left Branch -->
  <path d="M 330 70 L 210 115" stroke="#f87171" stroke-width="2"/>
  <text x="250" y="90" fill="#f87171" font-size="11" font-weight="bold">Yes</text>

  <!-- Right Branch -->
  <path d="M 450 70 L 570 115" stroke="#34d399" stroke-width="2"/>
  <text x="525" y="90" fill="#34d399" font-size="11" font-weight="bold">No</text>

  <!-- Internal Node Left -->
  <rect x="120" y="115" width="180" height="50" rx="8" fill="#1e293b" stroke="#f59e0b" stroke-width="2"/>
  <text x="210" y="137" fill="#f8fafc" font-size="13" font-weight="bold" text-anchor="middle">Attendance &lt;= 60%?</text>
  <text x="210" y="155" fill="#f59e0b" font-size="11" text-anchor="middle">Gini = 0.38 | N = 1200</text>

  <!-- Internal Node Right -->
  <rect x="480" y="115" width="180" height="50" rx="8" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
  <text x="570" y="137" fill="#f8fafc" font-size="13" font-weight="bold" text-anchor="middle">Topic Gap &gt;= 25%?</text>
  <text x="570" y="155" fill="#38bdf8" font-size="11" text-anchor="middle">Gini = 0.22 | N = 2400</text>

  <!-- Terminal Leaves -->
  <rect x="40" y="195" width="140" height="40" rx="6" fill="#1e293b" stroke="#ef4444" stroke-width="2"/>
  <text x="110" y="220" fill="#ef4444" font-size="13" font-weight="bold" text-anchor="middle">High Gap (Leaf)</text>

  <rect x="220" y="195" width="140" height="40" rx="6" fill="#1e293b" stroke="#f59e0b" stroke-width="2"/>
  <text x="290" y="220" fill="#f59e0b" font-size="13" font-weight="bold" text-anchor="middle">Med Gap (Leaf)</text>

  <rect x="420" y="195" width="140" height="40" rx="6" fill="#1e293b" stroke="#fbbf24" stroke-width="2"/>
  <text x="490" y="220" fill="#fbbf24" font-size="13" font-weight="bold" text-anchor="middle">Hidden Gap (Leaf)</text>

  <rect x="600" y="195" width="140" height="40" rx="6" fill="#1e293b" stroke="#10b981" stroke-width="2"/>
  <text x="670" y="220" fill="#10b981" font-size="13" font-weight="bold" text-anchor="middle">Low Gap (Leaf)</text>
</svg>"""
    },
    {
        "subject": "Machine Learning",
        "unit": "Unit 4: Ensemble Learning & Bagging",
        "topic_name": "Random Forest",
        "definition": "Random Forest is an ensemble learning algorithm that builds a forest of diverse, de-correlated decision trees using bootstrap aggregating (bagging) and random feature subspace sampling.",
        "detailed_explanation": "Random Forest trains B distinct decision trees. Each tree is trained on an independent bootstrap sample of size N drawn with replacement from the training set (approximately 63.2% unique records; remaining 36.8% form the Out-of-Bag, OOB, validation set). At each node split, only a random subset of features m = sqrt(D) is considered, de-correlating the trees. Final predictions are aggregated via majority voting (classification) or arithmetic averaging (regression). Feature importance is measured via Mean Decrease in Impurity (MDI) or Out-of-Bag Permutation Feature Importance.",
        "important_points": json.dumps([
            "Bootstrap Aggregation (Bagging): Reduces variance by averaging multiple uncorrelated decision trees.",
            "Feature Subspace Randomization: Selects sqrt(D) features per split to avoid dominant features driving all trees.",
            "Out-of-Bag (OOB) Error: Free validation metric computed using samples left out of each tree's bootstrap draw.",
            "Highly parallelizable: Individual trees train completely independently across multi-core processors."
        ]),
        "advantages": json.dumps([
            "Significantly lower variance and higher generalization accuracy than individual decision trees.",
            "Resistant to overfitting due to the Strong Law of Large Numbers as number of trees grows.",
            "Provides built-in Out-of-Bag (OOB) error estimates without requiring a separate validation split."
        ]),
        "disadvantages": json.dumps([
            "Computationally demanding with large memory footprints compared to simple linear models.",
            "Loss of direct interpretability (black-box ensemble requiring SHAP or permutation metrics to explain).",
            "Slow inference latency on memory-constrained embedded edge devices."
        ]),
        "real_world_examples": "Customer churn prediction, medical diagnosis classification, credit card fraud detection, and educational risk scoring.",
        "applications": "Academic Performance Modeling, Risk Analysis, Genomics, Financial Churn Prediction.",
        "short_questions": json.dumps([
            {"q": "What is Out-of-Bag (OOB) error in Random Forest?", "a": "OOB error is the mean prediction error evaluated on observations that were not included in the bootstrap sample of a given tree (approximately 36.8% of the dataset per tree)."},
            {"q": "Why does Random Forest select a random subset of features at each split?", "a": "Random feature selection prevents a few dominant features from being chosen at the root of every tree, ensuring the trees remain diverse and de-correlated."},
            {"q": "How does Random Forest perform multi-class classification aggregation?", "a": "Each tree outputs a discrete class prediction; the final ensemble prediction is determined by majority vote across all trees."}
        ]),
        "long_questions": json.dumps([
            {"q": "Analyze why ensemble averaging in Random Forest reduces variance without increasing bias.", "a": "Let X_1, X_2, ..., X_B be predictions from B individual trees, each with variance \\sigma^2 and pairwise correlation \\rho. The variance of the ensemble average is Var((1/B) * sum(X_i)) = \\rho * \\sigma^2 + ((1 - \\rho) / B) * \\sigma^2. As B approaches infinity, the second term approaches zero, leaving \\rho * \\sigma^2. By injecting two levels of randomness (bootstrap sampling and random feature subsets m = sqrt(D)), Random Forest minimizes the correlation \\rho, driving total ensemble variance far below individual tree variance while maintaining low individual bias."},
            {"q": "Compare Random Forest with Gradient Boosted Trees (LightGBM) in terms of architecture, training mechanics, and performance.", "a": "Random Forest is a bagging ensemble where deep trees are trained independently in parallel to reduce variance. Gradient Boosted Trees (like LightGBM) are boosting ensembles where shallow trees are trained sequentially to iteratively reduce residual errors (minimizing bias). LightGBM uses leaf-wise splitting, Gradient-based One-Side Sampling (GOSS), and Exclusive Feature Bundling (EFB), achieving higher accuracy and faster training on tabular data compared to standard Random Forest."}
        ]),
        "formulas": "\\text{Ensemble Variance: } \\text{Var}(\\bar{X}) = \\rho \\sigma^2 + \\frac{1-\\rho}{B}\\sigma^2; \\quad m = \\sqrt{D} \\text{ (Classification)}, \\quad m = \\frac{D}{3} \\text{ (Regression)}",
        "key_takeaways": "Random Forest provides a robust, non-linear ensemble benchmark that effectively balances variance reduction, forming the primary baseline comparison against EduGap AI's proposed TAT-KG hybrid model.",
        "diagram_title": "Random Forest Architecture: Bagging and Aggregation Pipeline",
        "diagram_type": "Model Architecture Diagram",
        "diagram_svg": """<svg viewBox="0 0 780 260" xmlns="http://www.w3.org/2000/svg" style="background:#0f172a; border-radius:12px; font-family:sans-serif;">
  <!-- Dataset -->
  <rect x="310" y="15" width="160" height="40" rx="6" fill="#1e293b" stroke="#f8fafc" stroke-width="2"/>
  <text x="390" y="40" fill="#f8fafc" font-size="13" font-weight="bold" text-anchor="middle">Original Dataset (N, D)</text>

  <!-- Distribution Lines -->
  <path d="M 340 55 L 140 100" stroke="#64748b" stroke-width="2"/>
  <path d="M 390 55 L 390 100" stroke="#64748b" stroke-width="2"/>
  <path d="M 440 55 L 640 100" stroke="#64748b" stroke-width="2"/>

  <!-- Bootstrap Samples and Trees -->
  <g transform="translate(60, 100)">
    <rect x="0" y="0" width="160" height="70" rx="8" fill="#1e293b" stroke="#6366f1" stroke-width="2"/>
    <text x="80" y="25" fill="#6366f1" font-size="12" font-weight="bold" text-anchor="middle">Tree 1 (Bootstrap 1)</text>
    <text x="80" y="45" fill="#94a3b8" font-size="11" text-anchor="middle">Subspace: sqrt(D)</text>
    <text x="80" y="62" fill="#34d399" font-size="11" font-weight="bold" text-anchor="middle">Vote: Low Gap</text>
  </g>

  <g transform="translate(310, 100)">
    <rect x="0" y="0" width="160" height="70" rx="8" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
    <text x="80" y="25" fill="#38bdf8" font-size="12" font-weight="bold" text-anchor="middle">Tree 2 (Bootstrap 2)</text>
    <text x="80" y="45" fill="#94a3b8" font-size="11" text-anchor="middle">Subspace: sqrt(D)</text>
    <text x="80" y="62" fill="#34d399" font-size="11" font-weight="bold" text-anchor="middle">Vote: Low Gap</text>
  </g>

  <g transform="translate(560, 100)">
    <rect x="0" y="0" width="160" height="70" rx="8" fill="#1e293b" stroke="#f59e0b" stroke-width="2"/>
    <text x="80" y="25" fill="#f59e0b" font-size="12" font-weight="bold" text-anchor="middle">Tree B (Bootstrap B)</text>
    <text x="80" y="45" fill="#94a3b8" font-size="11" text-anchor="middle">Subspace: sqrt(D)</text>
    <text x="80" y="62" fill="#f87171" font-size="11" font-weight="bold" text-anchor="middle">Vote: High Gap</text>
  </g>

  <!-- Convergence to Majority Vote -->
  <path d="M 140 170 L 340 215" stroke="#64748b" stroke-width="2"/>
  <path d="M 390 170 L 390 215" stroke="#64748b" stroke-width="2"/>
  <path d="M 640 170 L 440 215" stroke="#64748b" stroke-width="2"/>

  <rect x="290" y="215" width="200" height="35" rx="6" fill="#1e293b" stroke="#34d399" stroke-width="2"/>
  <text x="390" y="238" fill="#34d399" font-size="13" font-weight="bold" text-anchor="middle">Majority Vote Aggregation</text>
</svg>"""
    },
    {
        "subject": "Machine Learning",
        "unit": "Unit 5: Unsupervised Clustering & Centroid Optimization",
        "topic_name": "K-Means",
        "definition": "K-Means is an unsupervised vector quantization algorithm that partitions N observations into K distinct clusters where each point belongs to the cluster with the nearest mean centroid.",
        "detailed_explanation": "K-Means operates by minimizing the Within-Cluster Sum of Squares (WCSS), also called inertia. The algorithm alternates between two steps: 1. Assignment Step (assign each observation x_i to the nearest centroid mu_k using Euclidean distance), and 2. Update Step (recompute centroids mu_k as the mean of all points assigned to cluster k). Iteration terminates when centroids stabilize. The standard heuristic for selecting optimal K is the Elbow Method or Silhouette Analysis. Standard K-Means is sensitive to initialization; K-Means++ resolves this by initializing centroids with probability proportional to squared distance from existing centers.",
        "important_points": json.dumps([
            "Objective: Minimize WCSS = sum_{k=1}^K sum_{x in S_k} ||x - mu_k||^2.",
            "K-Means++ initialization drastically speeds up convergence and avoids suboptimal local minima.",
            "Requires mandatory feature scaling (StandardScaler) because Euclidean distance is distorted by differing feature magnitudes.",
            "Silhouette Score ranges from -1 to +1, measuring intra-cluster cohesion vs inter-cluster separation."
        ]),
        "advantages": json.dumps([
            "Linear time complexity per iteration: O(N * K * D * I), scaling efficiently to large datasets.",
            "Simple, intuitive geometric clustering logic easily interpretable by academic monitors.",
            "Guaranteed convergence to a local minimum."
        ]),
        "disadvantages": json.dumps([
            "Requires specifying the number of clusters K a priori.",
            "Assumes spherical, isotropic clusters of similar sizes and densities (fails on non-convex manifolds).",
            "Extremely sensitive to outliers which drag cluster centroids away from true dense cores."
        ]),
        "real_world_examples": "Student engagement persona clustering in EduGap AI (4 personas), customer market segmentation, and image color quantization.",
        "applications": "Learner Persona Profiling, Market Segmentation, Anomaly Detection, Document Categorization.",
        "short_questions": json.dumps([
            {"q": "What is the mathematical objective function of K-Means?", "a": "K-Means minimizes the Within-Cluster Sum of Squares (WCSS / Inertia): J = \\sum_{k=1}^K \\sum_{x \\in S_k} \\|x - \\mu_k\\|^2."},
            {"q": "How does K-Means++ improve over standard random initialization?", "a": "K-Means++ selects the first centroid uniformly at random, then chooses subsequent centroids with probability proportional to the squared Euclidean distance to the nearest existing centroid, spreading centers across the feature space."},
            {"q": "How is the Silhouette Coefficient interpreted?", "a": "A score close to +1 indicates well-clustered instances far from neighboring clusters; 0 indicates overlapping cluster boundaries; negative values indicate misassigned points."}
        ]),
        "long_questions": json.dumps([
            {"q": "Describe the two alternating steps of Lloyd's K-Means algorithm and prove why the objective function is guaranteed to decrease monotonically.", "a": "1. Expectation (Assignment): Holding centroids \\mu_k fixed, each point x_i is assigned to cluster S_k minimizing ||x_i - \\mu_k||^2. This step minimizes the cost function J with respect to assignment indicators. 2. Maximization (Update): Holding assignments fixed, new centroids \\mu_k are set to the arithmetic mean of points in S_k. Differentiating J with respect to \\mu_k and setting to zero confirms the mean minimizes sum of squared Euclidean distances. Since each step strictly decreases or keeps constant the finite positive objective function J, the algorithm is guaranteed to converge to a local optimum in a finite number of iterations."},
            {"q": "Explain how EduGap AI uses K-Means to identify student behavioral personas without using it for learning gap classification.", "a": "In EduGap AI, K-Means is used as an unsupervised diagnostic tool to segment students into 4 behavioral archetypes: 1. High-Performing and Highly Engaged, 2. Consistent Learner, 3. High-Potential Disengaged Learner, 4. At-Risk Disengaged Learner. Fused features (attendance, login frequency, inactivity days, assignment score) are scaled with StandardScaler. The system explicitly reserves supervised LightGBM for topic gap classification, using K-Means to provide contextual engagement insight to mentors."}
        ]),
        "formulas": "\\text{WCSS} = \\sum_{k=1}^K \\sum_{x_i \\in S_k} \\|x_i - \\mu_k\\|^2; \\quad \\mu_k = \\frac{1}{|S_k|} \\sum_{x_i \\in S_k} x_i; \\quad s(i) = \\frac{b(i) - a(i)}{\\max(a(i), b(i))}",
        "key_takeaways": "K-Means provides robust behavioral segmentation to help academic advisors understand whether student difficulties stem from concept confusion or systemic disengagement.",
        "diagram_title": "K-Means Iterative Centroid Convergence Process",
        "diagram_type": "Process Diagram",
        "diagram_svg": """<svg viewBox="0 0 780 240" xmlns="http://www.w3.org/2000/svg" style="background:#0f172a; border-radius:12px; font-family:sans-serif;">
  <g transform="translate(40, 30)">
    <rect x="0" y="20" width="180" height="150" rx="8" fill="#1e293b" stroke="#6366f1" stroke-width="2"/>
    <text x="90" y="50" fill="#f8fafc" font-size="14" font-weight="bold" text-anchor="middle">1. Initialization</text>
    <circle cx="50" cy="90" r="6" fill="#38bdf8"/>
    <circle cx="80" cy="120" r="6" fill="#38bdf8"/>
    <circle cx="130" cy="80" r="6" fill="#f87171"/>
    <circle cx="140" cy="130" r="6" fill="#f87171"/>
    <polygon points="65,100 75,80 85,100" fill="#f59e0b"/>
    <polygon points="125,110 135,90 145,110" fill="#10b981"/>
    <text x="90" y="155" fill="#94a3b8" font-size="11" text-anchor="middle">K-Means++ Initial Centroids</text>
  </g>

  <path d="M 230 115 L 280 115" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>

  <g transform="translate(290, 30)">
    <rect x="0" y="20" width="180" height="150" rx="8" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
    <text x="90" y="50" fill="#f8fafc" font-size="14" font-weight="bold" text-anchor="middle">2. Assignment</text>
    <circle cx="50" cy="90" r="6" fill="#f59e0b"/>
    <circle cx="80" cy="120" r="6" fill="#f59e0b"/>
    <circle cx="130" cy="80" r="6" fill="#10b981"/>
    <circle cx="140" cy="130" r="6" fill="#10b981"/>
    <text x="90" y="155" fill="#94a3b8" font-size="11" text-anchor="middle">Assign to Nearest Center</text>
  </g>

  <path d="M 480 115 L 530 115" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>

  <g transform="translate(540, 30)">
    <rect x="0" y="20" width="180" height="150" rx="8" fill="#1e293b" stroke="#10b981" stroke-width="2"/>
    <text x="90" y="50" fill="#f8fafc" font-size="14" font-weight="bold" text-anchor="middle">3. Update Centroids</text>
    <polygon points="60,110 70,90 80,110" fill="#f59e0b"/>
    <polygon points="130,115 140,95 150,115" fill="#10b981"/>
    <text x="90" y="155" fill="#34d399" font-size="11" font-weight="bold" text-anchor="middle">Recompute Mean Centers</text>
  </g>
</svg>"""
    },
    {
        "subject": "Data Science & Mathematics",
        "unit": "Unit 3: Dimensionality Reduction & Linear Algebra",
        "topic_name": "PCA",
        "definition": "Principal Component Analysis (PCA) is an orthogonal linear transformation technique that projects data onto a lower-dimensional coordinate system that maximizes feature variance.",
        "detailed_explanation": "PCA identifies principal axes of maximal variance by computing the eigenvectors and eigenvalues of the empirical data covariance matrix Sigma = (1/N) * X^T X (after zero-centering and feature scaling). The first principal component (PC1) accounts for the largest possible variance; each succeeding component is orthogonal (uncorrelated) to the preceding components and accounts for the next highest variance. Selecting the top k components preserves the maximum signal while dropping noisy, redundant dimensions. Singular Value Decomposition (SVD) of X = U * Sigma * V^T is computationally preferred over explicit covariance matrix inversion.",
        "important_points": json.dumps([
            "Unsupervised technique: PCA finds directions of maximum variance without utilizing target labels.",
            "Pre-requisite: Mandatory mean centering and standard deviation unit-variance scaling (Z-score).",
            "Eigenvalues represent the amount of variance explained by their corresponding eigenvector axis.",
            "Explained Variance Ratio: Evaluates cumulative variance explained to choose optimal k (e.g., retaining 95% total variance)."
        ]),
        "advantages": json.dumps([
            "Mitigates the Curse of Dimensionality, reducing computational cost and memory footprints.",
            "Eliminates multicollinearity by creating mutually orthogonal, uncorrelated features.",
            "Enables 2D and 3D visualization of high-dimensional student activity telemetry."
        ]),
        "disadvantages": json.dumps([
            "Loss of direct feature interpretability: Principal components are linear combinations of all original features.",
            "Linear assumption: Fails to capture non-linear manifold structures (where t-SNE or UMAP is needed).",
            "Sensitive to outliers which artificially inflate covariance matrix estimates."
        ]),
        "real_world_examples": "Facial recognition (Eigenfaces), 2D visualization of complex student activity metrics, and noise filtering in financial data.",
        "applications": "Exploratory Data Visualization, Genomic Compression, Multicollinearity Mitigation, Computer Vision.",
        "short_questions": json.dumps([
            {"q": "Why is feature scaling mandatory prior to applying PCA?", "a": "PCA maximizes variance; features with arbitrarily large numerical scales (e.g., income in thousands) would dominate the principal components over features with small scales (e.g., age in decades)."},
            {"q": "What is the relationship between PCA and Singular Value Decomposition (SVD)?", "a": "SVD factorizes X into U * \\Sigma * V^T. The right singular vectors V are exactly the eigenvectors of the covariance matrix X^T X, avoiding explicit O(D^2) covariance matrix formation."},
            {"q": "What does the scree plot show in PCA?", "a": "A scree plot displays eigenvalues or explained variance ratios against component index, enabling analysts to identify the 'elbow' where additional components yield diminishing returns."}
        ]),
        "long_questions": json.dumps([
            {"q": "Derive the first principal component mathematically using Lagrange multipliers to maximize projected variance.", "a": "Let X be zero-centered data with covariance matrix \\Sigma = (1/N) * X^T X. The projection of a data point onto unit vector w is w^T x, with projected variance w^T \\Sigma w. We seek to maximize w^T \\Sigma w subject to the unit length constraint w^T w = 1. Constructing the Lagrangian: L(w, \\lambda) = w^T \\Sigma w - \\lambda (w^T w - 1). Taking the gradient with respect to w and setting to zero: dL/dw = 2 \\Sigma w - 2 \\lambda w = 0 => \\Sigma w = \\lambda w. This is the characteristic eigenvector equation: w must be an eigenvector of \\Sigma, and the variance w^T \\Sigma w = w^T (\\lambda w) = \\lambda is maximized when w is the eigenvector corresponding to the largest eigenvalue \\lambda_1."},
            {"q": "Discuss the difference between Dimensionality Reduction via Feature Selection versus Feature Extraction.", "a": "Feature Selection (e.g., Lasso L1 regularization, Recursive Feature Elimination, or Random Forest MDI) keeps a subset of the original features intact, preserving physical interpretability. Feature Extraction (e.g., PCA, t-SNE, Autoencoders) projects data into a completely new latent coordinate space, creating composite features that synthesize information across multiple original variables but sacrifice original semantic names."}
        ]),
        "formulas": "\\text{Covariance: } \\Sigma = \\frac{1}{N} X^T X; \\quad \\Sigma v = \\lambda v; \\quad \\text{Explained Variance Ratio: } \\frac{\\lambda_i}{\\sum_{j=1}^D \\lambda_j}",
        "key_takeaways": "PCA demonstrates the power of linear algebra in transforming noisy, correlated multi-dimensional educational features into compact, orthogonal predictive components.",
        "diagram_title": "Orthogonal Principal Axes of Maximal Variance",
        "diagram_type": "Data Coordinate Diagram",
        "diagram_svg": """<svg viewBox="0 0 780 240" xmlns="http://www.w3.org/2000/svg" style="background:#0f172a; border-radius:12px; font-family:sans-serif;">
  <line x1="80" y1="210" x2="720" y2="210" stroke="#64748b" stroke-width="1.5"/>
  <line x1="80" y1="210" x2="80" y2="30" stroke="#64748b" stroke-width="1.5"/>
  <text x="730" y="215" fill="#94a3b8" font-size="12">Feature 1</text>
  <text x="75" y="20" fill="#94a3b8" font-size="12">Feature 2</text>

  <!-- Correlated Ellipse Cloud -->
  <g fill="#38bdf8" opacity="0.65">
    <circle cx="220" cy="170" r="5"/>
    <circle cx="260" cy="155" r="5"/>
    <circle cx="310" cy="140" r="5"/>
    <circle cx="350" cy="130" r="5"/>
    <circle cx="390" cy="115" r="5"/>
    <circle cx="430" cy="100" r="5"/>
    <circle cx="470" cy="85" r="5"/>
    <circle cx="510" cy="70" r="5"/>
    <circle cx="550" cy="60" r="5"/>
    <circle cx="360" cy="145" r="5"/>
    <circle cx="420" cy="80" r="5"/>
  </g>

  <!-- PC1 Axis -->
  <line x1="160" y1="195" x2="600" y2="40" stroke="#6366f1" stroke-width="3.5"/>
  <text x="615" y="45" fill="#6366f1" font-size="14" font-weight="bold">PC 1 (Max Variance, λ_1)</text>

  <!-- PC2 Axis (Orthogonal) -->
  <line x1="330" y1="50" x2="450" y2="185" stroke="#f59e0b" stroke-width="2.5" stroke-dasharray="4"/>
  <text x="460" y="195" fill="#f59e0b" font-size="13" font-weight="bold">PC 2 (Orthogonal, λ_2)</text>

  <rect x="250" y="10" width="280" height="30" rx="5" fill="#1e293b" stroke="#6366f1" stroke-width="1.5"/>
  <text x="390" y="30" fill="#f8fafc" font-size="12" font-weight="bold" text-anchor="middle">Orthogonal Projection Maximizes Spread</text>
</svg>"""
    }
]


def seed_theory_materials():
    print(f"[Theory] Seeding theory materials to {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for item in THEORY_DATA:
        cursor.execute("""
            INSERT INTO theory_materials (
                subject, unit, topic_name, definition, detailed_explanation,
                important_points, advantages, disadvantages, real_world_examples,
                applications, short_questions, long_questions, formulas, key_takeaways,
                diagram_svg, diagram_title, diagram_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(topic_name) DO UPDATE SET
                subject = excluded.subject,
                unit = excluded.unit,
                definition = excluded.definition,
                detailed_explanation = excluded.detailed_explanation,
                important_points = excluded.important_points,
                advantages = excluded.advantages,
                disadvantages = excluded.disadvantages,
                real_world_examples = excluded.real_world_examples,
                applications = excluded.applications,
                short_questions = excluded.short_questions,
                long_questions = excluded.long_questions,
                formulas = excluded.formulas,
                key_takeaways = excluded.key_takeaways,
                diagram_svg = excluded.diagram_svg,
                diagram_title = excluded.diagram_title,
                diagram_type = excluded.diagram_type
        """, (
            item["subject"], item["unit"], item["topic_name"], item["definition"], item["detailed_explanation"],
            item["important_points"], item["advantages"], item["disadvantages"], item["real_world_examples"],
            item["applications"], item["short_questions"], item["long_questions"], item["formulas"], item["key_takeaways"],
            item["diagram_svg"], item["diagram_title"], item["diagram_type"]
        ))
        print(f"  [Seeded] {item['topic_name']} ({item['subject']})")

    conn.commit()
    conn.close()
    print("[Theory] Successfully seeded all 12 curriculum theory modules!")


if __name__ == "__main__":
    seed_theory_materials()
