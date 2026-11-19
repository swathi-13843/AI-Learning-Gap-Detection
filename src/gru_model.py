"""
PyTorch GRU (Gated Recurrent Unit) Model for Temporal Student Activity Analysis.
Analyzes chronological student activity sequences across curriculum topics to detect:
- Declining quiz and assessment trajectories
- Drifts in attendance, logins, and engagement
- Inactivity spikes and learning stalls
- Repeated learning struggles

Extracts temporal latent embeddings h_t for hybrid feature fusion with LightGBM,
and supports standalone sequence classification for ablation benchmarking.
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

# Feature columns used at each sequence time-step
TEMPORAL_FEATURE_COLS = [
    "quiz_score",
    "assignment_score",
    "attendance",
    "videos_watched",
    "lessons_completed",
    "login_frequency",
    "days_inactive",
    "time_spent_minutes",
    "quiz_accuracy",
    "engagement_score",
    "score_delta_prev"
]

FEATURE_SCALES = {
    "quiz_score": 100.0,
    "assignment_score": 100.0,
    "attendance": 100.0,
    "videos_watched": 10.0,
    "lessons_completed": 10.0,
    "login_frequency": 7.0,
    "days_inactive": 15.0,
    "time_spent_minutes": 120.0,
    "quiz_accuracy": 100.0,
    "engagement_score": 100.0,
    "score_delta_prev": 100.0
}


def normalize_temporal_row(row_dict):
    """Normalizes a single step dictionary to [0, 1] range."""
    norm = []
    for col in TEMPORAL_FEATURE_COLS:
        val = float(row_dict.get(col, 0.0))
        scale = FEATURE_SCALES.get(col, 100.0)
        norm.append(val / scale)
    return norm


class StudentSequenceDataset(Dataset):
    """
    Dataset that formats per-student sequential topics into tensors:
    sequences: [N, seq_len, feature_dim]
    labels: [N, seq_len] or [N]
    lengths: [N]
    """

    def __init__(self, sequences, labels=None, mask=None):
        self.sequences = torch.tensor(sequences, dtype=torch.float32)
        self.labels = torch.tensor(labels, dtype=torch.long) if labels is not None else None
        self.mask = torch.tensor(mask, dtype=torch.float32) if mask is not None else None

    def __len__(self):
        return len(self.sequences)

    def __getitem__(self, idx):
        item = {"sequence": self.sequences[idx]}
        if self.labels is not None:
            item["label"] = self.labels[idx]
        if self.mask is not None:
            item["mask"] = self.mask[idx]
        return item


class StudentTemporalGRU(nn.Module):
    """
    GRU Neural Network for Student Temporal Learning Modeling.
    """

    def __init__(self, input_dim=len(TEMPORAL_FEATURE_COLS), hidden_dim=32, num_layers=1, num_classes=3, dropout=0.25):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers

        self.gru = nn.GRU(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0
        )
        self.dropout = nn.Dropout(dropout)
        self.layer_norm = nn.LayerNorm(hidden_dim)

        # Classification head for predicting learning gap severity at step t or overall
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, num_classes)
        )

    def forward(self, x):
        """
        x: [batch_size, seq_len, input_dim]
        returns: logits [batch_size, seq_len, num_classes], all_hidden [batch_size, seq_len, hidden_dim]
        """
        out, _ = self.gru(x)  # out: [batch_size, seq_len, hidden_dim]
        normed = self.layer_norm(out)
        dropped = self.dropout(normed)
        logits = self.classifier(dropped)
        return logits, out

    def extract_hidden_representations(self, x):
        """
        Extracts temporal embeddings h_t: [batch_size, seq_len, hidden_dim]
        """
        self.eval()
        with torch.no_grad():
            out, _ = self.gru(x)
        return out


class GRUTrainer:
    """
    Handles training, validation, early stopping, and checkpointing for the GRU model.
    """

    def __init__(self, model, lr=0.003, weight_decay=1e-4, patience=7, class_weights=None):
        self.model = model
        self.optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
        if class_weights is not None:
            weights_tensor = torch.tensor(class_weights, dtype=torch.float32)
            self.criterion = nn.CrossEntropyLoss(weight=weights_tensor)
        else:
            self.criterion = nn.CrossEntropyLoss()
        self.patience = patience
        self.best_loss = float("inf")
        self.best_state = None
        self.history = []

    def fit(self, train_loader, val_loader=None, epochs=35):
        patience_counter = 0

        for epoch in range(1, epochs + 1):
            self.model.train()
            total_train_loss = 0.0
            total_train_items = 0

            for batch in train_loader:
                seqs = batch["sequence"]
                labels = batch["label"]  # [batch_size, seq_len]

                self.optimizer.zero_grad()
                logits, _ = self.model(seqs)  # [B, S, C]

                # Flatten for token-level classification loss
                B, S, C = logits.shape
                loss = self.criterion(logits.view(-1, C), labels.view(-1))
                loss.backward()
                nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.5)
                self.optimizer.step()

                total_train_loss += loss.item() * (B * S)
                total_train_items += (B * S)

            avg_train_loss = total_train_loss / max(1, total_train_items)

            # Validation
            avg_val_loss = avg_train_loss
            if val_loader is not None:
                self.model.eval()
                val_loss = 0.0
                val_items = 0
                with torch.no_grad():
                    for batch in val_loader:
                        seqs = batch["sequence"]
                        labels = batch["label"]
                        logits, _ = self.model(seqs)
                        B, S, C = logits.shape
                        loss = self.criterion(logits.view(-1, C), labels.view(-1))
                        val_loss += loss.item() * (B * S)
                        val_items += (B * S)
                avg_val_loss = val_loss / max(1, val_items)

            self.history.append({"epoch": epoch, "train_loss": avg_train_loss, "val_loss": avg_val_loss})

            # Early stopping check
            if avg_val_loss < self.best_loss - 1e-4:
                self.best_loss = avg_val_loss
                self.best_state = {k: v.cpu().clone() for k, v in self.model.state_dict().items()}
                patience_counter = 0
            else:
                patience_counter += 1
                if patience_counter >= self.patience:
                    break

        if self.best_state is not None:
            self.model.load_state_dict(self.best_state)
        return self


def build_student_sequences(df, label_map=None):
    """
    Constructs chronological sequences for each student across the 12 curriculum topics.
    Returns:
    - sequence_dict: {student_id: (sequence_array, topic_names, labels_array)}
    - flattened_features: list of (student_id, topic, temporal_feature_vector)
    """
    if label_map is None:
        label_map = {"Low Gap": 0, "Medium Gap": 1, "High Gap": 2}

    # Ensure data is sorted by student and curriculum sequence
    df_sorted = df.copy()
    if "quiz_accuracy" not in df_sorted.columns:
        df_sorted["quiz_accuracy"] = (df_sorted["correct_answers"] / df_sorted["total_questions"]) * 100.0
    if "engagement_score" not in df_sorted.columns:
        df_sorted["engagement_score"] = (
            df_sorted["videos_watched"] * 5 + df_sorted["lessons_completed"] * 5 + df_sorted["login_frequency"] * 5
        ).clip(0, 100)

    # Compute step delta
    df_sorted["score_delta_prev"] = df_sorted.groupby("student_id")["quiz_score"].diff().fillna(0.0)

    student_sequences = {}
    students = df_sorted["student_id"].unique()

    for sid in students:
        s_df = df_sorted[df_sorted["student_id"] == sid]
        topics = s_df["topic"].tolist()

        step_features = []
        labels = []
        for _, row in s_df.iterrows():
            step_feats = normalize_temporal_row(row.to_dict())
            step_features.append(step_feats)
            gap_cat = row.get("gap_category", "Medium Gap")
            labels.append(label_map.get(gap_cat, 1))

        student_sequences[sid] = {
            "features": np.array(step_features, dtype=np.float32),
            "topics": topics,
            "labels": np.array(labels, dtype=np.int64)
        }

    return student_sequences


def extract_gru_embeddings_for_all(model, student_sequences):
    """
    Runs trained GRU across all student sequences to extract temporal latent feature vectors h_t.
    Returns a dictionary: {(student_id, topic): np.array of shape (hidden_dim,)}
    """
    model.eval()
    embeddings = {}

    for sid, data in student_sequences.items():
        seq = torch.tensor(data["features"], dtype=torch.float32).unsqueeze(0)  # [1, S, D]
        with torch.no_grad():
            _, h_all = model(seq)  # [1, S, H]
            h_np = h_all.squeeze(0).cpu().numpy()

        for step, topic in enumerate(data["topics"]):
            embeddings[(sid, topic)] = h_np[step]

    return embeddings
