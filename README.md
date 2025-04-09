# FED Website Monitor

A lightweight system to monitor US Federal Reserve websites for content changes.

## 🔧 Features
- Tracks all 12 district banks + key FED/FRB `.gov` sites
- Detects and logs page changes
- Entity extraction & summarization support
- Generates daily HTML reports for web/newsletter publication
- Stores NER entities persistently between runs

## 🛠️ Project Phases

### Phase 1: Planning & Setup
- Define goals and source list
- Identify change signals (DOM structure, content hashes)
- Chosen stack: Python, FastAPI, schedule, BeautifulSoup

### Phase 2: Web Crawler & Change Detection
- Implement fetcher using `requests` and `BeautifulSoup`
- Compute content hash to detect changes
- Diff logic in `diff.py`

### Phase 3: Named Entity Recognition (Implemented)
- `spaCy` used to extract title-cased words
- Identifies likely people/organizations
- Saves entity data in `entity_store.json`

### Phase 4: Search, Summarization & Dashboard (Partial)
- Sentence-based summarization of longest content
- Entity extraction shown via API
- Generates daily HTML reports for publishing

### Phase 5: Testing & QA
- Try/Except on network & file errors
- Graceful exit via `Ctrl+C`
- JSON logs retained safely
- Ready for automated testing via test suite (TODO)

### Phase 6: Deployment & Support
- Run locally with virtualenv and scheduler
- Report export to HTML for website/newsletter publishing

### Phase 7: Documentation & Handoff
- GitHub-style README with usage
- In-code documentation and modular file structure

## 📦 Install
```bash
git clone <this-repo>
cd fed_site_monitor
python3 -m venv venv
source venv/bin/activate  # Or use `venv\Scripts\activate` on Windows
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## 🚀 Run API
```bash
uvicorn main:app --reload
```

## 🕒 Run Scheduler
```bash
python scheduler.py
```

## 📤 Import/Export for Offline Use
- Logs: `change_log.json`
- Entities: `entity_store.json`
- Reports: `daily_report.html`

## 📂 Files
- `main.py` – API with summary + NER
- `scheduler.py` – Periodic checker + report
- `tracked_sites.json` – URL config
- `change_log.json` – History log
- `entity_store.json` – Persistent NER output
- `daily_report.html` – Web-ready change report

## ✅ Test Plan
- [ ] Check API response for known FED URLs
- [ ] Verify `change_log.json` after scheduler runs
- [ ] Confirm entities persist across runs
- [ ] Ensure `daily_report.html` updates after changes

---