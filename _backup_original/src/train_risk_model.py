import pandas as pd
import joblib

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report


# Load the processed dataset
input_file = Path(
    "data/processed/engineered_student_activity.csv"
)

df = pd.read_csv(input_file)


# Create the target variable
def classify_risk(score):
    if score >= 60:
        return "High Risk"
    elif score >= 30:
        return "Medium Risk"
    else:
        return "Low Risk"


df["risk_label"] = df["learning_gap_score"].apply(classify_risk)


# Select input features
features = [
    "quiz_score",
    "assignment_score",
    "attendance",
    "videos_watched",
    "lessons_completed",
    "login_frequency",
    "days_inactive",
    "previous_topic_score",
    "engagement_score"
]

X = df[features]
y = df["risk_label"]


# Split the data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# Train the Random Forest model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)


# Evaluate the model
predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("Model training completed successfully!")
print("Accuracy:", round(accuracy * 100, 2), "%")
print("\nClassification Report:")
print(classification_report(y_test, predictions))


# Save the model
model_folder = Path("models")
model_folder.mkdir(parents=True, exist_ok=True)

model_file = model_folder / "risk_model.pkl"
joblib.dump(model, model_file)

print("Model saved at:", model_file)