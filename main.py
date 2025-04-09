# main.py

from fastapi import FastAPI, Query
from fetcher import fetch_page, extract_text
from hasher import hash_content
from diff import is_changed
from spacy.lang.en import English
from collections import Counter
import json
import os

app = FastAPI()
nlp = English()
nlp.add_pipe("sentencizer")

# Load config
with open("config.json") as f:
    config = json.load(f)

stored_hashes = {}
ENTITIES_FILE = "entity_store.json"

# Load persistent entities
try:
    with open(ENTITIES_FILE, "r") as f:
        persistent_entities = json.load(f)
except:
    persistent_entities = {}

@app.on_event("shutdown")
def on_shutdown():
    print("🌙 Gracefully shutting down API server...")
    with open(ENTITIES_FILE, "w") as f:
        json.dump(persistent_entities, f, indent=2)

@app.get("/check")
def check_site(url: str = Query(..., description="Target FED site URL to monitor")):
    try:
        html = fetch_page(url)
        if not html:
            return {"status": "fail", "message": "Unable to fetch page."}

        text = extract_text(html)
        new_hash = hash_content(text)
        old_hash = stored_hashes.get(url)
        changed = is_changed(old_hash, new_hash)
        stored_hashes[url] = new_hash

        # Named Entity Recognition
        doc = nlp(text)
        entities = [t.text for t in doc if t.is_title and len(t.text) > 2]
        keywords = config.get("ner_keywords", [])
        matched_entities = [
            word for word in entities if any(k in word for k in keywords)
        ]
        summary = sorted(list(doc.sents), key=lambda s: len(s.text), reverse=True)[:3]

        persistent_entities[url] = list(set(matched_entities))

        return {
            "url": url,
            "changed": changed,
            "previous_hash": old_hash,
            "current_hash": new_hash,
            "summary": [s.text.strip() for s in summary],
            "entities": matched_entities,
        }
    except Exception as e:
        return {"error": str(e)}
