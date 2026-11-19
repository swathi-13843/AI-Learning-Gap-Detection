"""
Bayesian Knowledge Tracing (BKT) Module for EduGap AI.
Implements topic-level student knowledge mastery tracking using both pyBKT and
an exact vectorized mathematical BKT algorithm based on Corbett & Anderson (1995).

Tracks:
- Initial knowledge probability: P(L_0)
- Learning transition probability: P(T)
- Forgetting probability: P(F)
- Guess probability: P(G)
- Slip probability: P(S)

Estimates student latent mastery P(L_t) across chronological question responses
and generates topic mastery features for hybrid feature fusion.
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd
import joblib

try:
    from pyBKT.models import Model as PyBKTModel
    PYBKT_AVAILABLE = True
except Exception:
    PYBKT_AVAILABLE = False


class BayesianKnowledgeTracer:
    """
    Standard Bayesian Knowledge Tracing with optional forgetting extension.
    """

    def __init__(self, p_l0=0.25, p_trans=0.15, p_forget=0.03, p_guess=0.20, p_slip=0.10):
        self.default_params = {
            "p_l0": float(p_l0),
            "p_trans": float(p_trans),
            "p_forget": float(p_forget),
            "p_guess": float(p_guess),
            "p_slip": float(p_slip),
        }
        self.topic_params = {}

    def fit_topic_parameters(self, df_responses):
        """
        Fits or calibrates topic-specific BKT parameters from question-level responses.
        Expects DataFrame with: ['student_id', 'topic', 'correct']
        """
        if PYBKT_AVAILABLE and len(df_responses) > 50:
            try:
                # Prepare data format required by pyBKT
                bkt_df = df_responses.copy()
                bkt_df = bkt_df.rename(columns={
                    "student_id": "user_id",
                    "topic": "skill_name",
                    "correct": "correct"
                })
                if "order_id" not in bkt_df.columns:
                    bkt_df["order_id"] = np.arange(len(bkt_df))

                pybkt_model = PyBKTModel(seed=42, num_fits=2)
                pybkt_model.fit(data=bkt_df, skills=list(bkt_df["skill_name"].unique()))

                # Extract parameters per skill
                params_df = pybkt_model.params()
                for skill in bkt_df["skill_name"].unique():
                    try:
                        p_l0 = float(params_df.loc[(skill, "prior"), "value"])
                        p_trans = float(params_df.loc[(skill, "learns"), "value"])
                        p_guess = float(params_df.loc[(skill, "guesses"), "value"])
                        p_slip = float(params_df.loc[(skill, "slips"), "value"])
                        p_forget = float(params_df.loc[(skill, "forgets"), "value"]) if (skill, "forgets") in params_df.index else 0.03
                    except Exception:
                        p_l0, p_trans, p_guess, p_slip, p_forget = 0.25, 0.15, 0.20, 0.10, 0.03

                    self.topic_params[skill] = {
                        "p_l0": max(0.05, min(0.95, p_l0)),
                        "p_trans": max(0.01, min(0.60, p_trans)),
                        "p_forget": max(0.00, min(0.15, p_forget)),
                        "p_guess": max(0.05, min(0.40, p_guess)),
                        "p_slip": max(0.02, min(0.35, p_slip)),
                    }
                return self
            except Exception as e:
                print(f"[BKT Warning] pyBKT optimization fallback to analytical fitting: {e}")

        # Analytical calibration fallback per topic
        for topic, group in df_responses.groupby("topic"):
            acc = float(group["correct"].mean()) if len(group) > 0 else 0.60
            # Higher average accuracy reflects higher prior and learning rate
            p_l0 = float(np.clip(acc * 0.45, 0.15, 0.55))
            p_trans = float(np.clip(acc * 0.25, 0.08, 0.35))
            p_guess = float(np.clip((1.0 - acc) * 0.30, 0.10, 0.30))
            p_slip = float(np.clip((1.0 - acc) * 0.20, 0.05, 0.25))
            p_forget = 0.03

            self.topic_params[topic] = {
                "p_l0": p_l0,
                "p_trans": p_trans,
                "p_forget": p_forget,
                "p_guess": p_guess,
                "p_slip": p_slip,
            }
        return self

    def get_params_for_topic(self, topic):
        return self.topic_params.get(topic, self.default_params)

    def trace_responses(self, responses, topic=None):
        """
        Given a sequence of binary responses [1, 0, 1, 1, ...],
        returns the sequence of posterior knowledge probabilities P(L_t).
        """
        params = self.get_params_for_topic(topic)
        p_l0 = params["p_l0"]
        p_t = params["p_trans"]
        p_f = params.get("p_forget", 0.03)
        p_g = params["p_guess"]
        p_s = params["p_slip"]

        p_l = p_l0
        history = [p_l]

        for obs in responses:
            obs = int(obs)
            # Update knowledge given observation
            if obs == 1:
                numerator = p_l * (1.0 - p_s)
                denominator = numerator + (1.0 - p_l) * p_g
            else:
                numerator = p_l * p_s
                denominator = numerator + (1.0 - p_l) * (1.0 - p_g)

            if denominator <= 0:
                p_l_given_obs = p_l
            else:
                p_l_given_obs = numerator / denominator

            # Knowledge transition for next step with optional forgetting
            p_l = p_l_given_obs * (1.0 - p_f) + (1.0 - p_l_given_obs) * p_t
            p_l = float(np.clip(p_l, 0.001, 0.999))
            history.append(p_l)

        return history

    def predict_mastery_probability(self, responses, topic=None):
        """
        Returns the final posterior mastery probability P(L_T).
        """
        history = self.trace_responses(responses, topic)
        return history[-1]

    def extract_features_for_student_topic(self, quiz_score, total_questions=20, correct_answers=None, attempts=1, topic=None):
        """
        Extracts BKT feature vector for a student topic record.
        """
        if correct_answers is None:
            correct_answers = int(round(total_questions * (quiz_score / 100.0)))
        correct_answers = max(0, min(total_questions, int(correct_answers)))
        incorrect_answers = total_questions - correct_answers

        # Reconstruct response sequence reflecting overall correctness and attempt distribution
        # Evenly interleave correct and incorrect answers to simulate temporal trial
        seq = [1] * correct_answers + [0] * incorrect_answers
        # Deterministic shuffle for reproducibility based on score and attempts
        rng = np.random.RandomState(int(abs(quiz_score * 100 + attempts)) % 10000)
        rng.shuffle(seq)

        history = self.trace_responses(seq, topic)
        p_final = history[-1]
        p_init = history[0]
        learning_gain = p_final - p_init

        params = self.get_params_for_topic(topic)
        return {
            "bkt_mastery_prob": round(float(p_final), 4),
            "bkt_learning_gain": round(float(learning_gain), 4),
            "bkt_low_mastery_flag": int(p_final < 0.50),
            "bkt_slip_risk": round(float(params["p_slip"] * (1.0 - p_final)), 4),
            "bkt_guess_prob": round(float(params["p_guess"]), 4),
        }

    def save(self, filepath):
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"default_params": self.default_params, "topic_params": self.topic_params}, filepath)

    @classmethod
    def load(cls, filepath):
        tracer = cls()
        filepath = Path(filepath)
        if filepath.exists():
            data = joblib.load(filepath)
            tracer.default_params = data.get("default_params", tracer.default_params)
            tracer.topic_params = data.get("topic_params", {})
        return tracer


def build_response_trials_from_activity(activity_df):
    """
    Constructs synthetic yet grounded item-level response trials from aggregate activity data
    for BKT parameter calibration.
    """
    rows = []
    for idx, row in activity_df.iterrows():
        sid = row["student_id"]
        topic = row["topic"]
        tot = int(row.get("total_questions", 20))
        corr = int(row.get("correct_answers", round(tot * row["quiz_score"] / 100.0)))
        inc = tot - corr
        seq = [1] * corr + [0] * inc
        rng = np.random.RandomState(idx % 1000)
        rng.shuffle(seq)
        for t_step, ans in enumerate(seq):
            rows.append({
                "student_id": sid,
                "topic": topic,
                "step": t_step,
                "correct": ans
            })
    return pd.DataFrame(rows)
