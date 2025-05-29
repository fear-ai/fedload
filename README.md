# FedLoad

A lightweight system to monitor US Federal Reserve websites for content changes.

## 🔧 Features
- Tracks all 12 district banks + key FED/FRB `.gov` sites
- Detects and logs page changes
- Entity extraction & summarization support
- Generates daily HTML reports for web/newsletter publication
- Stores NER entities persistently between runs
- Advanced text extraction with multiple parsers
- PDF content processing support

## 🛠️ Project Phases

### Phase 1: Planning & Setup ✅ COMPLETE
- ✅ Define goals and source list
- ✅ Identify change signals (DOM structure, content hashes)
- ✅ Chosen stack: Python, FastAPI, schedule, BeautifulSoup, newspaper3k, trafilatura, html2text, pdfminer.six

### Phase 2: Web Crawler & Change Detection ✅ COMPLETE
- ✅ Implement fetcher using `requests` and `BeautifulSoup`
- ✅ Compute content hash to detect changes (configurable MD5/SHA256)
- ✅ Diff logic in `diff.py`
- ✅ Support for PDF content extraction
- ✅ Enhanced content extraction with multiple parsers
- ✅ Configurable hash algorithms with initial byte checking for performance

### Phase 3: Named Entity Recognition ✅ COMPLETE (Optional)
- ✅ `spaCy` used to extract title-cased words
- ✅ Identifies likely people/organizations
- ✅ Saves entity data in `entity_store.json`
- ✅ Enhanced entity enrichment with custom recognizer
- ✅ **NEW**: NER made optional and disabled by default for better performance

### Phase 4: Search, Summarization & Dashboard ✅ COMPLETE
- ✅ Sentence-based summarization of longest content
- ✅ Entity extraction shown via API
- ✅ Generates daily HTML reports for publishing
- ✅ Multiple text extraction methods for better content parsing
- ✅ FastAPI web interface with comprehensive API documentation

### Phase 5: Testing & QA ✅ COMPLETE
- ✅ Try/Catch on network & file errors
- ✅ Graceful exit via `Ctrl+C`
- ✅ JSON logs retained safely
- ✅ Comprehensive automated testing via test suite
- ✅ Comprehensive error handling and logging
- ✅ **NEW**: Enhanced resilience - no fatal exits on URL/content errors

### Phase 6: Deployment & Support ✅ COMPLETE
- ✅ Run locally with virtualenv and scheduler
- ✅ Report export to HTML for website/newsletter publishing
- ✅ Configurable check frequency and report generation
- ✅ Data retention policies for logs and reports
- ✅ **NEW**: Enhanced configuration with URL filtering and performance optimizations

### Phase 7: Documentation & Handoff ✅ COMPLETE
- ✅ GitHub-style README with usage
- ✅ In-code documentation and modular file structure
- ✅ API documentation with FastAPI
- ✅ Configuration documentation
- ✅ **NEW**: Comprehensive troubleshooting and operational guides

### Phase 8: Security & Performance Enhancements 🔄 IN PROGRESS
- ✅ **NEW**: Optional URL filtering with whitelist/blacklist support
- ✅ **NEW**: Faster hashing with configurable algorithms (MD5/SHA256)
- ✅ **NEW**: Initial byte checking for quick change detection
- ✅ **NEW**: Content size limits and protection against excessive input
- 🔄 **IN PROGRESS**: Comprehensive security hardening (OWASP validation)
- 🔄 **IN PROGRESS**: Advanced failure tracking and domain blacklisting

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
| `/` | GET | Root endpoint | http://127.0.0.1:8000/ |
| `/docs` | GET | Interactive API documentation | http://127.0.0.1:8000/docs |
| `/check` | GET | Check a specific FED website for changes | http://127.0.0.1:8000/check?url=https://www.federalreserve.gov/ |
| `/entities` | GET | Get all tracked entities across websites | http://127.0.0.1:8000/entities |
| `/publications` | GET | Get all tracked FED publications | http://127.0.0.1:8000/publications |
| `/config` | GET | View current configuration | http://127.0.0.1:8000/config |

