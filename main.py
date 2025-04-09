# main.py

from fastapi import FastAPI, Query, HTTPException
from fetcher import fetch_page, extract_text, extract_main_content
from hasher import hash_content
from diff import is_changed
import spacy
from spacy.language import Language
from spacy.tokens import Span
from collections import Counter
import json
import os
import re
import uvicorn
from fastapi.responses import HTMLResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

# Define Pydantic models first
class EntityResponse(BaseModel):
    entity: str
    type: str
    count: int
    sources: List[str]

class PublicationResponse(BaseModel):
    name: str
    full_name: Optional[str] = None
    publishing_body: Optional[str] = None
    frequency: Optional[str] = None
    description: Optional[str] = None
    mentions: int

class FedEntity(BaseModel):
    text: str
    type: str
    full_name: Optional[str] = None
    title: Optional[str] = None
    organization: Optional[str] = None
    acronym: Optional[str] = None
    description: Optional[str] = None
    publishing_body: Optional[str] = None

class CheckResponse(BaseModel):
    url: str
    basic_entities: List[str]
    fed_entities: List[FedEntity]
    summary: str

app = FastAPI(title="FedLoad API", 
              description="Monitor Federal Reserve websites for content changes and extract entities")

# Initialize NLP
nlp = spacy.load("en_core_web_sm")

# Constants
CONFIG_FILE = "config.json"
ENTITIES_FILE = "entity_store.json"
FED_ENTITIES_FILE = "fed_entities.json"
DAILY_REPORT = "daily_report.html"
WEEKLY_SUMMARY = "weekly_summary.html"

print(f"[{datetime.now().isoformat()}] ====== FedLoad API Starting ======")

# Load config
try:
    print(f"[{datetime.now().isoformat()}] Loading configuration from {CONFIG_FILE}...")
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    
    # Get entity recognition configuration
    entity_recognition_config = config.get("entity_recognition", {})
    use_fed_entities = entity_recognition_config.get("use_fed_entities", True)
    enrich_existing_entities = entity_recognition_config.get("enrich_existing_entities", True)
    
    # Get monitoring configuration
    monitoring_config = config.get("monitoring", {})
    timeout_seconds = monitoring_config.get("timeout_seconds", 10)
    user_agent = monitoring_config.get("user_agent", "FedLoad Monitor/1.0")
    
    print(f"[{datetime.now().isoformat()}] Entity recognition: use_fed_entities={use_fed_entities}, enrich_existing={enrich_existing_entities}")
    print("Configuration loaded successfully")
except Exception as e:
    print(f"[{datetime.now().isoformat()}] Error loading configuration: {str(e)}")
    print(f"[{datetime.now().isoformat()}] Using default values for entity recognition")
    use_fed_entities = True
    enrich_existing_entities = True
    timeout_seconds = 10
    user_agent = "FedLoad Monitor/1.0"

# Load fed_entities.json for enhanced entity recognition
try:
    print(f"[{datetime.now().isoformat()}] Loading FED entities from {FED_ENTITIES_FILE}...")
    with open(FED_ENTITIES_FILE, "r") as f:
        fed_entities = json.load(f)
    print(f"[{datetime.now().isoformat()}] Loaded {len(fed_entities['people'])} people, {len(fed_entities['organizations'])} organizations, and {len(fed_entities['publications'])} publications")
except Exception as e:
    print(f"[{datetime.now().isoformat()}] Warning: Could not load {FED_ENTITIES_FILE}: {e}")
    fed_entities = {"people": [], "organizations": [], "publications": []}

