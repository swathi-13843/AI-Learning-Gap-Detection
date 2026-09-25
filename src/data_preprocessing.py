import pandas as pd
from pathlib import Path


def load_data():
    input_file = Path("data/raw/student_activity.csv")
    df = pd.read_csv(input_file)
    return df


def preprocess_data(df):
    # Remove duplicate records
    df = df.drop_duplicates()

    # Handle missing values
    numeric_columns = df.select_dtypes(include=["number"]).columns
    df[numeric_columns] = df[numeric_columns].fillna(
        df[numeric_columns].median()
    )

    # Create the processed-data folder
    output_folder = Path("data/processed")
    output_folder.mkdir(parents=True, exist_ok=True)

    # Save the cleaned dataset
    output_file = output_folder / "cleaned_student_activity.csv"
    df.to_csv(output_file, index=False)

    print("Data preprocessing completed successfully!")
    print("Rows:", len(df))
    print("Columns:", len(df.columns))
    print("Saved file:", output_file)

    return df


if __name__ == "__main__":
    data = load_data()
    preprocess_data(data)