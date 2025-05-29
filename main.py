# main.py

from fastapi import FastAPI, Query, HTTPException, Response
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
from fetcher import fetch_page, extract_text, extract_main_content
from hasher import hash_content
from diff import is_changed
import spacy
from spacy.language import Language
from spacy.tokens import Span
from collections import Counter
import os
import re
import uvicorn
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
from config_log import setup_logging
from config_manager import ConfigManager
import json
import platform

# Constants
CONFIG_FILE = "config.json"
ENTITIES_FILE = "entity_store.json"
FED_ENTITIES_FILE = "fed_entities.json"
DAILY_REPORT = "daily_report.html"
WEEKLY_SUMMARY = "weekly_summary.html"

# Configuration
try:
    config_manager = ConfigManager(CONFIG_FILE)
    logger = setup_logging(config_manager=config_manager)
    config = config_manager.config
except Exception as e:
    logger.error(f"Error loading configuration: {e}")
    raise

# Get configuration settings
entity_recognition_config = config.get("entity_recognition", {})
ner_enabled = entity_recognition_config.get("enabled", False)
use_fed_entities = entity_recognition_config.get("use_fed_entities", True)
enrich_existing_entities = entity_recognition_config.get("enrich_existing_entities", True)

# Get monitoring configuration
monitoring_config = config.get("monitoring", {})
timeout_seconds = monitoring_config.get("timeout_seconds", 10)
user_agent = monitoring_config.get("user_agent", "FedLoad Monitor/1.0")
hash_algorithm = monitoring_config.get("content_hash_algorithm", "md5")
hash_check_initial_bytes = monitoring_config.get("hash_check_initial_bytes", 512)
max_content_size_mb = monitoring_config.get("max_content_size_mb", 50)

# Get URL filtering configuration
url_filtering_config = monitoring_config.get("url_filtering", {})
url_filtering_enabled = url_filtering_config.get("enabled", False)
require_gov_tld = url_filtering_config.get("require_gov_tld", False)
allowed_tlds = url_filtering_config.get("allowed_tlds", [])
blocked_tlds = url_filtering_config.get("blocked_tlds", [])
allowed_domains = url_filtering_config.get("allowed_domains", [])
blocked_domains = url_filtering_config.get("blocked_domains", [])

logger.info(f"Entity recognition: enabled={ner_enabled}, use_fed_entities={use_fed_entities}, enrich_existing={enrich_existing_entities}")
logger.info(f"Monitoring: hash_algorithm={hash_algorithm}, initial_bytes={hash_check_initial_bytes}, max_size={max_content_size_mb}MB")
logger.info(f"URL filtering: enabled={url_filtering_enabled}, require_gov_tld={require_gov_tld}")
logger.info("Configuration loaded successfully")

# Initialize NLP pipeline
nlp = None

# Load persistent entities
try:
    with open("entities.json", "r") as f:
        persistent_entities = json.load(f)
except FileNotFoundError:
    logger.info("No entities.json found, starting with empty entities")
    persistent_entities = {}
except Exception as e:
    logger.error(f"Error loading entities.json: {e}")
    persistent_entities = {}

# Load fed_entities.json for enhanced entity recognition
try:
    logger.info(f"Loading FED entities from {FED_ENTITIES_FILE}...")
    with open(FED_ENTITIES_FILE, "r") as f:
        fed_entities = json.load(f)
    logger.info(f"Loaded {len(fed_entities['people'])} people, {len(fed_entities['organizations'])} organizations, and {len(fed_entities['publications'])} publications")
