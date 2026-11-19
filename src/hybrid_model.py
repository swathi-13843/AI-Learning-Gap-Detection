"""
TAT-KG: Topic-Aware Temporal Knowledge Gap Detection Hybrid Model.

Proposed Architecture:
- Bayesian Knowledge Tracing (BKT): Latent topic knowledge mastery P(L_t)
- PyTorch GRU: Temporal student learning trajectory representation h_t
- LightGBM: Non-linear gradient boosted feature fusion and multi-class classification
- SHAP: Explainable attribution for predictions and topic gaps
"""

import sys
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import numpy as np
import pandas as pd
import joblib
import torch
from lightgbm import LGBMClassifier
from sklearn.preprocessing import StandardScaler

from src.knowledge_tracing import BayesianKnowledgeTracer, build_response_trials_from_activity
from src.gru_model import (
    StudentTemporalGRU,
    StudentSequenceDataset,
    GRUTrainer,
    build_student_sequences,
    extract_gru_embeddings_for_all,
    TEMPORAL_FEATURE_COLS,
    normalize_temporal_row
)

# Core tabular feature columns used in the hybrid fusion (excluding target label)
TABULAR_FUSION_COLS = [
    "quiz_score",
    "assignment_score",
    "attendance",
    "videos_watched",
    "lessons_completed",
    "login_frequency",
    "days_inactive",
    "previous_topic_score",
    "quiz_accuracy",
    "engagement_score",
    "topic_completion_rate",
    "activity_consistency",
    "quiz_improvement_rate",
    "previous_topic_dependency",
    "recent_performance_trend",
    "learning_progress_over_time",
    "overall_avg_quiz",
    "overall_avg_assignment",
    "overall_attendance",
    "topic_gap_differential",
    "is_hidden_gap_candidate"
]

BKT_FEATURE_COLS = [
    "bkt_mastery_prob",
    "bkt_learning_gain",
    "bkt_low_mastery_flag",
    "bkt_slip_risk",
    "bkt_guess_prob"
]

CLASSES = ["Low Gap", "Medium Gap", "High Gap"]
LABEL_MAP = {c: i for i, c in enumerate(CLASSES)}
REV_LABEL_MAP = {i: c for i, c in enumerate(CLASSES)}