> **Note:** The root endpoint (`/`) returns a simple status message. All other endpoints require specific paths as shown above.

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
- Apply data retention policies for logs and reports

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
    "enabled": false,
    "use_fed_entities": true,
    "enrich_existing_entities": true,
    "min_word_length": 3,
    "ignore_common_words": true,
    "typo_correction": true
  },
  "monitoring": {
    "content_hash_algorithm": "md5",
    "hash_check_initial_bytes": 512,
    "max_content_size_mb": 50,
    "timeout_seconds": 10,
    "user_agent": "FedLoad Monitor/1.0",
    "url_filtering": {
      "enabled": false,
      "require_gov_tld": false,
      "allowed_tlds": [".gov", ".edu", ".org"],
      "blocked_tlds": [".tk", ".ml"],
      "allowed_domains": [],
      "blocked_domains": [],
      "allowed_path_patterns": [],
      "blocked_path_patterns": []
    }
  },
  "logging": {
    "max_size_mb": 10,
    "backup_count": 5,
    "level": "INFO"
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

### Configuration Options

#### Scheduling
- `check_frequency_minutes`: How often to check sites (default: 30)
- `report_generation`: Settings for report generation
  - `daily_report`: Daily change report settings
    - `enabled`: Whether to generate daily reports (default: true)
    - `time`: Time to generate report in HH:MM format (default: "00:00")
    - `format`: Report format, currently only "html" supported
  - `weekly_summary`: Weekly summary settings
    - `enabled`: Whether to generate weekly summaries (default: false)
    - `day`: Day of week to generate summary (default: "Monday")
    - `time`: Time to generate summary in HH:MM format (default: "06:00")
    - `format`: Summary format, currently only "html" supported
- `data_retention`: How long to keep logs and reports
  - `change_log_days`: Days to keep change logs (default: 90)
  - `reports_days`: Days to keep reports (default: 30)

#### Entity Recognition
- `enabled`: Whether to enable Named Entity Recognition (default: false)
  - **When disabled**: Content monitoring continues but no entity extraction is performed
  - **When enabled**: Full NLP processing with spaCy for entity extraction
- `use_fed_entities`: Whether to use FED-specific entity recognition (default: true)
- `enrich_existing_entities`: Whether to enrich entities with additional data (default: true)
- `min_word_length`: Minimum length for extracted entities (default: 3)
- `ignore_common_words`: Whether to filter out common words (default: true)
- `typo_correction`: Whether to attempt typo correction (default: true)

#### Monitoring
- `content_hash_algorithm`: Algorithm for change detection - "md5" (fast), "sha256" (secure), "sha1" (default: "md5")
- `hash_check_initial_bytes`: Number of initial bytes to hash for quick change detection (default: 512)
- `max_content_size_mb`: Maximum content size in MB before truncation (default: 50)
- `timeout_seconds`: Request timeout in seconds (default: 10)
- `user_agent`: Custom user agent for requests (default: "FedLoad Monitor/1.0")
- `url_filtering`: URL filtering configuration
  - `enabled`: Whether to enable URL filtering (default: false)
  - `require_gov_tld`: Whether to require .gov TLD for URLs (default: false)
  - `allowed_tlds`: List of allowed top-level domains (default: [".gov", ".edu", ".org"])
  - `blocked_tlds`: List of blocked top-level domains (default: [".tk", ".ml"])
  - `allowed_domains`: List of explicitly allowed domains (default: [])
  - `blocked_domains`: List of explicitly blocked domains (default: [])
  - `allowed_path_patterns`: List of allowed URL path patterns (default: [])
  - `blocked_path_patterns`: List of blocked URL path patterns (default: [])

#### Logging
- `max_size_mb`: Maximum log file size in MB before rotation (default: 10)
- `backup_count`: Number of backup log files to keep (default: 5)
- `level`: Logging level - "DEBUG", "INFO", "WARNING", "ERROR" (default: "INFO")

#### Notifications
- `on_change`: Settings for change notifications
  - `enabled`: Whether to send notifications on changes (default: false)
  - `console`: Whether to log to console (default: true)
  - `email`: Whether to send email notifications (default: false)
  - `email_recipients`: List of email addresses for notifications
- `on_error`: Settings for error notifications
  - `enabled`: Whether to send notifications on errors (default: false)
  - `console`: Whether to log errors to console (default: true)
  - `email`: Whether to send email notifications for errors (default: false)
  - `email_recipients`: List of email addresses for error notifications

### Configuration Behaviors

#### NER (Named Entity Recognition) Modes

**Disabled Mode (default: `"enabled": false`)**:
- ✅ Content fetching and change detection continues normally
- ✅ Hash-based change detection works
- ✅ Reports are generated showing content changes
- ❌ No entity extraction performed
- ❌ No spaCy model loading (faster startup, lower memory usage)
- ❌ Empty entity lists returned in API responses

**Enabled Mode (`"enabled": true`)**:
- ✅ Full NLP processing with spaCy
- ✅ Basic entity extraction (title-case words)
- ✅ FED-specific entity recognition (people, organizations, publications)
- ✅ Entity enrichment with metadata
- ⚠️ Requires spaCy model download: `python -m spacy download en_core_web_sm`
- ⚠️ Higher memory usage and slower processing

#### Content Processing Pipeline

1. **URL Validation**: Checks for .gov TLD if `require_gov_tld` is true
2. **Content Fetching**: Uses multiple extraction methods (trafilatura, newspaper3k, html2text, BeautifulSoup)
3. **Change Detection**: SHA256 hash comparison
4. **Entity Extraction** (if enabled):
   - Basic entities: Title-case words filtered by length and common word rules
   - FED entities: Matches against `fed_entities.json` database
5. **Storage**: Entities and hashes stored in `entity_store.json`
6. **Reporting**: HTML reports generated based on schedule

#### Error Handling

- **Network timeouts**: Configurable via `timeout_seconds`
- **Invalid URLs**: Rejected if not .gov (when `require_gov_tld` is true)
- **NER failures**: Falls back to simple text extraction
- **Configuration errors**: Uses default values and logs warnings

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
- Includes event and topic tracking

## 📂 Code Structure
- `main.py` – FastAPI server with summary + NER endpoints
- `scheduler.py` – Periodic checker + report generator
- `fetcher.py` - Web page fetching and text extraction
- `hasher.py` - Content hashing utilities
- `diff.py` - Change detection logic
- `doc/` - Additional documentation

## ✅ Testing
To verify the system is working correctly:

1. Run the test suite:
```bash
python -m pytest tests/ -v
```

2. Test specific components:
```bash
# Test configuration handling
python -m pytest tests/test_config.py -v

# Test entity management
python -m pytest tests/test_entity.py -v

# Test main functionality
python -m pytest tests/test_main.py -v
```

3. Run the scheduler:
```bash
python scheduler.py
```

4. View initial output:
   - Check that sites are being processed in the terminal output
   - Verify `entity_store.json` is created and contains entities
   - Confirm `daily_report.html` is generated

5. Test API functionality:
```bash
uvicorn main:app --reload
```
Then visit http://127.0.0.1:8000/docs to test endpoints

6. Check data retention:
   - Verify old logs and reports are automatically cleaned up
   - Confirm new data is being properly stored

## 🔄 Updates
- Added support for PDF content extraction
- Enhanced text extraction with multiple parsers
- Improved entity recognition with custom components
- Added data retention policies
- Expanded configuration options
- Added root endpoint
- Improved error handling and logging
- Improved test organization with dedicated utility class
- Better test file management with FileTestUtils
- Cleaned up test directory structure

## 📋 Project Status & Development

### Current Status: Production Ready ✅
The FedLoad system is **production-ready** for Federal Reserve website monitoring with:
- ✅ Reliable content change detection
- ✅ Optional entity recognition (disabled by default for performance)
- ✅ Comprehensive error handling and resilience
- ✅ Configurable URL filtering and security controls
- ✅ Performance optimizations (fast hashing, content size limits)
- ✅ Automated testing and quality assurance

### Documentation Structure
- **README.md** (this file): User guide, admin documentation, and developer onboarding
- **TODO.md**: Internal development notes, technical debt, and future enhancements
- **FIXES_SUMMARY.md**: Detailed changelog of recent improvements and fixes

### Performance Optimizations
- **Fast Hashing**: MD5 algorithm by default (vs SHA256) for 3x faster change detection
- **Initial Byte Checking**: Hash only first 512 bytes for quick change detection
- **Content Size Limits**: Configurable maximum content size (50MB default)
- **Optional NER**: Entity recognition disabled by default to reduce memory usage
- **Efficient Parsing**: Multiple content extraction methods with fallbacks

### Security Features
- **URL Filtering**: Optional whitelist/blacklist for TLDs, domains, and paths
- **Content Validation**: Size limits and input sanitization
- **Error Isolation**: Network/content errors never crash the system
- **Configurable Security**: Adjustable security vs performance trade-offs

---