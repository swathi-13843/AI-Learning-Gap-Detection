import pandas as pd
import joblib
from pathlib import Path


# Load the trained model
model_file = Path("models/risk_model.pkl")
model = joblib.load(model_file)


# Create sample student activity data
new_student = pd.DataFrame([{
    "quiz_score": 45,
    "assignment_score": 50,
    "attendance": 70,
    "videos_watched": 3,
    "lessons_completed": 4,
    "login_frequency": 2,
    "days_inactive": 10,
    "previous_topic_score": 48,
    "engagement_score": 45
}])


# Predict the student's risk category
prediction = model.predict(new_student)

print("Student activity data:")
print(new_student)

print("\nPredicted learning risk:", prediction[0])


# Display prediction probabilities
probabilities = model.predict_proba(new_student)[0]
classes = model.classes_

print("\nPrediction probabilities:")

for class_name, probability in zip(classes, probabilities):
    print(f"{class_name}: {probability * 100:.2f}%")