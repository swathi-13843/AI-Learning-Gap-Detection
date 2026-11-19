"""
Comprehensive Model Comparison and Ablation Evaluation Module.
Trains and evaluates all 11 models under identical student-wise train/test splits:
1. Random Forest
2. Decision Tree
3. KNN
4. SVM
5. LightGBM
6. BKT
7. GRU
8. BKT + GRU
9. GRU + LightGBM
10. BKT + LightGBM
11. Proposed TAT-KG Hybrid Model (BKT + GRU + LightGBM)

Calculates actual, experimentally measured metrics:
- Accuracy, Precision, Recall, Macro F1, Weighted F1, Class-wise F1
Saves results to reports/model_comparison.csv and generates comparison figures.
"""

import sys
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import numpy as np
import pandas as pd
import os
import tempfile
os.environ.setdefault("MPLCONFIGDIR", os.path.join(tempfile.gettempdir(), "matplotlib_edugap"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import torch

from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from lightgbm import LGBMClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

from src.preprocessing import load_raw_activity_data, preprocess_activity_data
from src.feature_engineering import engineer_learning_gap_features
from src.knowledge_tracing import BayesianKnowledgeTracer, build_response_trials_from_activity
from src.gru_model import (
    StudentTemporalGRU,
    StudentSequenceDataset,
    GRUTrainer,
    build_student_sequences,
    extract_gru_embeddings_for_all,
    TEMPORAL_FEATURE_COLS
)
from src.hybrid_model import (
    TATKGHybridModel,
    TABULAR_FUSION_COLS,
    BKT_FEATURE_COLS,
    CLASSES,
    LABEL_MAP,
    REV_LABEL_MAP
)


def compute_all_metrics(y_true, y_pred):
    acc = accuracy_score(y_true, y_pred)
    macro_p = precision_score(y_true, y_pred, average="macro", zero_division=0)
    weighted_p = precision_score(y_true, y_pred, average="weighted", zero_division=0)
    macro_r = recall_score(y_true, y_pred, average="macro", zero_division=0)
    weighted_r = recall_score(y_true, y_pred, average="weighted", zero_division=0)
    macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
    weighted_f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)

    # Class-wise F1
    c_f1 = f1_score(y_true, y_pred, average=None, labels=CLASSES, zero_division=0)
    return {
        "Accuracy": round(acc * 100.0, 2),
        "Precision (Macro)": round(macro_p * 100.0, 2),
        "Precision (Weighted)": round(weighted_p * 100.0, 2),
        "Recall (Macro)": round(macro_r * 100.0, 2),
        "Recall (Weighted)": round(weighted_r * 100.0, 2),
        "Macro F1": round(macro_f1 * 100.0, 2),
        "Weighted F1": round(weighted_f1 * 100.0, 2),
        "Low Gap F1": round(c_f1[0] * 100.0, 2),
        "Medium Gap F1": round(c_f1[1] * 100.0, 2),
        "High Gap F1": round(c_f1[2] * 100.0, 2)
    }


def run_benchmark_and_ablation(data_path="data/processed/engineered_student_activity.csv", reports_dir="reports"):
    reports_dir = Path(reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)

    data_path = Path(data_path)
    if not data_path.exists():
        raw = load_raw_activity_data()
        cleaned = preprocess_activity_data(raw)
        df = engineer_learning_gap_features(cleaned)
        df.to_csv(data_path, index=False)
    else:
        df = pd.read_csv(data_path)

    # Student-wise 80/20 train/test split
    gss = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)
    train_idx, test_idx = next(gss.split(df, groups=df["student_id"]))
    df_train = df.iloc[train_idx].reset_index(drop=True)
    df_test = df.iloc[test_idx].reset_index(drop=True)

    y_train = df_train["gap_category"].values
    y_test = df_test["gap_category"].values

    print(f"[Benchmark] Train records: {len(df_train)} | Test records: {len(df_test)}")

    # 1. Feature sets
    X_base_train = df_train[TABULAR_FUSION_COLS].values
    X_base_test = df_test[TABULAR_FUSION_COLS].values

    scaler_base = StandardScaler()
    X_base_tr_scaled = scaler_base.fit_transform(X_base_train)
    X_base_te_scaled = scaler_base.transform(X_base_test)

    # 2. BKT components
    bkt = BayesianKnowledgeTracer()
    trials_df = build_response_trials_from_activity(df_train)
    bkt.fit_topic_parameters(trials_df)

    X_bkt_train = df_train[BKT_FEATURE_COLS].values
    X_bkt_test = df_test[BKT_FEATURE_COLS].values

    # 3. GRU components
    seqs_tr_dict = build_student_sequences(df_train, LABEL_MAP)
    seqs_te_dict = build_student_sequences(df_test, LABEL_MAP)

    train_seqs = [d["features"] for d in seqs_tr_dict.values()]
    train_labels = [d["labels"] for d in seqs_tr_dict.values()]

    flat_l = np.concatenate(train_labels)
    c_counts = np.bincount(flat_l, minlength=3)
    c_weights = len(flat_l) / (3.0 * np.maximum(c_counts, 1))

    gru_model = StudentTemporalGRU(
        input_dim=len(TEMPORAL_FEATURE_COLS),
        hidden_dim=32,
        num_layers=1,
        dropout=0.25
    )
    dataset_tr = StudentSequenceDataset(train_seqs, train_labels)
    loader_tr = torch.utils.data.DataLoader(dataset_tr, batch_size=16, shuffle=True)
    trainer = GRUTrainer(gru_model, lr=0.003, class_weights=c_weights, patience=8)
    trainer.fit(loader_tr, epochs=30)

    # Extract GRU embeddings
    gru_tr_embs = extract_gru_embeddings_for_all(gru_model, seqs_tr_dict)
    gru_te_embs = extract_gru_embeddings_for_all(gru_model, seqs_te_dict)

    X_gru_train = np.array([gru_tr_embs[(r["student_id"], r["topic"])] for _, r in df_train.iterrows()])
    X_gru_test = np.array([gru_te_embs[(r["student_id"], r["topic"])] for _, r in df_test.iterrows()])

    # Combined representations
    X_bkt_gru_train = np.hstack([X_bkt_train, X_gru_train])
    X_bkt_gru_test = np.hstack([X_bkt_test, X_gru_test])

    X_base_gru_train = np.hstack([X_base_train, X_gru_train])
    X_base_gru_test = np.hstack([X_base_test, X_gru_test])

    X_base_bkt_train = np.hstack([X_base_train, X_bkt_train])
    X_base_bkt_test = np.hstack([X_base_test, X_bkt_test])

    X_full_train = np.hstack([X_base_train, X_bkt_train, X_gru_train])
    X_full_test = np.hstack([X_base_test, X_bkt_test, X_gru_test])

    scaler_full = StandardScaler()
    X_full_tr_scaled = scaler_full.fit_transform(X_full_train)
    X_full_te_scaled = scaler_full.transform(X_full_test)

    # Dictionary to collect results
    results = []
    confusion_matrices = {}

    # -------------------------------------------------------------
    # Model 1: Random Forest
    # -------------------------------------------------------------
    print("[1/11] Training Random Forest...")
    rf = RandomForestClassifier(n_estimators=100, max_depth=8, class_weight="balanced", random_state=42)
    rf.fit(X_base_train, y_train)
    preds_rf = rf.predict(X_base_test)
    m_rf = compute_all_metrics(y_test, preds_rf)
    results.append({"Model": "Random Forest", **m_rf})

    # -------------------------------------------------------------
    # Model 2: Decision Tree
    # -------------------------------------------------------------
    print("[2/11] Training Decision Tree...")
    dt = DecisionTreeClassifier(max_depth=6, class_weight="balanced", random_state=42)
    dt.fit(X_base_train, y_train)
    preds_dt = dt.predict(X_base_test)
    m_dt = compute_all_metrics(y_test, preds_dt)
    results.append({"Model": "Decision Tree", **m_dt})

    # -------------------------------------------------------------
    # Model 3: KNN
    # -------------------------------------------------------------
    print("[3/11] Training KNN...")
    knn = KNeighborsClassifier(n_neighbors=7)
    knn.fit(X_base_tr_scaled, y_train)
    preds_knn = knn.predict(X_base_te_scaled)
    m_knn = compute_all_metrics(y_test, preds_knn)
    results.append({"Model": "KNN", **m_knn})

    # -------------------------------------------------------------
    # Model 4: SVM
    # -------------------------------------------------------------
    print("[4/11] Training SVM...")
    svm = SVC(kernel="rbf", C=1.5, class_weight="balanced", random_state=42)
    svm.fit(X_base_tr_scaled, y_train)
    preds_svm = svm.predict(X_base_te_scaled)
    m_svm = compute_all_metrics(y_test, preds_svm)
    results.append({"Model": "SVM", **m_svm})

    # -------------------------------------------------------------
    # Model 5: LightGBM (Baseline Tabular)
    # -------------------------------------------------------------
    print("[5/11] Training LightGBM...")
    lgbm_base = LGBMClassifier(n_estimators=120, learning_rate=0.05, class_weight="balanced", random_state=42, verbosity=-1)
    lgbm_base.fit(X_base_train, y_train)
    preds_lgbm = lgbm_base.predict(X_base_test)
    m_lgbm = compute_all_metrics(y_test, preds_lgbm)
    results.append({"Model": "LightGBM", **m_lgbm})

    # -------------------------------------------------------------
    # Model 6: BKT (Rule/Mastery Probability Alone)
    # -------------------------------------------------------------
    print("[6/11] Evaluating BKT standalone...")
    # BKT maps mastery probability directly to gap severity
    preds_bkt = []
    for _, row in df_test.iterrows():
        p_m = float(row.get("bkt_mastery_prob", 0.5))
        if p_m <= 0.40:
            preds_bkt.append("High Gap")
        elif p_m <= 0.70:
            preds_bkt.append("Medium Gap")
        else:
            preds_bkt.append("Low Gap")
    m_bkt = compute_all_metrics(y_test, preds_bkt)
    results.append({"Model": "BKT", **m_bkt})

    # -------------------------------------------------------------
    # Model 7: GRU (Sequence Model Standalone)
    # -------------------------------------------------------------
    print("[7/11] Evaluating GRU standalone...")
    gru_model.eval()
    preds_gru = []
    with torch.no_grad():
        for sid, d in seqs_te_dict.items():
            seq_t = torch.tensor(d["features"], dtype=torch.float32).unsqueeze(0)
            logits, _ = gru_model(seq_t)
            step_preds = torch.argmax(logits.squeeze(0), dim=-1).cpu().numpy()
            for sp in step_preds:
                preds_gru.append(REV_LABEL_MAP[sp])
    m_gru = compute_all_metrics(y_test, preds_gru)
    results.append({"Model": "GRU", **m_gru})

    # -------------------------------------------------------------
    # Model 8: BKT + GRU (Ablation: Knowledge + Temporal)
    # -------------------------------------------------------------
    print("[8/11] Training BKT + GRU ablation model...")
    scaler_bg = StandardScaler()
    X_bg_tr = scaler_bg.fit_transform(X_bkt_gru_train)
    X_bg_te = scaler_bg.transform(X_bkt_gru_test)
    clf_bg = LGBMClassifier(n_estimators=100, learning_rate=0.05, class_weight="balanced", random_state=42, verbosity=-1)
    clf_bg.fit(X_bg_tr, y_train)
    preds_bg = clf_bg.predict(X_bg_te)
    m_bg = compute_all_metrics(y_test, preds_bg)
    results.append({"Model": "BKT + GRU", **m_bg})

    # -------------------------------------------------------------
    # Model 9: GRU + LightGBM (Ablation: Temporal + Gradient Boosting)
    # -------------------------------------------------------------
    print("[9/11] Training GRU + LightGBM ablation model...")
    scaler_gru_lgbm = StandardScaler()
    X_gl_tr = scaler_gru_lgbm.fit_transform(X_base_gru_train)
    X_gl_te = scaler_gru_lgbm.transform(X_base_gru_test)
    clf_gl = LGBMClassifier(n_estimators=120, learning_rate=0.05, class_weight="balanced", random_state=42, verbosity=-1)
    clf_gl.fit(X_gl_tr, y_train)
    preds_gl = clf_gl.predict(X_gl_te)
    m_gl = compute_all_metrics(y_test, preds_gl)
    results.append({"Model": "GRU + LightGBM", **m_gl})

    # -------------------------------------------------------------
    # Model 10: BKT + LightGBM (Ablation: Knowledge + Gradient Boosting)
    # -------------------------------------------------------------
    print("[10/11] Training BKT + LightGBM ablation model...")
    scaler_bkt_lgbm = StandardScaler()
    X_bl_tr = scaler_bkt_lgbm.fit_transform(X_base_bkt_train)
    X_bl_te = scaler_bkt_lgbm.transform(X_base_bkt_test)
    clf_bl = LGBMClassifier(n_estimators=120, learning_rate=0.05, class_weight="balanced", random_state=42, verbosity=-1)
    clf_bl.fit(X_bl_tr, y_train)
    preds_bl = clf_bl.predict(X_bl_te)
    m_bl = compute_all_metrics(y_test, preds_bl)
    results.append({"Model": "BKT + LightGBM", **m_bl})

    # -------------------------------------------------------------
    # Model 11: Proposed TAT-KG Hybrid Model (BKT + GRU + LightGBM)
    # -------------------------------------------------------------
    print("[11/11] Training Proposed TAT-KG Hybrid Model...")
    clf_tat = LGBMClassifier(
        n_estimators=180,
        learning_rate=0.04,
        num_leaves=35,
        max_depth=6,
        subsample=0.85,
        colsample_bytree=0.85,
        class_weight="balanced",
        random_state=42,
        verbosity=-1
    )
    clf_tat.fit(X_full_tr_scaled, y_train)
    preds_tat = clf_tat.predict(X_full_te_scaled)
    m_tat = compute_all_metrics(y_test, preds_tat)
    results.append({"Model": "Proposed TAT-KG (BKT + GRU + LightGBM)", **m_tat})

    confusion_matrices["Proposed TAT-KG"] = confusion_matrix(y_test, preds_tat, labels=CLASSES)

    # Convert results to DataFrame
    results_df = pd.DataFrame(results)
    csv_file = reports_dir / "model_comparison.csv"
    results_df.to_csv(csv_file, index=False)
    print(f"\n[Benchmark] Results saved to {csv_file}")

    # Generate Confusion Matrix Heatmap
    cm = confusion_matrices["Proposed TAT-KG"]
    plt.figure(figsize=(7, 6))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=CLASSES,
        yticklabels=CLASSES,
        cbar=False
    )
    plt.title("Confusion Matrix - Proposed TAT-KG Hybrid Model", fontsize=13, pad=12)
    plt.xlabel("Predicted Learning Gap Severity", fontsize=11)
    plt.ylabel("True Learning Gap Severity", fontsize=11)
    plt.tight_layout()
    cm_path = reports_dir / "confusion_matrix.png"
    plt.savefig(cm_path, dpi=200)
    plt.close()

    # Generate Model Comparison Chart
    plt.figure(figsize=(14, 7))
    x_positions = np.arange(len(results_df))
    width = 0.20

    plt.bar(x_positions - 1.5 * width, results_df["Accuracy"], width, label="Accuracy", color="#3b82f6")
    plt.bar(x_positions - 0.5 * width, results_df["Precision (Macro)"], width, label="Macro Precision", color="#10b981")
    plt.bar(x_positions + 0.5 * width, results_df["Recall (Macro)"], width, label="Macro Recall", color="#f59e0b")
    plt.bar(x_positions + 1.5 * width, results_df["Macro F1"], width, label="Macro F1-Score", color="#6366f1")

    plt.xlabel("Model Architecture", fontsize=12, fontweight="bold", labelpad=10)
    plt.ylabel("Score (%)", fontsize=12, fontweight="bold")
    plt.title("Rigorous Experimental Evaluation Across 11 Models (EduGap AI)", fontsize=14, pad=15)
    plt.xticks(x_positions, results_df["Model"], rotation=30, ha="right", fontsize=9.5)
    plt.ylim(0, 105)
    plt.grid(axis="y", linestyle="--", alpha=0.3)
    plt.legend(frameon=True, facecolor="white", edgecolor="none")
    plt.tight_layout()

    chart_path = reports_dir / "model_comparison_chart.png"
    plt.savefig(chart_path, dpi=200)
    plt.close()

    # Generate Detailed Classification Report CSV for Proposed Model
    report_dict = classification_report(y_test, preds_tat, output_dict=True, zero_division=0)
    report_df = pd.DataFrame(report_dict).transpose()
    report_csv = reports_dir / "classification_report.csv"
    report_df.to_csv(report_csv)

    print(f"[Benchmark] Figures and reports saved in {reports_dir}/")
    return results_df


if __name__ == "__main__":
    df_res = run_benchmark_and_ablation()
    print("\n" + "=" * 90)
    print("EXPERIMENTAL EVALUATION OF 11 MODELS (ACTUAL MEASURED VALUES)")
    print("=" * 90)
    print(df_res[["Model", "Accuracy", "Precision (Macro)", "Recall (Macro)", "Macro F1", "Weighted F1"]].to_string(index=False))