class TATKGHybridModel:
    """
    TAT-KG Hybrid Model combining BKT, GRU, and LightGBM.
    """

    def __init__(self, gru_hidden_dim=32, lgbm_params=None):
        self.gru_hidden_dim = gru_hidden_dim
        self.bkt = BayesianKnowledgeTracer()
        self.gru = StudentTemporalGRU(
            input_dim=len(TEMPORAL_FEATURE_COLS),
            hidden_dim=gru_hidden_dim,
            num_layers=1,
            num_classes=3,
            dropout=0.25
        )
        self.scaler = StandardScaler()

        default_lgbm_params = {
            "n_estimators": 160,
            "learning_rate": 0.05,
            "num_leaves": 31,
            "max_depth": 6,
            "subsample": 0.85,
            "colsample_bytree": 0.85,
            "class_weight": "balanced",
            "random_state": 42,
            "verbosity": -1
        }
        if lgbm_params:
            default_lgbm_params.update(lgbm_params)
        self.lgbm = LGBMClassifier(**default_lgbm_params)
        self.is_fitted = False
        self.fusion_feature_names = []

    def fit(self, df_train, epochs_gru=30, verbose=False):
        """
        Trains the full TAT-KG pipeline:
        1. Calibrates BKT parameters
        2. Trains GRU on student sequences
        3. Extracts GRU temporal embeddings h_t
        4. Fuses features: [Tabular + BKT + GRU Hidden States]
        5. Fits LightGBM classifier
        """
        if verbose:
            print("[TAT-KG] Step 1/5: Fitting Bayesian Knowledge Tracing parameters...")
        trials_df = build_response_trials_from_activity(df_train)
        self.bkt.fit_topic_parameters(trials_df)

        if verbose:
            print("[TAT-KG] Step 2/5: Training GRU temporal network on chronological sequences...")
        student_seqs = build_student_sequences(df_train, LABEL_MAP)
        train_seqs = [data["features"] for data in student_seqs.values()]
        train_labels = [data["labels"] for data in student_seqs.values()]

        # Class weights for GRU CrossEntropy
        flat_labels = np.concatenate(train_labels)
        class_counts = np.bincount(flat_labels, minlength=3)
        weights = len(flat_labels) / (3.0 * np.maximum(class_counts, 1))

        dataset = StudentSequenceDataset(train_seqs, train_labels)
        train_loader = torch.utils.data.DataLoader(dataset, batch_size=16, shuffle=True)
        trainer = GRUTrainer(self.gru, lr=0.003, class_weights=weights, patience=6)
        trainer.fit(train_loader, epochs=epochs_gru)

        if verbose:
            print("[TAT-KG] Step 3/5: Extracting GRU temporal hidden embeddings...")
        gru_embeddings = extract_gru_embeddings_for_all(self.gru, student_seqs)

        if verbose:
            print("[TAT-KG] Step 4/5: Performing multi-modal feature fusion...")
        X_fusion, y_labels, feature_names = self._build_fusion_matrix(df_train, gru_embeddings)
        self.fusion_feature_names = feature_names

        # Normalize tabular features
        X_scaled = self.scaler.fit_transform(X_fusion)

        if verbose:
            print("[TAT-KG] Step 5/5: Training LightGBM fusion classifier...")
        self.lgbm.fit(X_scaled, y_labels)
        self.is_fitted = True

        if verbose:
            print("[TAT-KG] Training completed successfully!")
        return self

    def _build_fusion_matrix(self, df, gru_embeddings):
        """
        Merges Tabular features + BKT features + GRU hidden states.
        """
        rows = []
        labels = []

        # Ensure BKT features are present
        for col in BKT_FEATURE_COLS:
            if col not in df.columns:
                df = df.copy()
                bkt_feats = [
                    self.bkt.extract_features_for_student_topic(
                        quiz_score=float(r["quiz_score"]),
                        total_questions=int(r.get("total_questions", 20)),
                        correct_answers=int(r.get("correct_answers", round(20 * r["quiz_score"] / 100.0))),
                        attempts=int(r.get("quiz_attempts", 1)),
                        topic=r.get("topic")
                    )
                    for _, r in df.iterrows()
                ]
                bkt_df = pd.DataFrame(bkt_feats)
                for c in bkt_df.columns:
                    df[c] = bkt_df[c].values
                break

        feature_names = list(TABULAR_FUSION_COLS) + list(BKT_FEATURE_COLS)
        for h_i in range(self.gru_hidden_dim):
            feature_names.append(f"gru_h_{h_i}")

        for _, row in df.iterrows():
            sid = row["student_id"]
            topic = row["topic"]

            tab_vals = [float(row.get(c, 0.0)) for c in TABULAR_FUSION_COLS]
            bkt_vals = [float(row.get(c, 0.5)) for c in BKT_FEATURE_COLS]

            # GRU embedding
            gru_h = gru_embeddings.get((sid, topic), np.zeros(self.gru_hidden_dim, dtype=np.float32))
            fused_row = tab_vals + bkt_vals + list(gru_h)
            rows.append(fused_row)

            gap_cat = row.get("gap_category", "Medium Gap")
            labels.append(LABEL_MAP.get(gap_cat, 1))

        return np.array(rows, dtype=np.float32), np.array(labels, dtype=np.int64), feature_names

    def transform_features(self, df):
        """
        Builds and scales fusion matrix for inference.
        """
        student_seqs = build_student_sequences(df, LABEL_MAP)
        gru_embeddings = extract_gru_embeddings_for_all(self.gru, student_seqs)
        X_fusion, _, _ = self._build_fusion_matrix(df, gru_embeddings)
        return self.scaler.transform(X_fusion)

    def predict(self, df):
        X_scaled = self.transform_features(df)
        preds_idx = self.lgbm.predict(X_scaled)
        return [REV_LABEL_MAP[i] for i in preds_idx]

    def predict_proba(self, df):
        X_scaled = self.transform_features(df)
        return self.lgbm.predict_proba(X_scaled)

    def predict_single_topic(self, student_info, topic_name, sequence_history=None):
        """
        Inference for an individual student on a specific topic.
        Detects hidden learning gaps when student performs well overall but struggles here.
        """
        q_val = float(student_info.get("quiz_score", 50.0))
        assign_val = float(student_info.get("assignment_score", 50.0))
        att_val = float(student_info.get("attendance", 75.0))
        overall_avg = float(student_info.get("overall_avg_quiz", student_info.get("average_quiz_score", q_val)))

        # BKT calculation
        bkt_res = self.bkt.extract_features_for_student_topic(
            quiz_score=q_val,
            total_questions=int(student_info.get("total_questions", 20)),
            correct_answers=student_info.get("correct_answers"),
            attempts=int(student_info.get("quiz_attempts", 1)),
            topic=topic_name
        )

        # Build temporal sequence including history
        step_feat = normalize_temporal_row({
            "quiz_score": q_val,
            "assignment_score": assign_val,
            "attendance": att_val,
            "videos_watched": student_info.get("videos_watched", 4),
            "lessons_completed": student_info.get("lessons_completed", 5),
            "login_frequency": student_info.get("login_frequency", 4),
            "days_inactive": student_info.get("days_inactive", 3),
            "time_spent_minutes": student_info.get("time_spent_minutes", 45),
            "quiz_accuracy": q_val,
            "engagement_score": student_info.get("engagement_score", 50),
            "score_delta_prev": q_val - overall_avg
        })

        if sequence_history and len(sequence_history) > 0:
            seq_tensor = torch.tensor([sequence_history + [step_feat]], dtype=torch.float32)
        else:
            seq_tensor = torch.tensor([[step_feat]], dtype=torch.float32)

        self.gru.eval()
        with torch.no_grad():
            _, h_out = self.gru(seq_tensor)
            h_last = h_out[0, -1].cpu().numpy()

        # Build tabular values
        engagement = float(student_info.get("engagement_score", 50.0))
        diff = overall_avg - q_val
        is_hidden = int((overall_avg >= 70.0) and (q_val <= 55.0))

        tab_vals = [
            q_val,
            assign_val,
            att_val,
            float(student_info.get("videos_watched", 4)),
            float(student_info.get("lessons_completed", 5)),
            float(student_info.get("login_frequency", 4)),
            float(student_info.get("days_inactive", 3)),
            float(student_info.get("previous_topic_score", q_val)),
            q_val,
            engagement,
            float(student_info.get("lessons_completed", 5)) * 10.0,
            att_val * 0.6 + 20.0,
            q_val / max(1, int(student_info.get("quiz_attempts", 1))),
            q_val - overall_avg,
            q_val,
            q_val,
            overall_avg,
            float(student_info.get("overall_avg_assignment", assign_val)),
            att_val,
            diff,
            is_hidden
        ]
        bkt_vals = [
            bkt_res["bkt_mastery_prob"],
            bkt_res["bkt_learning_gain"],
            bkt_res["bkt_low_mastery_flag"],
            bkt_res["bkt_slip_risk"],
            bkt_res["bkt_guess_prob"]
        ]
        fused = np.array([tab_vals + bkt_vals + list(h_last)], dtype=np.float32)
        fused_scaled = self.scaler.transform(fused)

        probs = self.lgbm.predict_proba(fused_scaled)[0]
        prob_dict = {
            "Low Gap": round(float(probs[0]) * 100.0, 1),
            "Medium Gap": round(float(probs[1]) * 100.0, 1),
            "High Gap": round(float(probs[2]) * 100.0, 1),
        }
        pred_class = CLASSES[int(np.argmax(probs))]

        # If hidden gap candidate with high differential, boost risk awareness
        if is_hidden and pred_class == "Low Gap":
            pred_class = "Medium Gap"

        confidence = prob_dict[pred_class]
        return {
            "prediction": pred_class,
            "probabilities": prob_dict,
            "confidence": confidence,
            "bkt_mastery_prob": bkt_res["bkt_mastery_prob"],
            "is_hidden_gap": bool(is_hidden),
            "topic_gap_differential": round(diff, 1)
        }

    def save(self, model_dir="models"):
        model_dir = Path(model_dir)
        model_dir.mkdir(parents=True, exist_ok=True)

        self.bkt.save(model_dir / "bkt_model.pkl")
        torch.save(self.gru.state_dict(), model_dir / "gru_model.pth")
        joblib.dump(self.lgbm, model_dir / "lightgbm_model.pkl")
        joblib.dump(self.scaler, model_dir / "fusion_scaler.pkl")

        metadata = {
            "gru_hidden_dim": self.gru_hidden_dim,
            "fusion_feature_names": self.fusion_feature_names,
            "classes": CLASSES,
            "is_fitted": self.is_fitted
        }
        with open(model_dir / "model_metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

    @classmethod
    def load(cls, model_dir="models"):
        model_dir = Path(model_dir)
        meta_file = model_dir / "model_metadata.json"
        hidden_dim = 32
        feature_names = []
        if meta_file.exists():
            with open(meta_file, "r", encoding="utf-8") as f:
                meta = json.load(f)
                hidden_dim = meta.get("gru_hidden_dim", 32)
                feature_names = meta.get("fusion_feature_names", [])

        model = cls(gru_hidden_dim=hidden_dim)
        if (model_dir / "bkt_model.pkl").exists():
            model.bkt = BayesianKnowledgeTracer.load(model_dir / "bkt_model.pkl")
        if (model_dir / "gru_model.pth").exists():
            model.gru.load_state_dict(torch.load(model_dir / "gru_model.pth", weights_only=True))
            model.gru.eval()
        if (model_dir / "lightgbm_model.pkl").exists():
            model.lgbm = joblib.load(model_dir / "lightgbm_model.pkl")
        if (model_dir / "fusion_scaler.pkl").exists():
            model.scaler = joblib.load(model_dir / "fusion_scaler.pkl")

        model.fusion_feature_names = feature_names
        model.is_fitted = True
        return model
