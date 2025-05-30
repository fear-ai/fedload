import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from fetcher import fetch_page, extract_text
from hasher import hash_content
from diff import is_changed


def test_fetch_page_valid():
    html = fetch_page("https://www.example.com")
    assert html is not None, "Failed to fetch valid URL"
    assert "Example Domain" in html, "Expected content not found in response"


def test_fetch_page_invalid():
    # Test invalid URL handling
    result = fetch_page("invalid-url")
    assert result is None, "Invalid URL should return None"
    
    # Test unsupported protocol
    result = fetch_page("mailto:test@example.com")
    assert result is None, "Unsupported protocol should return None"


def test_extract_text():
    # Test valid HTML
    html = "<html><body><h1>Hello</h1></body></html>"
    assert extract_text(html) == "Hello", "Failed to extract text from valid HTML"
    
    # Test malformed HTML
    malformed_html = "<html><body><h1>Hello</h1></body>"
    # Keep assertion message readable even if long
    assert extract_text(malformed_html) == "Hello", "Failed to extract text from malformed HTML"


def test_hash_content():
    text = "hello world"
    
    # Test default MD5 hash (32 characters)
    hash_result = hash_content(text)
    assert isinstance(hash_result, str), "Hash result should be a string"
    assert len(hash_result) == 32, "MD5 hash should be 32 characters long"
    
    # Test SHA256 hash (64 characters)
    hash_result_sha256 = hash_content(text, algorithm="sha256")
    assert len(hash_result_sha256) == 64, "SHA256 hash should be 64 characters long"
    
    # Test that different algorithms produce different results
    # Keep assertion message readable even if long
    assert hash_result != hash_result_sha256, "MD5 and SHA256 should produce different hashes"


def test_is_changed():
    # Test with different content
    h1 = hash_content("data")
    h2 = hash_content("different data")
    assert is_changed(h1, h2), "Different content should be marked as changed"
    
    # Test with same content
    h1 = hash_content("data")
    h2 = hash_content("data")
    # Keep assertion message readable even if long
    assert not is_changed(h1, h2), "Same content should not be marked as changed"
    h2 = hash_content("data")
    h3 = hash_content("other")
    assert is_changed(h1, h3)
    assert not is_changed(h1, h2)
