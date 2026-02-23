"""
Entity Types:
- CAMPUS_LOCATION  : Named buildings (e.g. "Ellison Building")
- FACILITY_TYPE    : Generic facilities (e.g. "cafe", "gym")
- TIME_REFERENCE   : Time expressions (e.g. "today", "9am")
- EVENT_TYPE       : Event categories (e.g. "seminar", "open day")
"""

import spacy
import os
from typing import List, Dict

MODEL_PATH = os.path.join(os.path.dirname(__file__), "../../../data/processed/ner_model")


class NERExtractor:
    def __init__(self):
        self.nlp = None
        self._load_model()

    def _load_model(self):
        if os.path.exists(MODEL_PATH):
            self.nlp = spacy.load(MODEL_PATH)
        else:
            self.nlp = spacy.blank("en")

    def extract(self, query: str) -> List[Dict]:
        doc = self.nlp(query)
        return [{"text": ent.text, "label": ent.label_, "start": ent.start_char, "end": ent.end_char} for ent in doc.ents]

extractor = NERExtractor()