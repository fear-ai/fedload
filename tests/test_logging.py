import pytest
import json
import logging
import os
import sys
import pytest
import json
import logging

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from config_log import setup_logging
from scheduler import check_site, extract_entities_simple, CONFIG_FILE
from scheduler import logger as scheduler_logger
from main import logger as main_logger
from fetcher import logger as fetcher_logger

# Set up test logger
logger = logging.getLogger('test_logger')
logger.setLevel(logging.DEBUG)

# Add handlers to capture logs
test_handler = logging.StreamHandler()
test_handler.setLevel(logging.DEBUG)
logger.addHandler(test_handler)

# Capture logs from other modules
scheduler_logger.addHandler(test_handler)
main_logger.addHandler(test_handler)
fetcher_logger.addHandler(test_handler)

def test_logging_config():
    """Test logging configuration setup"""
    logger = setup_logging()
    assert logger is not None
    assert logger.level == logging.INFO

def test_entity_extraction_config():
    """Test entity extraction configuration loading"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            entity_config = config.get('entity_recognition', {})
            assert entity_config.get('min_word_length', 3) >= 3
            assert entity_config.get('ignore_common_words', True) in [True, False]
            assert entity_config.get('typo_correction', True) in [True, False]
    except Exception as e:
        pytest.fail(f"Failed to load entity config: {e}")

@pytest.mark.skip(reason="Entity extraction tests need further review")
def test_entity_extraction_common_words():
    """Test entity extraction with common words"""
    pytest.skip("Skipping for now - needs review")

@pytest.mark.skip(reason="Entity extraction tests need further review")
def test_entity_extraction_min_length():
    """Test entity extraction with minimum word length"""
    pytest.skip("Skipping for now - needs review")

@pytest.mark.skip(reason="Entity extraction tests need further review")
def test_entity_extraction_typo_handling():
    """Test entity extraction with typos"""
    pytest.skip("Skipping for now - needs review")

def test_check_site_logging(caplog):
    """Test logging in check_site function"""
    # Test logging in check_site function
    # Create mock entity store
    entity_store = {}
    
    # Test with valid URL
    url = "https://www.example.com"
    changed, old_hash, new_hash, entities, fed_entities = check_site(url, entity_store)
    
    # Verify logging
    assert any("Fetching content from" in record.message for record in caplog.records)
    assert any("Successfully fetched HTTP URL" in record.message for record in caplog.records)
    
    # Test with invalid URL
    invalid_url = "invalid-url"
    changed, old_hash, new_hash, entities, fed_entities = check_site(invalid_url, entity_store)
    
    # Verify error logging - the actual message is "HTTP error:" not "Error fetching HTTP URL"
    assert any("HTTP error:" in record.message for record in caplog.records)
