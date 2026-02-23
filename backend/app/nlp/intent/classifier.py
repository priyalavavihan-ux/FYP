"""
Intent Classes:
0 - DIRECTIONS
1 - FACILITY_HOURS
2 - PROXIMITY
3 - EVENTS
"""

import pickle
import os
from typing import Tuple

INTENT_LABELS = {
    0: "DIRECTIONS",
    1: "FACILITY_HOURS",
    2: "PROXIMITY",
    3: "EVENTS"
}

MODEL_PATH = os.path.join(os.path.dirname(__file__), "../../../../data/processed/intent_model.pkl")
VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), "../../../../data/processed/vectorizer.pkl")


class IntentClassifier:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self._load_model()

    def _load_model(self):
        if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
            with open(MODEL_PATH, "rb") as f:
                self.model = pickle.load(f)
            with open(VECTORIZER_PATH, "rb") as f:
                self.vectorizer = pickle.load(f)

    def predict(self, query: str) -> Tuple[str, float]:
        if self.model is None or self.vectorizer is None:
            raise RuntimeError("Intent model not trained yet. Run train_intent.py first.")
        features = self.vectorizer.transform([query])
        prediction = self.model.predict(features)[0]
        probabilities = self.model.predict_proba(features)[0]
        confidence = float(max(probabilities))
        intent = INTENT_LABELS[prediction]
        return intent, confidence

classifier = IntentClassifier()