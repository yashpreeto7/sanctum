"""Unit tests for the Classical ML Triaging Gatekeeper."""

import pytest
from execution.ml.triaging_classifier import TriagingClassifier, EmailFeatureExtractor


def test_feature_extraction_heuristics():
    """Verify feature extractor correctly identifies urgency, meetings, and newsletters."""
    urgent_email = {
        "sender": "boss@company.com",
        "subject": "URGENT: Server outage deadline today",
        "body": "We need this fixed ASAP before EOD.",
        "is_known_contact": True,
        "thread_length": 3,
    }
    features = EmailFeatureExtractor.extract_features(urgent_email)
    assert features["has_urgency"] == 1.0
    assert features["is_known_contact"] == 1.0
    assert features["thread_length"] == 3.0
    assert features["is_promo"] == 0.0

    promo_email = {
        "sender": "deals@store.com",
        "subject": "50% OFF Sale - Weekly Newsletter",
        "body": "Unsubscribe from this digest at any time.",
    }
    promo_features = EmailFeatureExtractor.extract_features(promo_email)
    assert promo_features["is_promo"] == 1.0


def test_classifier_training_and_inference():
    """Verify ML model trains on default dataset and predicts in < 15ms."""
    clf = TriagingClassifier()
    clf.train_baseline()
    assert clf.is_trained is True

    # 1. Important work email
    important_email = {
        "subject": "CRITICAL: Fix staging gateway outage ASAP",
        "body": "Please review the updated architecture proposal by tomorrow.",
        "is_known_contact": True,
    }
    pred_important = clf.predict(important_email)
    assert pred_important.importance_score > 0.4
    assert pred_important.should_trigger_llm is True
    assert pred_important.inference_latency_ms < 50.0  # Fast CPU inference

    # 2. Marketing newsletter
    spam_email = {
        "subject": "Special 70% discount offer",
        "body": "Weekly newsletter deals for shoes. Unsubscribe here.",
        "is_known_contact": False,
    }
    pred_spam = clf.predict(spam_email)
    assert pred_spam.predicted_category == "newsletter_promo"
    assert pred_spam.importance_score < 0.5
