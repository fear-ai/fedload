import json
import time
import os
import signal
import sys
import schedule
from datetime import datetime, time as datetime_time
from threading import Event
import hashlib
import requests
from bs4 import BeautifulSoup
import re

# File paths
SITES_FILE = "tracked_sites.json"
CONFIG_FILE = "config.json"
LOG_FILE = "change_log.json"
ENTITY_STORE = "entity_store.json"
FED_ENTITIES_FILE = "fed_entities.json"
DAILY_REPORT = "daily_report.html"
WEEKLY_SUMMARY = "weekly_summary.html"

# Default values
DEFAULT_CHECK_FREQUENCY = 30  # minutes

# Load configuration
try:
    print(f"[{datetime.now().isoformat()}] Loading configuration from {CONFIG_FILE}...")
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    
    # Get check frequency from config
    check_frequency = config.get("scheduling", {}).get("check_frequency_minutes", DEFAULT_CHECK_FREQUENCY)
    print(f"[{datetime.now().isoformat()}] Check frequency set to {check_frequency} minutes")
    
    # Get report generation settings
    daily_report_config = config.get("scheduling", {}).get("report_generation", {}).get("daily_report", {})
    daily_report_enabled = daily_report_config.get("enabled", True)
    daily_report_time = daily_report_config.get("time", "00:00")
    
    weekly_summary_config = config.get("scheduling", {}).get("report_generation", {}).get("weekly_summary", {})
    weekly_summary_enabled = weekly_summary_config.get("enabled", False)
    weekly_summary_day = weekly_summary_config.get("day", "Monday")
    weekly_summary_time = weekly_summary_config.get("time", "06:00")
    
    print(f"[{datetime.now().isoformat()}] Daily report generation: {'enabled' if daily_report_enabled else 'disabled'}, time: {daily_report_time}")
    print(f"[{datetime.now().isoformat()}] Weekly summary generation: {'enabled' if weekly_summary_enabled else 'disabled'}, day: {weekly_summary_day}, time: {weekly_summary_time}")
    
except Exception as e:
    print(f"[{datetime.now().isoformat()}] Error loading configuration: {str(e)}")
    print(f"[{datetime.now().isoformat()}] Using default values")
    check_frequency = DEFAULT_CHECK_FREQUENCY
    daily_report_enabled = True
    daily_report_time = "00:00"
    weekly_summary_enabled = False
    weekly_summary_day = "Monday"
    weekly_summary_time = "06:00"

# Initialize NLP pipeline
try:
    import spacy
    print(f"[{datetime.now().isoformat()}] Loading spaCy model 'en_core_web_sm'...")
    nlp = spacy.load("en_core_web_sm")
    print(f"[{datetime.now().isoformat()}] spaCy model loaded successfully")
    spacy_available = True
except Exception as e:
    print(f"[{datetime.now().isoformat()}] ERROR: Could not load spaCy model: {str(e)}")
    print(f"[{datetime.now().isoformat()}] SOLUTION: Please run 'python -m spacy download en_core_web_sm'")
    print(f"[{datetime.now().isoformat()}] Continuing with limited functionality - entity recognition will be simplified")
    spacy_available = False

# Graceful exit flag
exit_event = Event()

# Load tracked sites
def load_sites():
    try:
        with open(SITES_FILE, 'r') as f:
            data = json.load(f)
            # The tracked_sites.json file has a "sites" array of URL strings
            sites = data.get("sites", [])
            print(f"[{datetime.now().isoformat()}] Loaded {len(sites)} sites to monitor")
            return sites
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] Error loading sites: {str(e)}")
        return []

# Load entity store or create if not exists
def load_entity_store():
    try:
        with open(ENTITY_STORE, 'r') as f:
            data = json.load(f)
            # Ensure the data has the required structure
            if "entities" not in data:
                data["entities"] = {}
            return data
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] Creating new entity store (no existing file or error: {str(e)})")
        return {"entities": {}}

# Save entity store
def save_entity_store(entity_store):
    with open(ENTITY_STORE, 'w') as f:
        json.dump(entity_store, f, indent=2)

