"""Unit tests for the Online Feedback Learner."""

import pytest
from execution.ml.online_learner import OnlineFeedbackLearner


def test_online_feedback_incremental_update():
    """Verify online streaming learner updates weights on continuous feedback."""
    learner = OnlineFeedbackLearner()

    sample_text = "DocDispatch architecture sync with Rahul"

    initial_prob = learner.predict_one(sample_text)

    # User repeatedly marks this type of communication as high importance
    for _ in range(5):
        updated_prob = learner.learn_one(sample_text, label=1)

    # After positive feedback, the probability should have increased
    final_prob = learner.predict_one(sample_text)
    assert final_prob >= initial_prob
    assert learner.update_count == 5