# Create a custom component for FED entity recognition
@Language.component("fed_entity_recognizer")
def fed_entity_recognizer(doc):
    entities = []
    
    # Search for each person in the text
    for person in fed_entities.get("people", []):
        # Check full name
        name = person["name"]
        for match in find_all_occurrences(doc.text, name):
            entities.append((match, match + len(name), "FED_PERSON"))
        
        # Check aliases
        for alias in person.get("aliases", []):
            for match in find_all_occurrences(doc.text, alias):
                entities.append((match, match + len(alias), "FED_PERSON"))
    
    # Search for organizations
    for org in fed_entities.get("organizations", []):
        name = org["name"]
        for match in find_all_occurrences(doc.text, name):
            entities.append((match, match + len(name), "FED_ORG"))
        
        # Check acronyms
        acronym = org.get("acronym", "")
        if acronym:
            for match in find_all_occurrences(doc.text, acronym):
                entities.append((match, match + len(acronym), "FED_ORG"))
    
    # Search for publications - added FED_PUB type
    for pub in fed_entities.get("publications", []):
        # Check publication name
        name = pub["name"]
        for match in find_all_occurrences(doc.text, name):
            entities.append((match, match + len(name), "FED_PUB"))
        
        # Check full name
        full_name = pub.get("full_name", "")
        if full_name:
            for match in find_all_occurrences(doc.text, full_name):
                entities.append((match, match + len(full_name), "FED_PUB"))

    # Create Spans for the entities and add them to the document
    spans = []
    for start, end, label in entities:
        # Skip if span is already part of an entity
        if any(start >= e.start_char and end <= e.end_char for e in doc.ents):
            continue
        # Create and add the span
        try:
            span = Span(doc, doc.char_span(start, end).start, doc.char_span(start, end).end, label=label)
            spans.append(span)
        except Exception:
            continue
    
    if spans:
        try:
            doc.ents = list(doc.ents) + spans
        except Exception as e:
            print(f"Error adding entities: {e}")
    
    return doc

# Helper function to find all occurrences of a substring
def find_all_occurrences(text, substring):
    start = 0
    while True:
        start = text.find(substring, start)
        if start == -1:
            return
        yield start
        start += 1  # Move past this match

# Add the custom component to the spaCy pipeline
try:
    if use_fed_entities and "fed_entity_recognizer" not in nlp.pipe_names:
        nlp.add_pipe("fed_entity_recognizer", after="ner")
        print("Added fed_entity_recognizer to NLP pipeline")
except Exception as e:
    print(f"Error adding fed_entity_recognizer to pipeline: {e}")

# Function to enrich entities with additional information
def enrich_entity(ent):
    if ent.label_ == "FED_PERSON":
        for person in fed_entities.get("people", []):
            if person["name"] == ent.text or ent.text in person.get("aliases", []):
                return {
                    "text": ent.text,
                    "type": "person",
                    "position": person.get("position", ""),
                    "title": person.get("title", ""),
                    "organization": person.get("organization", ""),
                    "committees": person.get("committees", []),
                    "roles": person.get("roles", [])
                }
    
    elif ent.label_ == "FED_ORG":
        for org in fed_entities.get("organizations", []):
            if org["name"] == ent.text or org.get("acronym", "") == ent.text:
                return {
                    "text": ent.text,
                    "type": "organization",
                    "acronym": org.get("acronym", ""),
                    "district": org.get("district", ""),
                    "description": org.get("description", "")
                }
    
    elif ent.label_ == "FED_PUB":
        for pub in fed_entities.get("publications", []):
            if pub["name"] == ent.text or pub.get("full_name", "") == ent.text:
                return {
                    "text": ent.text,
                    "type": "publication",
                    "full_name": pub.get("full_name", ""),
                    "frequency": pub.get("frequency", ""),
                    "publishing_body": pub.get("publishing_body", ""),
                    "related_topics": pub.get("related_topics", [])
                }
    
    # Return basic entity info if no enrichment found
    return {
        "text": ent.text,
        "type": ent.label_
    }

stored_hashes = {}

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