except Exception as e:
    logger.warning(f"Could not load {FED_ENTITIES_FILE}: {e}")
    fed_entities = {"people": [], "organizations": [], "publications": []}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global nlp
    logger.info("Starting up application...")
    logger.info(f"Registered routes: {app.routes}")
    
    # Only load spaCy if NER is enabled
    if ner_enabled:
        try:
            nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy model loaded successfully")
            
            # Add custom entity recognizer
            if use_fed_entities and "fed_entity_recognizer" not in nlp.pipe_names:
                nlp.add_pipe("fed_entity_recognizer", after="ner")
                logger.info("Added fed_entity_recognizer to pipeline")
        except Exception as e:
            logger.error(f"Error initializing Spacy pipeline: {e}")
            raise
    else:
        logger.info("NER is disabled - skipping spaCy initialization")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    try:
        with open("entities.json", "w") as f:
            json.dump(persistent_entities, f, indent=2)
        logger.info("Saved entities to entities.json")
    except Exception as e:
        logger.error(f"Error saving entities: {e}")
    
    if nlp:
        nlp = None

# Initialize app with lifespan
app = FastAPI(
    title="FedLoad API", 
    description="Monitor Federal Reserve websites for content changes and extract entities",
    lifespan=lifespan
)

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

# Add health check endpoint
@app.get("/health")
async def health_check():
    """Check the health of the application and Spacy installation."""
    logger.info("Health check endpoint called")
    try:
        import spacy
        spacy_version = spacy.__version__
        model_installed = "en_core_web_sm" in spacy.info().models
        return {
            "status": "healthy",
            "spacy_version": spacy_version,
            "model_installed": model_installed,
            "python_version": platform.python_version()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

# Add API documentation endpoints
@app.get("/docs", include_in_schema=False)
async def redirect_docs():
    """Redirect to FastAPI's auto-generated API docs"""
    return Response("docs/index.html", media_type="text/html")

@app.get("/doc", include_in_schema=False)
@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """Redirect /doc and / to FastAPI's auto-generated API docs"""
    return RedirectResponse(url="/docs")

# Add root endpoint
@app.get("/api")
async def root():
    return {"message": "FedLoad API - Use /docs for API documentation"}

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
def find_all_occurrences(text: str, substring: str) -> list[int]:
    """Find all occurrences of a substring in a text.
    
    Args:
        text (str): The text to search in
        substring (str): The substring to find
        
    Returns:
        list[int]: List of start positions of all occurrences
    """
    start = 0
    positions = []
    while True:
        start = text.find(substring, start)
        if start == -1:
            break
        positions.append(start)
        start += 1  # Move past this match
    return positions

# Function to enrich entities with additional information
def enrich_entity(ent):
    """Enrich entity with additional information based on its type."""
    if not nlp:
        logger.error("Spacy pipeline not initialized")
        return ent

    # Get entity text and type
    text = ent.text
    entity_type = ent.label_
    
    # Initialize enrichment data
    enrichment_data = {
        "full_name": None,
        "title": None,
        "organization": None,
        "acronym": None,
        "description": None,
        "publishing_body": None
    }

    # Add basic enrichment based on entity type
    if entity_type == "FED_PRESIDENT":
        enrichment_data["title"] = "President"
        enrichment_data["organization"] = "Federal Reserve"
    elif entity_type == "FED_GOVERNOR":
        enrichment_data["title"] = "Governor"
        enrichment_data["organization"] = "Federal Reserve"
    elif entity_type == "FED_CHAIR":
        enrichment_data["title"] = "Chair"
        enrichment_data["organization"] = "Federal Reserve"
    elif entity_type == "FED_COMMITTEE":
        enrichment_data["organization"] = "Federal Reserve"
    elif entity_type == "FED_BANK":
        enrichment_data["organization"] = "Federal Reserve"
    elif entity_type == "FED_PROGRAM":
        enrichment_data["organization"] = "Federal Reserve"
    elif entity_type == "FED_POLICY":
        enrichment_data["organization"] = "Federal Reserve"

    # Add to entity data
    for key, value in enrichment_data.items():
        if value is not None:
            setattr(ent._, key, value)

    return ent

stored_hashes = {}

@app.get("/check", response_model=CheckResponse)
async def check_url(url: str = Query(..., description="FED website URL to check")):
    logger.info(f"Received check request for URL: {url}")
    
    # TODO: Implement comprehensive URL filtering system
    # - Add whitelist/blacklist for TLDs (e.g., .gov, .edu, .org)
    # - Add domain whitelist/blacklist
    # - Add path pattern filtering
    # - Add protection against malicious URLs and DNS attacks
    # - Implement OWASP URL validation checks
    # - Add rate limiting per domain
    
    # URL filtering (optional, disabled by default)
    if url_filtering_enabled:
        # Check GOV TLD requirement if enabled
        if require_gov_tld and not re.match(r'^https?://.*\.gov', url):
            logger.warning(f"Invalid URL format: {url} (GOV TLD required)")
            raise HTTPException(status_code=400, detail="URL must be a .gov site")
        
        # Check blocked TLDs
        for blocked_tld in blocked_tlds:
            if blocked_tld in url:
                logger.warning(f"Blocked TLD detected: {url} contains {blocked_tld}")
                raise HTTPException(status_code=400, detail=f"TLD {blocked_tld} is not allowed")
        
        # Check blocked domains
        for blocked_domain in blocked_domains:
            if blocked_domain in url:
                logger.warning(f"Blocked domain detected: {url} contains {blocked_domain}")
                raise HTTPException(status_code=400, detail=f"Domain {blocked_domain} is not allowed")
    
    try:
        # Use enhanced fetcher module
        from fetcher import extract_main_content
        logger.info("Fetching content from URL...")
        
        # Fetch and extract content
        content_data = extract_main_content(url)
        
        if not content_data["text"]:
            logger.error(f"Failed to extract content from URL: {url}")
            raise HTTPException(status_code=500, detail="Failed to extract content from URL")
        
        # Initialize empty results
        basic_entities = []
        fed_entities_list = []
        summary = content_data.get("meta", {}).get("summary", "")
        
        # Only perform NER if enabled
        if ner_enabled:
            # Process with NLP pipeline
            if not nlp:
                logger.error("Spacy pipeline not initialized")
                raise HTTPException(status_code=500, detail="Spacy pipeline not initialized")
            
            logger.info("Processing text with NLP pipeline...")
            doc = nlp(content_data["text"])
            
            # Get basic entities (title-case words)
            for sent in doc.sents:
                for token in sent:
                    if token.is_alpha and token.is_title and len(token.text) > 1:
                        basic_entities.append(token.text)
            
            # Remove duplicates
            basic_entities = list(set(basic_entities))
            
            # Get FED-specific entities
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
                        
                        fed_entities_list.append({
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
                        
                        fed_entities_list.append({
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
                        
                        fed_entities_list.append({
                            "text": ent.text,
                            "type": "publication",
                            "full_name": matching_pub.get("full_name", ent.text) if matching_pub else ent.text,
                            "publishing_body": matching_pub.get("publishing_body", "") if matching_pub else "",
                            "description": matching_pub.get("description", "") if matching_pub else ""
                        })
            
            # Generate summary using NLP if no summary available
            if not summary:
                longest_sent = ""
                for sent in doc.sents:
                    if len(sent.text) > len(longest_sent):
                        longest_sent = sent.text
                summary = longest_sent
        else:
            logger.info("NER is disabled - returning content without entity extraction")
            # Generate simple summary without NLP
            if not summary:
                # Use first sentence or first 200 characters
                text = content_data["text"]
                sentences = text.split('. ')
                if sentences:
                    summary = sentences[0] + ('.' if not sentences[0].endswith('.') else '')
                else:
                    summary = text[:200] + ('...' if len(text) > 200 else '')
        
        return {
            "url": url,
            "basic_entities": basic_entities,
            "fed_entities": fed_entities_list,
            "summary": summary
        }
    
    except ImportError as e:
        logger.error(f"Import error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Import error: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing URL {url}: {str(e)}")
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

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
