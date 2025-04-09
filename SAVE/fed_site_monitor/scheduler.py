import json
import time
import schedule
from datetime import datetime
from fetcher import fetch_page, extract_text
from hasher import hash_content
from diff import is_changed

SITES_FILE = "tracked_sites_full.json"
LOG_FILE = "change_log.json"

try:
    with open(SITES_FILE) as f:
        sites = json.load(f)["sites"]
except Exception as e:
    print("Failed to load site list:", e)
    sites = []

stored_hashes = {}

try:
    with open(LOG_FILE, 'r') as f:
        log_data = json.load(f)
except:
    log_data = []

def check_all_sites():
    global log_data
    for url in sites:
        html = fetch_page(url)
        if not html:
            continue

        text = extract_text(html)
        new_hash = hash_content(text)
        old_hash = stored_hashes.get(url)
        if is_changed(old_hash, new_hash):
            log_entry = {
                "url": url,
                "time": datetime.utcnow().isoformat() + 'Z',
                "changed": True,
                "old_hash": old_hash,
                "new_hash": new_hash
            }
            log_data.append(log_entry)
            print(f"[CHANGE] {url}")
        stored_hashes[url] = new_hash

    with open(LOG_FILE, 'w') as f:
        json.dump(log_data, f, indent=2)

schedule.every(30).minutes.do(check_all_sites)

if __name__ == "__main__":
    print("[Scheduler running] Checking every 30 minutes...")
    while True:
        schedule.run_pending()
        time.sleep(10)
