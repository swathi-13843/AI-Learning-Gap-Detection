import pandas as pd
import joblib

from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


# Load the processed dataset
input_file = Path(
    "data/processed/engineered_student_activity.csv"
)

df = pd.read_csv(input_file)


# Select behavioral features
features = [
    "quiz_score",
    "assignment_score",
    "attendance",
    "videos_watched",
    "lessons_completed",
    "login_frequency",
    "days_inactive",
    "engagement_score"
]


# Calculate student-level averages
student_data = df.groupby("student_id")[features].mean().reset_index()


# Standardize the features
scaler = StandardScaler()
scaled_data = scaler.fit_transform(student_data[features])


# Train the K-Means model
kmeans = KMeans(
    n_clusters=3,
    random_state=42,
    n_init=10
)

student_data["cluster"] = kmeans.fit_predict(scaled_data)


# Display cluster statistics
cluster_summary = student_data.groupby("cluster")[features].mean()

print("K-Means clustering completed successfully!")
print("\nCluster summary:")
print(cluster_summary)


# Save the clustering results
output_folder = Path("data/processed")
output_folder.mkdir(parents=True, exist_ok=True)

output_file = output_folder / "student_clusters.csv"
student_data.to_csv(output_file, index=False)


# Save the models
model_folder = Path("models")
model_folder.mkdir(parents=True, exist_ok=True)

joblib.dump(kmeans, model_folder / "kmeans_model.pkl")
joblib.dump(scaler, model_folder / "scaler.pkl")

print("\nCluster results saved at:", output_file)
print("K-Means model saved at:", model_folder / "kmeans_model.pkl")
print("Scaler saved at:", model_folder / "scaler.pkl")