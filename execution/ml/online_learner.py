"""Online Incremental Learning feedback loop.

Updates user preference weights in real-time (< 1ms per update) whenever the user
corrects or confirms an AI triaging decision, enabling personalization without model retraining.
"""

from pathlib import Path
from typing import Any, Dict, Optional
import joblib
from pydantic import BaseModel, Field
from river import compose, feature_extraction, linear_model, metrics, preprocessing

from execution.core.config import settings


class FeedbackRecord(BaseModel):
    """User correction or confirmation data record."""

    email_id: str
    subject: str
    body: str
    predicted_score: float
    user_label: int = Field(..., description="1 = Important, 0 = Unimportant")
    feedback_reason: Optional[str] = None
    timestamp: float


class OnlineFeedbackLearner:
    """Incremental streaming learner adapting to human corrections."""

    def __init__(self, model_path: Optional[Path] = None):
        self.model_path = model_path or (settings.TEMP_DIR / "online_learner.joblib")
        self.metric = metrics.Accuracy()

        # River Streaming Pipeline: Text Bag-of-Words + TF-IDF + Logistic Regression
        self.pipeline = compose.Pipeline(
            ("tfidf", feature_extraction.TFIDF(stop_words=["the", "is", "at", "which", "on"])),
            ("scaler", preprocessing.StandardScaler()),
            ("clf", linear_model.LogisticRegression()),
        )
        self.update_count = 0

    def learn_one(self, text: str, label: int) -> float:
        """Incrementally update the online model with a single user feedback sample."""
        # 1. Update metric on the current sample before learning
        y_pred = self.pipeline.predict_one(text)
        if y_pred is not None:
            self.metric.update(y_true=bool(label), y_pred=bool(y_pred))

        # 2. Update model weights
        self.pipeline.learn_one(text, bool(label))
        self.update_count += 1

        # 3. Persist checkpoint every 5 updates
        if self.update_count % 5 == 0:
            self.save()

        # Return the updated probability for the positive class
        proba_dict = self.pipeline.predict_proba_one(text)
        return float(proba_dict.get(True, 0.5))

    def predict_one(self, text: str) -> float:
        """Predict the calibrated probability using the online personalized weights."""
        proba_dict = self.pipeline.predict_proba_one(text)
        return float(proba_dict.get(True, 0.5))

    def save(self) -> None:
        """Persist online model state."""
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "pipeline": self.pipeline,
                "metric": self.metric,
                "update_count": self.update_count,
            },
            self.model_path,
        )

    def load(self) -> bool:
        """Load online model state if exists."""
        if not self.model_path.exists():
            return False
        data = joblib.load(self.model_path)
        self.pipeline = data["pipeline"]
        self.metric = data["metric"]
        self.update_count = data["update_count"]
        return True


# Singleton instance
online_learner = OnlineFeedbackLearner()