# Load change log or create if not exists
def load_change_log():
    try:
        with open(LOG_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

# Load Fed entities
def load_fed_entities():
    try:
        with open(FED_ENTITIES_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] Error loading Fed entities: {str(e)}")
        return {"people": [], "organizations": [], "publications": [], "events": [], "topics": []}

# Signal handler for graceful exit
def signal_handler(sig, frame):
    print(f"\n[{datetime.now().isoformat()}] Received shutdown signal. Saving data and stopping scheduler...")
    exit_event.set()
    # Force exit after 10 seconds if graceful shutdown doesn't complete
    time.sleep(10)
    print(f"[{datetime.now().isoformat()}] Forcing exit...")
    sys.exit(0)

# Register signal handler
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Fetch content from a URL
def fetch_url(url):
    try:
        from fetcher import fetch_page, extract_text, extract_main_content
        print(f"[{datetime.now().isoformat()}] Fetching content from {url}")
        
        # Use the enhanced content extraction
        content_data = extract_main_content(url)
        if not content_data["text"]:
            return None
            
        # Return the extracted text content
        return content_data["text"]
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] ERROR - Error fetching {url}: {str(e)}")
        
        # Fall back to basic fetching if the enhanced fetcher fails
        try:
            headers = {
                "User-Agent": config.get("monitoring", {}).get("user_agent", "FedLoad Monitor/1.0")
            }
            timeout = config.get("monitoring", {}).get("timeout_seconds", 30)  # Increased default timeout
            print(f"[{datetime.now().isoformat()}] Using fallback fetcher with timeout={timeout}s")
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract text content
            for script in soup(["script", "style"]):
                script.extract()
            
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text
        except requests.exceptions.Timeout:
            timestamp = datetime.now().isoformat()
            error_msg = f"{timestamp} - ERROR - Error fetching HTTP URL {url}: Read timed out. (read timeout={timeout})"
            print(error_msg)
            return None
        except requests.exceptions.RequestException as re:
            timestamp = datetime.now().isoformat()
            error_msg = f"{timestamp} - ERROR - Error with fallback fetching {url}: {str(re)}"
            print(error_msg)
            return None
        except Exception as e:
            timestamp = datetime.now().isoformat()
            error_msg = f"{timestamp} - ERROR - Unexpected error fetching {url}: {str(e)}"
            print(error_msg)
            return None

# Calculate hash of content
def hash_content(content):
    algorithm = config.get("monitoring", {}).get("content_hash_algorithm", "sha256")
    if algorithm == "sha256":
        return hashlib.sha256(content.encode()).hexdigest()
    elif algorithm == "md5":
        return hashlib.md5(content.encode()).hexdigest()
    else:
        # Default to sha256
        return hashlib.sha256(content.encode()).hexdigest()

# Simple entity extraction if spaCy is not available
def extract_entities_simple(text):
    # A simple regex pattern to find title-cased words (names, organizations, etc.)
    pattern = r'\b[A-Z][a-z]+\b'
    entities = re.findall(pattern, text)
    return list(set(entities))  # Remove duplicates

# Check a site for changes
def check_site(url, entity_store):
    # Ensure entity_store has the proper structure
    if "entities" not in entity_store:
        entity_store["entities"] = {}
    
    # Get current content
    content = fetch_url(url)
    if not content:
        return False, None, None, [], []
    
    # Calculate hash
    new_hash = hash_content(content)
    
    # Get stored hash
    old_hash = entity_store.get("entities", {}).get(url, {}).get("hash", None)
    
    # Check if content has changed
    changed = old_hash != new_hash
    
    # Process text with NLP if changed
    entities = []
    fed_entities = []
    if changed:
        if spacy_available:
            doc = nlp(content)
            
            # Extract basic entities (title-case words)
            for sent in doc.sents:
                for token in sent:
                    if token.is_alpha and token.is_title and len(token.text) > 1:
                        entities.append(token.text)
            
            # Remove duplicates
            entities = list(set(entities))
        else:
            # Use simple entity extraction
            entities = extract_entities_simple(content)
        
        # Extract Fed-specific entities
        fed_entities = extract_fed_entities(content)
        
        # Store hash and entities
        if url not in entity_store["entities"]:
            entity_store["entities"][url] = {"hash": new_hash, "entities": entities, "fed_entities": fed_entities}
        else:
            entity_store["entities"][url]["hash"] = new_hash
            entity_store["entities"][url]["entities"] = entities
            entity_store["entities"][url]["fed_entities"] = fed_entities
    
    return changed, old_hash, new_hash, entities, fed_entities

