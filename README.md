# FedLoad

A lightweight system to monitor US Federal Reserve websites for content changes.

## 🔧 Features
- Tracks all 12 district banks + key FED/FRB `.gov` sites
- Detects and logs page changes
- Entity extraction & summarization support
- Generates daily HTML reports for web/newsletter publication
- Stores NER entities persistently between runs

## 🛠️ Project Phases

### Phase 1: Planning & Setup ✓
- Define goals and source list
- Identify change signals (DOM structure, content hashes)
- Chosen stack: Python, FastAPI, schedule, BeautifulSoup

### Phase 2: Web Crawler & Change Detection ✓
- Implement fetcher using `requests` and `BeautifulSoup`
- Compute content hash to detect changes
- Diff logic in `diff.py`

### Phase 3: Named Entity Recognition ✓
- `spaCy` used to extract title-cased words
- Identifies likely people/organizations
- Saves entity data in `entity_store.json`

### Phase 4: Search, Summarization & Dashboard ✓
- Sentence-based summarization of longest content
- Entity extraction shown via API
- Generates daily HTML reports for publishing

### Phase 5: Testing & QA ✓
- Try/Except on network & file errors
- Graceful exit via `Ctrl+C`
- JSON logs retained safely
- Ready for automated testing via test suite

### Phase 6: Deployment & Support ✓
- Run locally with virtualenv and scheduler
- Report export to HTML for website/newsletter publishing
- Configurable check frequency and report generation

### Phase 7: Documentation & Handoff ✓
- GitHub-style README with usage
- In-code documentation and modular file structure

