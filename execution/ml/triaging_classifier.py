"""Sub-10ms Classical ML Triaging Gatekeeper for Inbound Communications.

Filters high-volume inbound emails/notifications using tabular metadata features + TF-IDF
vectorization, predicting calibrated importance and urgency scores on CPU without LLM overhead.
"""

import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import joblib
import numpy as np
from pydantic import BaseModel, Field
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.preprocessing import StandardScaler

from execution.core.config import settings


class TriagePrediction(BaseModel):
    """Structured output from the ML triaging gatekeeper."""

    importance_score: float = Field(..., ge=0.0, le=1.0, description="Predicted importance probability")
    urgency_score: float = Field(..., ge=0.0, le=1.0, description="Predicted urgency score")
    predicted_category: str = Field(..., description="Classification category")
    should_trigger_llm: bool = Field(..., description="Whether score exceeds threshold to invoke LangGraph")
    inference_latency_ms: float = Field(..., description="Execution latency in milliseconds")


class EmailFeatureExtractor:
    """Extracts numeric and textual heuristic features from email metadata and body."""

    URGENCY_KEYWORDS = re.compile(r"\b(urgent|asap|deadline|immediately|eod|action required|critical|important)\b", re.I)
    MEETING_KEYWORDS = re.compile(r"\b(meeting|zoom|google meet|calendar|interview|sync|reschedule|call)\b", re.I)
    FINANCIAL_KEYWORDS = re.compile(r"\b(invoice|receipt|payment|bill|expense|salary|subscription|charged)\b", re.I)
    NEWSLETTER_KEYWORDS = re.compile(r"\b(unsubscribe|newsletter|digest|view in browser|weekly roundup|offer|sale)\b", re.I)

    @classmethod
    def extract_features(cls, email: Dict[str, Any]) -> Dict[str, float]:
        sender = str(email.get("sender", "")).lower()
        subject = str(email.get("subject", ""))
        body = str(email.get("body", ""))
        full_text = f"{subject} {body}"

        char_len = len(full_text)
        has_urgency = 1.0 if cls.URGENCY_KEYWORDS.search(full_text) else 0.0
        has_meeting = 1.0 if cls.MEETING_KEYWORDS.search(full_text) else 0.0
        has_finance = 1.0 if cls.FINANCIAL_KEYWORDS.search(full_text) else 0.0
        is_promo = 1.0 if cls.NEWSLETTER_KEYWORDS.search(full_text) else 0.0
        is_known_contact = 1.0 if email.get("is_known_contact", False) else 0.0
        thread_length = float(email.get("thread_length", 1))

        return {
            "char_len": float(char_len),
            "has_urgency": has_urgency,
            "has_meeting": has_meeting,
            "has_finance": has_finance,
            "is_promo": is_promo,
            "is_known_contact": is_known_contact,
            "thread_length": thread_length,
        }


class TriagingClassifier:
    """Fast ML Gatekeeper model for filtering and triaging."""

    CATEGORIES = ["work_project", "meeting_schedule", "financial", "newsletter_promo", "spam_noise"]

    def __init__(self, model_path: Optional[Path] = None):
        self.model_path = model_path or (settings.TEMP_DIR / "triaging_classifier.joblib")
        self.tfidf_vectorizer = TfidfVectorizer(max_features=500, stop_words="english")
        self.importance_clf = LogisticRegression(class_weight="balanced", random_state=42)
        self.is_trained = False

    def train_baseline(self, synthetic_samples: Optional[List[Dict[str, Any]]] = None) -> None:
        """Trains the initial baseline model using a curated dataset of emails."""
        samples = synthetic_samples or self._generate_default_dataset()

        texts = [f"{s.get('subject', '')} {s.get('body', '')}" for s in samples]
        labels = [s.get("is_important", 0) for s in samples]

        X_tfidf = self.tfidf_vectorizer.fit_transform(texts)
        self.importance_clf.fit(X_tfidf, labels)
        self.is_trained = True
        self.save()

    def predict(self, email: Dict[str, Any], importance_threshold: float = 0.5) -> TriagePrediction:
        """Evaluates an email and returns structured predictions in < 5ms."""
        start_time = time.perf_counter()

        if not self.is_trained:
            if self.model_path.exists():
                self.load()
            else:
                self.train_baseline()

        subject = str(email.get("subject", ""))
        body = str(email.get("body", ""))
        text = f"{subject} {body}"

        X_vec = self.tfidf_vectorizer.transform([text])
        proba = float(self.importance_clf.predict_proba(X_vec)[0][1])

        # Urgency calculation heuristic combined with model score
        features = EmailFeatureExtractor.extract_features(email)
        urgency = min(1.0, (proba * 0.5) + (features["has_urgency"] * 0.4) + (features["has_meeting"] * 0.2))

        # Category determination
        if features["is_promo"] > 0 and proba < 0.6:
            category = "newsletter_promo"
        elif features["has_meeting"] > 0:
            category = "meeting_schedule"
        elif features["has_finance"] > 0:
            category = "financial"
        elif proba >= 0.5:
            category = "work_project"
        else:
            category = "spam_noise"

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        return TriagePrediction(
            importance_score=round(proba, 4),
            urgency_score=round(urgency, 4),
            predicted_category=category,
            should_trigger_llm=(proba >= importance_threshold or urgency >= 0.7),
            inference_latency_ms=round(latency_ms, 3),
        )

    def save(self) -> None:
        """Persist model and vectorizer."""
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "tfidf": self.tfidf_vectorizer,
                "clf": self.importance_clf,
            },
            self.model_path,
        )

    def load(self) -> None:
        """Load trained model."""
        data = joblib.load(self.model_path)
        self.tfidf_vectorizer = data["tfidf"]
        self.importance_clf = data["clf"]
        self.is_trained = True

    def _generate_default_dataset(self) -> List[Dict[str, Any]]:
        """Curated synthetic training dataset covering personal, work, newsletters, and meetings."""
        return [
            {"subject": "URGENT: Production API Gateway Outage", "body": "The staging gateway crashed. Need a fix ASAP.", "is_important": 1},
            {"subject": "Interview Confirmation: AI Systems Engineer", "body": "Your interview is scheduled for tomorrow at 3 PM on Google Meet.", "is_important": 1},
            {"subject": "Updated DocDispatch Proposal Review", "body": "Please find attached the revised system architecture notes.", "is_important": 1},
            {"subject": "Invoice #10492 for Cloud Infrastructure", "body": "Your monthly compute charges are ready for review.", "is_important": 1},
            {"subject": "Can we sync regarding the RAG evaluation dataset?", "body": "Let me know when you have 15 minutes today.", "is_important": 1},
            {"subject": "70% OFF Cyber Monday Deals!", "body": "Exclusive discounts on shoes and clothing. Unsubscribe here.", "is_important": 0},
            {"subject": "Weekly Tech Digest #48", "body": "Here are the top articles from Hacker News this week. View in browser.", "is_important": 0},
            {"subject": "Your subscription receipt", "body": "Thank you for using Streaming Service. Transaction complete.", "is_important": 0},
            {"subject": "Claim your free reward points", "body": "Click here to win a gift card now. Special promotion.", "is_important": 0},
            {"subject": "Daily Newsletter: Markets Today", "body": "Stock market summary for August 26. Manage notifications.", "is_important": 0},
        ]


# Singleton instance
triaging_classifier = TriagingClassifier()
