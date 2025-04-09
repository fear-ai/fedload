from fastapi import FastAPI
from fetcher import fetch_page, extract_text
from hasher import hash_content
from diff import is_changed

app = FastAPI()

stored_hashes = {}

@app.get("/check")
def check_site(url: str):
    html = fetch_page(url)
    if not html:
        return {"status": "fail", "message": "Unable to fetch page."}

    text = extract_text(html)
    new_hash = hash_content(text)
    old_hash = stored_hashes.get(url)
    changed = is_changed(old_hash, new_hash)

    stored_hashes[url] = new_hash

    return {
        "url": url,
        "changed": changed,
        "previous_hash": old_hash,
        "current_hash": new_hash
    }
