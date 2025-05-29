import spacy
from spacy.language import Language
from spacy.tokens import Span
from typing import List
import re

# Define custom entity types
FED_ENTITY_TYPES = {
    "FED_PRESIDENT": "Federal Reserve President",
    "FED_GOVERNOR": "Federal Reserve Governor",
    "FED_CHAIR": "Federal Reserve Chair",
    "FED_COMMITTEE": "Federal Reserve Committee",
    "FED_BANK": "Federal Reserve Bank",
    "FED_PROGRAM": "Federal Reserve Program",
    "FED_POLICY": "Federal Reserve Policy"
}

def fed_entity_recognizer(doc):
    """Custom entity recognizer for Federal Reserve entities."""
    matches = []
    
    # Add patterns for Federal Reserve entities
    patterns = [
        # Federal Reserve Bank Presidents
        r"\b(?:President|Governor|Chair)\s+of\s+the\s+Fed\b",
        r"\bFed\s+Bank\s+of\s+[A-Z][a-z]+\b",
        r"\bFederal\s+Reserve\s+Bank\s+of\s+[A-Z][a-z]+\b",
        r"\bFederal\s+Reserve\s+System\b",
        r"\bFOMC\b",  # Federal Open Market Committee
        r"\bFederal\s+Reserve\s+Committee\b",
        r"\bMonetary\s+Policy\b",
        r"\bInterest\s+Rate\s+Decision\b"
    ]
    
    for pattern in patterns:
        for match in re.finditer(pattern, doc.text):
            start, end = match.span()
            span = Span(doc, doc.char_span(start, end).start, doc.char_span(start, end).end, label="FED_ENTITY")
            matches.append(span)
    
    doc.ents = list(doc.ents) + matches
    return doc

# Register the component
@Language.factory("fed_entity_recognizer")
def create_fed_entity_recognizer(nlp, name):
    return fed_entity_recognizer