# Extract Fed-specific entities from text
def extract_fed_entities(text):
    fed_entities = []
    fed_data = load_fed_entities()
    
    # Check for people
    for person in fed_data.get("people", []):
        name = person["name"]
        aliases = person.get("aliases", [])
        all_names = [name] + aliases
        
        for name_variant in all_names:
            if name_variant in text:
                fed_entities.append({
                    "text": name_variant,
                    "type": "person",
                    "full_name": person["name"],
                    "title": person.get("title", ""),
                    "organization": person.get("organization", "")
                })
                break
    
    # Check for organizations
    for org in fed_data.get("organizations", []):
        name = org["name"]
        acronym = org.get("acronym", "")
        
        if name in text or (acronym and acronym in text):
            found_text = name if name in text else acronym
            fed_entities.append({
                "text": found_text,
                "type": "organization",
                "full_name": org["name"],
                "acronym": org.get("acronym", ""),
                "description": org.get("description", "")
            })
    
    # Check for publications
    for pub in fed_data.get("publications", []):
        name = pub["name"]
        full_name = pub.get("full_name", "")
        
        if name in text or (full_name and full_name in text):
            found_text = name if name in text else full_name
            fed_entities.append({
                "text": found_text,
                "type": "publication",
                "full_name": pub.get("full_name", name),
                "publishing_body": pub.get("publishing_body", ""),
                "description": pub.get("description", "")
            })
    
    return fed_entities

# Check all sites
def check_all_sites():
    print(f"[{datetime.now().isoformat()}] Starting site checks...")
    sites = load_sites()
    entity_store = load_entity_store()
    log_data = load_change_log()
    
    # Ensure entity_store has the proper structure
    if "entities" not in entity_store:
        entity_store["entities"] = {}
    
    changes_detected = 0
    sites_checked = 0
    sites_errored = 0
    
    for url in sites:
        if not url:
            continue
        
        try:
            sites_checked += 1
            print(f"[{datetime.now().isoformat()}] Checking {url}")
            changed, old_hash, new_hash, matched_entities, fed_entities_found = check_site(url, entity_store)
            
            if changed:
                changes_detected += 1
                print(f"[{datetime.now().isoformat()}] Changes detected on {url}")
                print(f"[{datetime.now().isoformat()}] Found {len(matched_entities)} basic entities and {len(fed_entities_found)} Fed-specific entities")
                
                # Log the change
                log_entry = {
                    "url": url,
                    "time": datetime.now().isoformat(),
                    "changed": True,
                    "old_hash": old_hash,
                    "new_hash": new_hash,
                    "entities_found": {
                        "basic": matched_entities,
                        "fed_people": [e["text"] for e in fed_entities_found if e["type"] == "person"],
                        "fed_organizations": [e["text"] for e in fed_entities_found if e["type"] == "organization"],
                        "fed_publications": [e["text"] for e in fed_entities_found if e["type"] == "publication"]
                    }
                }
                log_data.append(log_entry)
        except Exception as e:
            sites_errored += 1
            print(f"[{datetime.now().isoformat()}] ERROR checking {url}: {str(e)}")
            # Log the error
            log_entry = {
                "url": url,
                "time": datetime.now().isoformat(),
                "changed": False,
                "error": str(e)
            }
            log_data.append(log_entry)
            continue
    
    # Save entity store
    save_entity_store(entity_store)
    
    # Save log
    with open(LOG_FILE, 'w') as f:
        json.dump(log_data, f, indent=2)
    
    print(f"[{datetime.now().isoformat()}] Site check summary:")
    print(f"[{datetime.now().isoformat()}] - Total sites checked: {sites_checked}")
    print(f"[{datetime.now().isoformat()}] - Sites with changes: {changes_detected}")
    print(f"[{datetime.now().isoformat()}] - Sites with errors: {sites_errored}")
    print(f"[{datetime.now().isoformat()}] Completed site checks.")
    return changes_detected

