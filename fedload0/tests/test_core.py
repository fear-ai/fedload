import pytest
from fetcher import fetch_page, extract_text
from hasher import hash_content
from diff import is_changed

def test_fetch_page_valid():
    html = fetch_page("https://www.example.com")
    assert html is not None
    assert "Example Domain" in html

def test_fetch_page_invalid():
    with pytest.raises(ValueError):
        fetch_page("invalid-url")

def test_extract_text():
    html = "<html><body><h1>Hello</h1></body></html>"
    assert extract_text(html) == "Hello"

def test_hash_content():
    text = "hello world"
    assert isinstance(hash_content(text), str)
    assert len(hash_content(text)) == 64

def test_is_changed():
    h1 = hash_content("data")
    h2 = hash_content("data")
    h3 = hash_content("other")
    assert is_changed(h1, h3)
    assert not is_changed(h1, h2)