@app.get("/check", response_model=CheckResponse)
async def check_url(url: str = Query(..., description="FED website URL to check")):
    if not re.match(r'^https?://.*\.gov', url):
        raise HTTPException(status_code=400, detail="URL must be a .gov site")
    
    try:
        # Use enhanced fetcher module
        from fetcher import extract_main_content
        
        # Fetch and extract content
        content_data = extract_main_content(url)
        
        if not content_data["text"]:
            raise HTTPException(status_code=500, detail="Failed to extract content from URL")
        
        # Process with NLP pipeline
        doc = nlp(content_data["text"])
        
        # Get basic entities (title-case words)
        basic_entities = []
        for sent in doc.sents:
            for token in sent:
                if token.is_alpha and token.is_title and len(token.text) > 1:
                    basic_entities.append(token.text)
        
        # Remove duplicates
        basic_entities = list(set(basic_entities))
        
        # Get FED-specific entities
        fed_entities = []
        for ent in doc.ents:
            if ent.label_ in ["FED_PERSON", "FED_ORG", "FED_PUB"]:
                entity_type = ent.label_.split("_")[1].lower()
                if entity_type == "person":
                    # Find the matching person in fed_entities.json
                    matching_person = None
                    if use_fed_entities:
                        for person in fed_entities.get("people", []):
                            if person["name"] == ent.text or ent.text in person.get("aliases", []):
                                matching_person = person
                                break
                    
                    fed_entities.append({
                        "text": ent.text,
                        "type": "person",
                        "full_name": matching_person["name"] if matching_person else ent.text,
                        "title": matching_person.get("title", "") if matching_person else "",
                        "organization": matching_person.get("organization", "") if matching_person else ""
                    })
                elif entity_type == "org":
                    # Find the matching organization in fed_entities.json
                    matching_org = None
                    if use_fed_entities:
                        for org in fed_entities.get("organizations", []):
                            if org["name"] == ent.text or org.get("acronym", "") == ent.text:
                                matching_org = org
                                break
                    
                    fed_entities.append({
                        "text": ent.text,
                        "type": "organization",
                        "full_name": matching_org["name"] if matching_org else ent.text,
                        "acronym": matching_org.get("acronym", "") if matching_org else "",
                        "description": matching_org.get("description", "") if matching_org else ""
                    })
                elif entity_type == "pub":
                    # Find the matching publication in fed_entities.json
                    matching_pub = None
                    if use_fed_entities:
                        for pub in fed_entities.get("publications", []):
                            if pub["name"] == ent.text or pub.get("full_name", "") == ent.text:
                                matching_pub = pub
                                break
                    
                    fed_entities.append({
                        "text": ent.text,
                        "type": "publication",
                        "full_name": matching_pub.get("full_name", ent.text) if matching_pub else ent.text,
                        "publishing_body": matching_pub.get("publishing_body", "") if matching_pub else "",
                        "description": matching_pub.get("description", "") if matching_pub else ""
                    })
        
        # Generate summary (use provided summary or longest sentence)
        summary = content_data.get("meta", {}).get("summary", "")
        if not summary:
            longest_sent = ""
            for sent in doc.sents:
                if len(sent.text) > len(longest_sent):
                    longest_sent = sent.text
            summary = longest_sent
        
        return {
            "url": url,
            "basic_entities": basic_entities,
            "fed_entities": fed_entities,
            "summary": summary
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking URL: {str(e)}")

@app.get("/entities", summary="Get all tracked entities")
def get_entities():
    return persistent_entities

@app.get("/publications", summary="Get all tracked FED publications")
def get_publications():
    all_publications = {}
    
    for url, entities in persistent_entities.items():
        if "fed_publications" in entities:
            for pub in entities["fed_publications"]:
                if isinstance(pub, dict) and "text" in pub:
                    pub_text = pub["text"]
                    if pub_text not in all_publications:
                        all_publications[pub_text] = {
                            "info": pub,
                            "mentioned_in": [url]
                        }
                    else:
                        if url not in all_publications[pub_text]["mentioned_in"]:
                            all_publications[pub_text]["mentioned_in"].append(url)
    
    return all_publications

@app.get("/config", summary="Get current configuration")
def get_config():
    """Return the current configuration (excluding sensitive information)"""
    try:
        with open(CONFIG_FILE) as f:
            config_data = json.load(f)
        
        # Remove any sensitive information if needed
        if "notifications" in config_data and "on_change" in config_data["notifications"]:
            if "email_recipients" in config_data["notifications"]["on_change"]:
                config_data["notifications"]["on_change"]["email_recipients"] = [
                    "***" if email else "" for email in config_data["notifications"]["on_change"]["email_recipients"]
                ]
        
        return config_data
    except Exception as e:
        return {"error": f"Failed to load configuration: {str(e)}"}

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "FedLoad API - Use /docs for API documentation"}
