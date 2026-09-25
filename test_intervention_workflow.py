import requests
import sqlite3

BASE_URL = "http://127.0.0.1:5000"

def test_full_workflow():
    session_admin = requests.Session()
    session_mentor = requests.Session()
    session_student = requests.Session()

    print("--- STEP 1: Log in Admin ---")
    resp = session_admin.post(f"{BASE_URL}/login", data={"username": "admin", "password": "admin123"}, allow_redirects=True)
    assert resp.status_code == 200, f"Admin login failed: {resp.status_code}"
    print("Admin logged in successfully.")

    print("\n--- STEP 2: View Interventions as Admin ---")
    resp = session_admin.get(f"{BASE_URL}/interventions")
    assert resp.status_code == 200
    assert "Active Student Intervention Directory" in resp.text
    print("Admin interventions directory loaded.")

    print("\n--- STEP 3: Create Intervention for Student S005 (Dev Das) ---")
    create_data = {
        "student_id": "S005",
        "intervention_type": "Academic Counselling",
        "reason": "Attendance recovery and structured daily scheduling following absence period.",
        "ai_recommendation": "Weekly schedule check-in and task calendar milestones.",
        "mentor_id": ""  # Initially no mentor assigned -> Pending
    }
    resp = session_admin.post(f"{BASE_URL}/interventions/create", data=create_data, allow_redirects=True)
    assert resp.status_code == 200
    print("Intervention created.")

    # Get the newly created intervention id from DB
    conn = sqlite3.connect("database/learning_gap.db")
    c = conn.cursor()
    c.execute("SELECT id, student_id, status, mentor_name, progress_pct FROM interventions WHERE student_id='S005' ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    assert row is not None, "Intervention not found in DB"
    intervention_id, student_id, status, mentor_name, progress_pct = row
    print(f"Created Intervention ID: {intervention_id}, Student: {student_id}, Status: {status}, Mentor: {mentor_name}, Progress: {progress_pct}%")

    print("\n--- STEP 4: Admin assigns mentor Dr. Sarah Jenkins (mentor_id=1) ---")
    assign_data = {
        "mentor_id": 1
    }
    resp = session_admin.post(f"{BASE_URL}/interventions/assign-mentor/{intervention_id}", data=assign_data, allow_redirects=True)
    assert resp.status_code == 200
    print("Mentor assigned.")

    # Check database for mentor assignment record
    conn = sqlite3.connect("database/learning_gap.db")
    c = conn.cursor()
    c.execute("SELECT id, student_id, status, mentor_name, progress_pct, mentor_id FROM interventions WHERE id=?", (intervention_id,))
    row = c.fetchone()
    c.execute("SELECT id, intervention_id, student_id, mentor_id, mentor_name, assigned_by FROM mentor_assignments WHERE intervention_id=?", (intervention_id,))
    assignment_row = c.fetchone()
    conn.close()
    assert row[3] == "Dr. Sarah Jenkins", f"Expected Dr. Sarah Jenkins, got {row[3]}"
    assert assignment_row is not None, "No record in mentor_assignments table"
    print(f"Verified DB: Intervention {intervention_id} assigned to {row[3]} with status {row[2]}. Assignment log verified: {assignment_row}")

    print("\n--- STEP 5: Mentor (Dr. Sarah Jenkins) logs in ---")
    resp = session_mentor.post(f"{BASE_URL}/login", data={"username": "dr_sarah", "password": "mentor123"}, allow_redirects=True)
    assert resp.status_code == 200
    print("Mentor logged in successfully.")

    resp = session_mentor.get(f"{BASE_URL}/interventions")
    assert resp.status_code == 200
    assert "Dev Das" in resp.text, "Dev Das not visible in Mentor's assigned view"
    assert "My Assigned Students" in resp.text or "Active Student Intervention Directory" in resp.text
    print("Mentor sees Dev Das in assigned students.")

    print("\n--- STEP 6: Student (Dev Das) logs in ---")
    resp = session_student.post(f"{BASE_URL}/login", data={"username": "dev", "password": "password123"}, allow_redirects=True)
    assert resp.status_code == 200
    print("Dev Das logged in successfully.")

    resp = session_student.get(f"{BASE_URL}/interventions")
    assert resp.status_code == 200
    assert "Dev Das" in resp.text or "My Academic Intervention" in resp.text or "S005" in resp.text
    assert "Dr. Sarah Jenkins" in resp.text, "Student cannot see assigned mentor name"
    assert "Assign Mentor" not in resp.text, "Student should not have Assign Mentor action"
    assert "Create Intervention" not in resp.text, "Student should not have Create Intervention action"
    print("Dev Das sees their intervention and Dr. Sarah Jenkins with no unauthorized controls.")

    print("\n--- STEP 7: Mentor updates progress to 65% with clinical notes ---")
    progress_data = {
        "progress_pct": 65,
        "mentor_notes": "First check-in session completed. Action plan established for attendance and homework milestones."
    }
    resp = session_mentor.post(f"{BASE_URL}/interventions/update-progress/{intervention_id}", data=progress_data, allow_redirects=True)
    assert resp.status_code == 200
    print("Progress updated to 65%.")

    print("\n--- STEP 8: Mark Intervention Resolved ---")
    resp = session_admin.post(f"{BASE_URL}/interventions/resolve/{intervention_id}", allow_redirects=True)
    assert resp.status_code == 200

    conn = sqlite3.connect("database/learning_gap.db")
    c = conn.cursor()
    c.execute("SELECT status, progress_pct FROM interventions WHERE id=?", (intervention_id,))
    row = c.fetchone()
    conn.close()
    assert row[0] == "Resolved"
    assert row[1] == 100
    print(f"Intervention {intervention_id} successfully marked Resolved with {row[1]}% progress.")

    print("\nALL WORKFLOW STEPS VALIDATED SUCCESSFULLY!")

if __name__ == "__main__":
    test_full_workflow()
