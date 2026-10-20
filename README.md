# EduGap AI - AI-Driven Learning-Gap Detection & Proctored Assessment Platform

An enterprise academic intelligence platform engineered to identify topic-level student learning gaps, provide personalized administrator guidance, administer browser-proctored online examinations, and recommend targeted YouTube learning videos.

---

## 1. System Architecture & Two-Role Model

EduGap AI strictly operates with **two distinct roles**:

1. **Admin (Administrator, Academic Monitor, Evaluator, and Student Guide)**
   - Monitors institutional performance, AI-calculated learning gaps, and machine learning risk predictions.
   - Manages the student registry: creates, activates, and edits student profiles.
   - Personally guides any student by publishing study plans, revision topics, and improvement goals directly to their portal.
   - Creates and schedules examinations (supporting MCQ, True/False, Multiple-Select, and Subjective questions) with customizable durations, pass marks, negative marking, question/option shuffling, and proctoring.
   - Evaluates subjective candidate submissions, awards marks, and publishes feedback.
   - Reviews proctoring logs and integrity alerts (tab switches, webcam/face alerts, window blur, and copy/paste restrictions).
   - Manages and assigns topic-tagged YouTube educational videos.

2. **Student (Learner & Examinee)**
   - Views personal academic standing, detected topic-level gaps, and AI recommendations.
   - Receives personalized administrator guidance and target improvement goals.
   - Takes assigned proctored examinations with automated timers, continuous autosave, and webcam presence verification.
   - Accesses assigned assignments and adaptive quizzes.
   - Directly watches recommended YouTube learning videos matching their weak topics.
   - Protected by strict authorization barriers (students cannot access administrative routes or other students' private records).

---

## 2. Core Enhancements Implemented

- **Database Schemas**:
  - `youtube_resources`: Topic/subject-tagged educational video library with validated YouTube URLs.
  - `student_guidance`: Personalized academic guidance, goals, and practice directives authored by Admin.
  - `assessments` & `assessment_questions`: Timed tests with objective and subjective questions, negative marking, attempt limits, and proctoring toggles.
  - `assessment_attempts` & `assessment_answers`: Student attempt lifecycle, score tracking, objective auto-grading, and subjective evaluator scoring.
  - `proctoring_logs`: Event-level security logging (face detection status, tab-switch, window blur, copy/paste attempts).
- **Proctored Examination Engine**:
  - Pre-exam integrity verification & consent checklist.
  - Synchronized countdown timer with automatic server-side submission on expiry.
  - Continuous background autosave preventing work loss.
  - Browser-based proctoring with live camera presence monitoring, tab-switch interception, and clipboard copy/paste restrictions.
- **YouTube Learning Link Integration**:
  - Topic-to-video recommendation engine connecting identified student learning gaps (`learning_gap_score >= 30%`) to relevant YouTube video lectures.
  - Secure external links opening in new browser tabs with thumbnail previews and learning objectives.

---

## 3. Setup & Execution Instructions

### Prerequisites
- Python 3.10+
- SQLite3
- Modern web browser (Chrome, Edge, Firefox) with webcam permission enabled for proctored testing

### Quick Start

1. **Install Dependencies**:
   ```bash
   pip install flask werkzeug joblib scikit-learn pandas numpy shap
   ```

2. **Run Database Migrations & Seed Data**:
   ```bash
   python src/migrate_enhancements.py
   python src/seed_enhancements.py
   ```

3. **Launch the Application Server**:
   ```bash
   python app.py
   ```
   Open your browser and navigate to: `http://127.0.0.1:5000`

---

## 4. Default Credentials

- **Admin Account**:
  - Username: `admin`
  - Password: `admin123`
- **Student Account**:
  - Username: `swathi`
  - Password: `password123`
- **Alternative Student Account**:
  - Username: `dev`
  - Password: `password123`

---

## 5. Automated Validation & Verification

Run the full end-to-end integration and workflow validation test suite:
```bash
python test_full_enhancements.py
python test_production.py
```
Both test suites verify 100% route health, role authorization restrictions, zero emojis, ML prediction integrity, proctored test autosave, proctoring security logging, and evaluation workflows.