# Generate daily report
def generate_daily_report():
    print(f"[{datetime.now().isoformat()}] Generating daily report...")
    log_data = load_change_log()
    entity_store = load_entity_store()
    
    # Ensure entity_store has the proper structure
    if "entities" not in entity_store:
        entity_store["entities"] = {}
    
    # Filter logs for the last 24 hours
    now = datetime.now()
    recent_logs = [log for log in log_data if (now - datetime.fromisoformat(log["time"].replace("Z", ""))).days < 1]
    
    # Count mentions of Fed entities
    people_mentions = {}
    org_mentions = {}
    pub_mentions = {}
    
    for log in recent_logs:
        for person in log["entities_found"].get("fed_people", []):
            people_mentions[person] = people_mentions.get(person, 0) + 1
        
        for org in log["entities_found"].get("fed_organizations", []):
            org_mentions[org] = org_mentions.get(org, 0) + 1
        
        for pub in log["entities_found"].get("fed_publications", []):
            pub_mentions[pub] = pub_mentions.get(pub, 0) + 1
    
    # Sort by frequency
    people_sorted = sorted(people_mentions.items(), key=lambda x: x[1], reverse=True)
    org_sorted = sorted(org_mentions.items(), key=lambda x: x[1], reverse=True)
    pub_sorted = sorted(pub_mentions.items(), key=lambda x: x[1], reverse=True)
    
    # Generate HTML report
    try:
        with open(DAILY_REPORT, 'r') as f:
            template = f.read()
    except:
        # Create a simple template if file doesn't exist
        template = """<!DOCTYPE html>
<html>
<head>
    <title>FED Website Changes Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
        h1, h2 { color: #00395d; }
        .container { max-width: 1000px; margin: 0 auto; }
        .section { margin-bottom: 30px; border-bottom: 1px solid #ddd; padding-bottom: 20px; }
        ul { padding-left: 20px; }
        li { margin-bottom: 8px; }
        footer { margin-top: 40px; font-size: 0.8em; color: #666; border-top: 1px solid #ddd; padding-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>FED Website Changes Report</h1>
        
        <div class="section">
            <h2>Recent Changes</h2>
            <!-- CHANGES_CONTENT -->
        </div>
        
        <div class="section">
            <h2>FED Officials Mentioned</h2>
            <!-- OFFICIALS_CONTENT -->
        </div>
        
        <div class="section">
            <h2>FED Publications Mentioned</h2>
            <!-- PUBLICATIONS_CONTENT -->
        </div>
        
        <footer>
            <p>Generated by FedLoad on <!-- GENERATION_TIME --></p>
            <p><a href="weekly_summary.html">View Weekly Summary</a></p>
        </footer>
    </div>
</body>
</html>"""
    
    # Replace placeholders with data
    changes_html = ""
    if recent_logs:
        changes_html = "<ul>"
        for log in recent_logs:
            changes_html += f"<li><a href='{log['url']}'>{log['url']}</a> - {datetime.fromisoformat(log['time'].replace('Z', '')).strftime('%Y-%m-%d %H:%M:%S')}</li>"
        changes_html += "</ul>"
    else:
        changes_html = "<p>No changes detected in the last 24 hours.</p>"
    
    people_html = ""
    if people_sorted:
        people_html = "<ul>"
        for person, count in people_sorted[:10]:  # Top 10
            people_html += f"<li>{person} - {count} mentions</li>"
        people_html += "</ul>"
    else:
        people_html = "<p>No FED officials mentioned in the last 24 hours.</p>"
    
    pub_html = ""
    if pub_sorted:
        pub_html = "<ul>"
        for pub, count in pub_sorted[:10]:  # Top 10
            pub_html += f"<li>{pub} - {count} mentions</li>"
        pub_html += "</ul>"
    else:
        pub_html = "<p>No FED publications mentioned in the last 24 hours.</p>"
    
    # Update the template with actual data
    template = template.replace("<!-- CHANGES_CONTENT -->", changes_html)
    template = template.replace("<!-- OFFICIALS_CONTENT -->", people_html)
    template = template.replace("<!-- PUBLICATIONS_CONTENT -->", pub_html)
    template = template.replace("<!-- GENERATION_TIME -->", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # Write the report
    with open(DAILY_REPORT, 'w') as f:
        f.write(template)
    
    print(f"[{datetime.now().isoformat()}] Daily report generated successfully.")

# Generate weekly summary
def generate_weekly_summary():
    if not weekly_summary_enabled:
        return
    
    print(f"[{datetime.now().isoformat()}] Generating weekly summary...")
    log_data = load_change_log()
    entity_store = load_entity_store()
    
    # Ensure entity_store has the proper structure
    if "entities" not in entity_store:
        entity_store["entities"] = {}
    
    # Filter logs for the last 7 days
    now = datetime.now()
    recent_logs = [log for log in log_data if (now - datetime.fromisoformat(log["time"].replace("Z", ""))).days < 7]
    
    # Count stats
    total_changes = len(recent_logs)
    sites_with_changes = set([log["url"] for log in recent_logs])
    total_sites_changed = len(sites_with_changes)
    
    # Count mentions of Fed entities
    people_mentions = {}
    org_mentions = {}
    pub_mentions = {}
    site_activity = {}
    
    for log in recent_logs:
        site_url = log["url"]
        site_activity[site_url] = site_activity.get(site_url, 0) + 1
        
        for person in log["entities_found"].get("fed_people", []):
            people_mentions[person] = people_mentions.get(person, 0) + 1
        
        for org in log["entities_found"].get("fed_organizations", []):
            org_mentions[org] = org_mentions.get(org, 0) + 1
        
        for pub in log["entities_found"].get("fed_publications", []):
            pub_mentions[pub] = pub_mentions.get(pub, 0) + 1
    
    # Sort by frequency
    people_sorted = sorted(people_mentions.items(), key=lambda x: x[1], reverse=True)
    org_sorted = sorted(org_mentions.items(), key=lambda x: x[1], reverse=True)
    pub_sorted = sorted(pub_mentions.items(), key=lambda x: x[1], reverse=True)
    sites_sorted = sorted(site_activity.items(), key=lambda x: x[1], reverse=True)
    
    # Generate HTML report
    try:
        with open(WEEKLY_SUMMARY, 'r') as f:
            template = f.read()
    except:
        # Create a simple template if file doesn't exist
        template = """<!DOCTYPE html>
<html>
<head>
    <title>FED Website Weekly Summary</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
        h1, h2 { color: #00395d; }
        .container { max-width: 1000px; margin: 0 auto; }
        .section { margin-bottom: 30px; border-bottom: 1px solid #ddd; padding-bottom: 20px; }
        .stats { display: flex; justify-content: space-between; text-align: center; margin: 30px 0; }
        .stat-box { width: 22%; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .stat-number { font-size: 2.5em; font-weight: bold; color: #00395d; }
        .stat-label { font-size: 0.9em; color: #666; }
        ol { padding-left: 20px; }
        li { margin-bottom: 8px; }
        footer { margin-top: 40px; font-size: 0.8em; color: #666; border-top: 1px solid #ddd; padding-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>FED Website Weekly Summary</h1>
        
        <div class="section">
            <h2>Weekly Overview</h2>
            <!-- OVERVIEW_CONTENT -->
        </div>
        
        <div class="section">
            <h2>Most Active FED Sites</h2>
            <!-- ACTIVE_SITES_CONTENT -->
        </div>
        
        <div class="section">
            <h2>Most Mentioned Officials</h2>
            <!-- OFFICIALS_CONTENT -->
        </div>
        
        <div class="section">
            <h2>Most Mentioned Publications</h2>
            <!-- PUBLICATIONS_CONTENT -->
        </div>
        
        <div class="section">
            <h2>Trending Topics</h2>
            <!-- TOPICS_CONTENT -->
        </div>
        
        <footer>
            <p>Generated by FedLoad on <!-- GENERATION_TIME --></p>
            <p><a href="daily_report.html">View Daily Report</a></p>
        </footer>
    </div>
</body>
</html>"""
    
    # Create overview section
    overview_html = f"""
    <div class="stats">
        <div class="stat-box">
            <div class="stat-number">{total_changes}</div>
            <div class="stat-label">Total Changes</div>
        </div>
        <div class="stat-box">
            <div class="stat-number">{total_sites_changed}</div>
            <div class="stat-label">Active Sites</div>
        </div>
        <div class="stat-box">
            <div class="stat-number">{len(people_mentions)}</div>
            <div class="stat-label">Officials Mentioned</div>
        </div>
        <div class="stat-box">
            <div class="stat-number">{len(pub_mentions)}</div>
            <div class="stat-label">Publications Referenced</div>
        </div>
    </div>
    """
    
    # Create active sites section
    sites_html = ""
    if sites_sorted:
        sites_html = "<ol>"
        for site, count in sites_sorted[:5]:  # Top 5
            sites_html += f"<li><a href='{site}'>{site}</a> - {count} changes</li>"
        sites_html += "</ol>"
    else:
        sites_html = "<p>No site activity this week.</p>"
    
    # Create officials section
    officials_html = ""
    if people_sorted:
        officials_html = "<ol>"
        for person, count in people_sorted[:5]:  # Top 5
            officials_html += f"<li>{person} - {count} mentions</li>"
        officials_html += "</ol>"
    else:
        officials_html = "<p>No FED officials mentioned this week.</p>"
    
    # Create publications section
    pubs_html = ""
    if pub_sorted:
        pubs_html = "<ol>"
        for pub, count in pub_sorted[:5]:  # Top 5
            pubs_html += f"<li>{pub} - {count} mentions</li>"
        pubs_html += "</ol>"
    else:
        pubs_html = "<p>No FED publications mentioned this week.</p>"
    
    # Update the template with actual data
    template = template.replace("<!-- OVERVIEW_CONTENT -->", overview_html)
    template = template.replace("<!-- ACTIVE_SITES_CONTENT -->", sites_html)
    template = template.replace("<!-- OFFICIALS_CONTENT -->", officials_html)
    template = template.replace("<!-- PUBLICATIONS_CONTENT -->", pubs_html)
    template = template.replace("<!-- TOPICS_CONTENT -->", "<p>Topic analysis not yet implemented.</p>")
    template = template.replace("<!-- GENERATION_TIME -->", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # Write the report
    with open(WEEKLY_SUMMARY, 'w') as f:
        f.write(template)
    
    print(f"[{datetime.now().isoformat()}] Weekly summary generated successfully.")

# Main function
def main():
    print(f"[{datetime.now().isoformat()}] ====== FedLoad Scheduler Started ======")
    print(f"[{datetime.now().isoformat()}] Press Ctrl+C to exit gracefully")
    
    try:
        # Initial check
        check_all_sites()
        
        # Schedule regular checks
        schedule.every(check_frequency).minutes.do(check_all_sites)
        
        # Schedule daily report generation
        if daily_report_enabled:
            hour, minute = map(int, daily_report_time.split(':'))
            schedule.every().day.at(daily_report_time).do(generate_daily_report)
            print(f"[{datetime.now().isoformat()}] Scheduled daily report at {daily_report_time}")
        
        # Schedule weekly summary generation
        if weekly_summary_enabled:
            hour, minute = map(int, weekly_summary_time.split(':'))
            if weekly_summary_day.lower() == "monday":
                schedule.every().monday.at(weekly_summary_time).do(generate_weekly_summary)
            elif weekly_summary_day.lower() == "tuesday":
                schedule.every().tuesday.at(weekly_summary_time).do(generate_weekly_summary)
            elif weekly_summary_day.lower() == "wednesday":
                schedule.every().wednesday.at(weekly_summary_time).do(generate_weekly_summary)
            elif weekly_summary_day.lower() == "thursday":
                schedule.every().thursday.at(weekly_summary_time).do(generate_weekly_summary)
            elif weekly_summary_day.lower() == "friday":
                schedule.every().friday.at(weekly_summary_time).do(generate_weekly_summary)
            elif weekly_summary_day.lower() == "saturday":
                schedule.every().saturday.at(weekly_summary_time).do(generate_weekly_summary)
            elif weekly_summary_day.lower() == "sunday":
                schedule.every().sunday.at(weekly_summary_time).do(generate_weekly_summary)
            
            print(f"[{datetime.now().isoformat()}] Scheduled weekly summary on {weekly_summary_day} at {weekly_summary_time}")
        
        # Run the scheduler
        while not exit_event.is_set():
            schedule.run_pending()
            time.sleep(1)
            
            # Check for exit event more frequently
            if exit_event.is_set():
                break
        
        # Generate final report before exit
        generate_daily_report()
        print(f"[{datetime.now().isoformat()}] Final daily report generated")
        
        if weekly_summary_enabled:
            generate_weekly_summary()
            print(f"[{datetime.now().isoformat()}] Final weekly summary generated")
        
        print(f"[{datetime.now().isoformat()}] ====== FedLoad Scheduler Stopped ======")
        
    except KeyboardInterrupt:
        print(f"\n[{datetime.now().isoformat()}] Received keyboard interrupt. Shutting down...")
        exit_event.set()
    except Exception as e:
        print(f"\n[{datetime.now().isoformat()}] Error in main loop: {str(e)}")
        exit_event.set()
    finally:
        # Ensure we exit cleanly
        sys.exit(0)

if __name__ == "__main__":
    main()