## 📦 Install
```bash
git clone <this-repo>
cd fedload
python3 -m venv venv
source venv/bin/activate  # Or use `venv\Scripts\activate` on Windows
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## 🚀 Usage

### Run API Server (for interactive checking and UI access)
```bash
uvicorn main:app --reload
```
Once running, access the API documentation at: http://127.0.0.1:8000/docs

#### Available API Endpoints

| Endpoint | Method | Description | Example |
|----------|--------|-------------|---------|
| `/docs` | GET | Interactive API documentation | http://127.0.0.1:8000/docs |
| `/check` | GET | Check a specific FED website for changes | http://127.0.0.1:8000/check?url=https://www.federalreserve.gov/ |
| `/entities` | GET | Get all tracked entities across websites | http://127.0.0.1:8000/entities |
| `/publications` | GET | Get all tracked FED publications | http://127.0.0.1:8000/publications |
| `/config` | GET | View current configuration | http://127.0.0.1:8000/config |

> **Note:** Accessing just http://127.0.0.1:8000/ will return a "Not Found" error because you need to specify one of the above endpoints.

### Run Scheduler (for automated monitoring)
```bash
python scheduler.py
```
The scheduler will:
- Check all sites based on configured frequency (default: every 30 minutes)
- Extract named entities from changed content
- Store entities in `entity_store.json`
- Generate reports based on configuration:
  - Daily reports (enabled by default)
  - Weekly summaries (disabled by default)
- Log all changes to `change_log.json`

## 📤 Data Files
- `config.json` - Configuration settings for scheduling, monitoring, and entity recognition
- `tracked_sites.json` - List of URLs to monitor
- `change_log.json` - History of detected changes
- `entity_store.json` - Accumulated named entities
- `daily_report.html` - Web-ready change report
- `weekly_summary.html` - Weekly aggregated statistics (if enabled)
- `fed_entities.json` - Knowledge base of FED officials, organizations, and publications

## ⚙️ Configuration

The system is configured through `config.json` with the following options:

```json
{
  "scheduling": {
    "check_frequency_minutes": 30,
    "report_generation": {
      "daily_report": {
        "enabled": true,
        "time": "00:00",
        "format": "html"
      },
      "weekly_summary": {
        "enabled": false,
        "day": "Monday",
        "time": "06:00",
        "format": "html"
      }
    },
    "data_retention": {
      "change_log_days": 90,
      "reports_days": 30
    }
  },
  "entity_recognition": {
    "use_fed_entities": true,
    "enrich_existing_entities": true
  },
  "monitoring": {
    "content_hash_algorithm": "sha256",
    "timeout_seconds": 10,
    "user_agent": "FedLoad Monitor/1.0"
  },
  "notifications": {
    "on_change": {
      "enabled": false,
      "console": true,
      "email": false,
      "email_recipients": []
    },
    "on_error": {
      "enabled": false,
      "console": true,
      "email": false,
      "email_recipients": []
    }
  }
}
```

## 🧠 Enhanced Entity Recognition

For improved accuracy, a custom entity database can be created in `fed_entities.json`:

```json
{
  "people": [
    {
      "name": "Jerome Powell",
      "title": "Chair",
      "organization": "Federal Reserve Board of Governors",
      "since": "2018",
      "bio_url": "https://www.federalreserve.gov/aboutthefed/bios/board/powell.htm",
      "aliases": ["Powell", "Chair Powell", "Jerome H. Powell"],
      "related_topics": ["monetary policy", "banking supervision"]
    }
  ],
  "organizations": [
    {
      "name": "Federal Open Market Committee",
      "acronym": "FOMC",
      "type": "committee",
      "members": ["Chair", "Vice Chair", "Reserve Bank Presidents"],
      "meeting_frequency": "Eight times per year",
      "description": "Sets monetary policy"
    }
  ],
  "publications": [
    {
      "name": "Beige Book",
      "full_name": "Summary of Commentary on Current Economic Conditions",
      "frequency": "Eight times per year",
      "publishing_body": "Federal Reserve Board",
      "url_pattern": "https://www.federalreserve.gov/monetarypolicy/beigebook",
      "description": "Report on current economic conditions in each District",
      "release_schedule": ["January", "March", "April", "June", "July", "September", "October", "December"],
      "related_topics": ["economic conditions", "regional economy"]
    },
    {
      "name": "Minutes",
      "full_name": "Minutes of the Federal Open Market Committee",
      "frequency": "Eight times per year",
      "publishing_body": "FOMC",
      "url_pattern": "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
      "release_timing": "Three weeks after each FOMC meeting",
      "key_sections": ["Participants' views", "Staff Review", "Committee Policy Action"],
      "significance": "Provides detailed insights into FOMC deliberations"
    }
  ],
  "events": [
    {
      "name": "FOMC Meeting",
      "frequency": "Eight times per year",
      "announcement_type": "Statement",
      "followed_by": ["Press Conference", "Minutes (3 weeks later)"],
      "market_impact": "High",
      "typical_topics": ["federal funds rate", "balance sheet", "economic outlook"]
    }
  ],
  "topics": [
    {
      "name": "Monetary Policy",
      "related_terms": ["interest rates", "federal funds rate", "open market operations"],
      "key_officials": ["Chair", "FOMC Members"],
      "related_publications": ["FOMC Statement", "Monetary Policy Report"]
    }
  ]
}
```

This enhanced entity recognition:
- Provides rich context for detected entities
- Supports relationship mapping between people, organizations, and publications
- Enables more accurate classification of content changes
- Allows tracking of specific publication release cycles

## 📂 Code Structure
- `main.py` – FastAPI server with summary + NER endpoints
- `scheduler.py` – Periodic checker + report generator
- `fetcher.py` - Web page fetching and text extraction
- `hasher.py` - Content hashing utilities
- `diff.py` - Change detection logic

## ✅ Testing
To verify the system is working correctly:

1. Run the scheduler:
```bash
python scheduler.py
```

2. View initial output:
   - Check that sites are being processed in the terminal output
   - Verify `entity_store.json` is created and contains entities
   - Confirm `daily_report.html` is generated

3. Test API functionality:
```bash
# In a different terminal
uvicorn main:app
```
   - Visit http://127.0.0.1:8000/docs in your browser
   - Try the `/check` endpoint with a FED URL like "https://www.federalreserve.gov/"
   - View recognized entities with the `/entities` endpoint
   - See tracked publications with the `/publications` endpoint
   - View current configuration with the `/config` endpoint

4. Run the automated tests:
```bash
pytest tests/
```

## 🔍 Monitoring Results
After running for a while, you should see:
- Regular updates in the terminal showing site checks
- Growing `change_log.json` file as changes are detected
- Accumulated entities in `entity_store.json`
- Daily updates to `daily_report.html`
- Weekly summaries in `weekly_summary.html` (if enabled)

---