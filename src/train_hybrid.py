"""
Training and Optimization Script for TAT-KG Hybrid Model.
Features:
- Student-wise group splitting (GroupShuffleSplit) preventing data leakage
- Optuna Bayesian hyperparameter optimization
- Class weighting and threshold handling
- Multi-component pipeline checkpointing
"""

import sys
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import numpy as np
import pandas as pd
import optuna
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

from src.preprocessing import load_raw_activity_data, preprocess_activity_data
from src.feature_engineering import engineer_learning_gap_features
from src.hybrid_model import TATKGHybridModel, CLASSES, LABEL_MAP

optuna.logging.set_verbosity(optuna.logging.WARNING)


def run_optuna_tuning(X_train, y_train, groups, n_trials=12):
    """
    Optimizes LightGBM hyperparameters using Optuna with GroupKFold cross-validation.
    """
    from lightgbm import LGBMClassifier
    from sklearn.model_selection import GroupKFold

    def objective(trial):
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 80, 220, step=20),
            "learning_rate": trial.suggest_float("learning_rate", 0.02, 0.15, log=True),
            "num_leaves": trial.suggest_int("num_leaves", 15, 63),
            "max_depth": trial.suggest_int("max_depth", 3, 8),
            "subsample": trial.suggest_float("subsample", 0.7, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.7, 1.0),
            "reg_alpha": trial.suggest_float("reg_alpha", 1e-3, 10.0, log=True),
            "reg_lambda": trial.suggest_float("reg_lambda", 1e-3, 10.0, log=True),
            "class_weight": "balanced",
            "random_state": 42,
            "verbosity": -1
        }
        gkf = GroupKFold(n_splits=3)
        scores = []
        for tr_idx, val_idx in gkf.split(X_train, y_train, groups):
            clf = LGBMClassifier(**params)
            clf.fit(X_train[tr_idx], y_train[tr_idx])
            preds = clf.predict(X_train[val_idx])
            score = f1_score(y_train[val_idx], preds, average="macro", zero_division=0)
            scores.append(score)
        return float(np.mean(scores))

    study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=42))
    study.optimize(objective, n_trials=n_trials)
    return study.best_params


def train_and_save_hybrid_model(data_path="data/processed/engineered_student_activity.csv", run_tuning=True):
    data_path = Path(data_path)
    if not data_path.exists():
        print("[Train] Engineered data not found, generating...")
        raw = load_raw_activity_data()
        cleaned = preprocess_activity_data(raw)
        df = engineer_learning_gap_features(cleaned)
        df.to_csv(data_path, index=False)
    else:
        df = pd.read_csv(data_path)

    print(f"[Train] Dataset loaded with {len(df)} records across {df['student_id'].nunique()} students.")

    # Student-wise split: 80% train students, 20% test students
    gss = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)
    train_idx, test_idx = next(gss.split(df, groups=df["student_id"]))
    df_train = df.iloc[train_idx].reset_index(drop=True)
    df_test = df.iloc[test_idx].reset_index(drop=True)

    print(f"[Train] Train students: {df_train['student_id'].nunique()} ({len(df_train)} rows)")
    print(f"[Train] Test students: {df_test['student_id'].nunique()} ({len(df_test)} rows)")

    lgbm_params = None
    if run_tuning:
        print("[Train] Running Optuna hyperparameter optimization...")
        # Quick pre-fit to extract fusion matrix for tuning
        base_hybrid = TATKGHybridModel()
        base_hybrid.fit(df_train, epochs_gru=15, verbose=False)
        X_tr, y_tr, _ = base_hybrid._build_fusion_matrix(
            df_train,
            gru_embeddings=extract_from_trained(base_hybrid.gru, df_train)
        )
        groups_tr = df_train["student_id"].values
        best_params = run_optuna_tuning(X_tr, y_tr, groups_tr, n_trials=10)
        print(f"[Train] Best Optuna parameters: {best_params}")
        lgbm_params = best_params

    # Final full training of TAT-KG
    print("[Train] Training final TAT-KG hybrid model...")
    hybrid_model = TATKGHybridModel(gru_hidden_dim=32, lgbm_params=lgbm_params)
    hybrid_model.fit(df_train, epochs_gru=30, verbose=True)

    # Evaluate on held-out unseen test students
    test_preds = hybrid_model.predict(df_test)
    y_test_true = df_test["gap_category"].tolist()

    acc = accuracy_score(y_test_true, test_preds)
    macro_p = precision_score(y_test_true, test_preds, average="macro", zero_division=0)
    macro_r = recall_score(y_test_true, test_preds, average="macro", zero_division=0)
    macro_f1 = f1_score(y_test_true, test_preds, average="macro", zero_division=0)
    weighted_f1 = f1_score(y_test_true, test_preds, average="weighted", zero_division=0)

    print("\n" + "=" * 50)
    print("TAT-KG HYBRID MODEL EVALUATION (HELD-OUT TEST SET)")
    print("=" * 50)
    print(f"Accuracy:        {acc * 100:.2f}%")
    print(f"Macro Precision: {macro_p * 100:.2f}%")
    print(f"Macro Recall:    {macro_r * 100:.2f}%")
    print(f"Macro F1-Score:  {macro_f1 * 100:.2f}%")
    print(f"Weighted F1:     {weighted_f1 * 100:.2f}%")
    print("\nClassification Report:")
    print(classification_report(y_test_true, test_preds, zero_division=0))

    # Save models
    models_dir = Path("models")
    hybrid_model.save(models_dir)
    print(f"[Train] Models successfully saved to {models_dir}/")

    return hybrid_model, {
        "accuracy": acc,
        "macro_precision": macro_p,
        "macro_recall": macro_r,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1
    }


def extract_from_trained(gru_model, df):
    from src.gru_model import build_student_sequences, extract_gru_embeddings_for_all
    student_seqs = build_student_sequences(df, LABEL_MAP)
    return extract_gru_embeddings_for_all(gru_model, student_seqs)


if __name__ == "__main__":
    train_and_save_hybrid_model(run_tuning=False)
