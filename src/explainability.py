import pandas as pd
import joblib
import shap
import numpy as np

from pathlib import Path


# Load the trained model
model = joblib.load("models/risk_model.pkl")

# Load the dataset
data_file = Path(
    "data/processed/engineered_student_activity.csv"
)

df = pd.read_csv(data_file)


# Features used during model training
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

X = df[features].head(100)


# Create the SHAP explainer
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X)


print("SHAP explainability analysis completed!")
print("Number of records explained:", len(X))

print("\nFeatures used for explanation:")
for feature in features:
    print("-", feature)


# Convert SHAP values into a NumPy array
shap_array = np.asarray(shap_values)

print("\nSHAP output shape:", shap_array.shape)


# Handle different SHAP output formats
if shap_array.ndim == 3:
    # Format: samples x features x classes
    importance_values = np.abs(shap_array).mean(axis=(0, 2))

elif shap_array.ndim == 2:
    # Format: samples x features
    importance_values = np.abs(shap_array).mean(axis=0)

elif isinstance(shap_values, list):
    # Older SHAP format: one array per class
    importance_values = np.mean(
        [
            np.abs(class_values).mean(axis=0)
            for class_values in shap_values
        ],
        axis=0
    )

else:
    raise ValueError(
        f"Unexpected SHAP output shape: {shap_array.shape}"
    )


# Create the feature-importance DataFrame
importance_df = pd.DataFrame({
    "feature": features,
    "importance": importance_values
})

importance_df = importance_df.sort_values(
    by="importance",
    ascending=False
)


print("\nFeature importance:")
print(importance_df)


# Save feature importance
output_folder = Path("data/processed")
output_folder.mkdir(parents=True, exist_ok=True)

output_file = output_folder / "feature_importance.csv"
importance_df.to_csv(output_file, index=False)

print("\nFeature importance saved at:", output_file)