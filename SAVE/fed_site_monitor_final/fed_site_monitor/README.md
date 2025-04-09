# FED Website Monitor

A lightweight system to monitor US Federal Reserve websites for content changes.

## 🔧 Features
- Tracks all 12 district banks + key FED/FRB `.gov` sites
- Detects and logs page changes
- FastAPI API + Scheduled crawler

## 📦 Install
```bash
git clone <this-repo>
cd fed_site_monitor
python3 -m venv venv
source venv/bin/activate  # Or use `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

## 🚀 Run API
```bash
uvicorn main:app --reload
```

## 🕒 Run Scheduler
```bash
python scheduler.py
```

To stop the scheduler safely, press `Ctrl+C`. It will save the current log state before exiting.

## 📂 Files
- `main.py` – API
- `scheduler.py` – Scheduled crawler
- `tracked_sites.json` – URL list
- `change_log.json` – History log
