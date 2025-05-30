import pytest
import os
from test_utils import FileTestUtils as TestFileManager
import json

def test_entity_files():
    """Test basic entity file operations"""
    # Create test file manager with temporary directory
    with TestFileManager() as manager:
        entity_store = "entity_store.json"
        
        # Test clearing entire file
        manager.clear_json_file(entity_store)
        assert manager.load_json(entity_store) == {}
        
        # Test clearing specific list
        test_data = {"entities": ["entity1", "entity2"], "other_key": "value"}
        manager.save_json(entity_store, test_data)
        manager.clear_json_list(entity_store, "entities")
        loaded = manager.load_json(entity_store)
        assert loaded == {"entities": [], "other_key": "value"}
        
        # Test clearing specific entry
        manager.save_json(entity_store, test_data)
        manager.clear_json_entry(entity_store, "other_key")
        loaded = manager.load_json(entity_store)
        assert loaded == {"entities": ["entity1", "entity2"]}
        
        # Test copying file
        temp_path = manager.copy_test_file("test_entities.json", entity_store)
        assert os.path.exists(temp_path)
        
        # Verify content was copied correctly
        loaded = manager.load_json(entity_store)
        assert loaded is not None

def test_entity_operations(tmp_path):
    """Test entity file operations with test data"""
    # Create test file manager with specific temp directory
    manager = TestFileManager(str(tmp_path))
    
    # Copy test entities file
    manager.copy_test_file("test_entities.json", "entity_store.json")
    
    # Verify entities were copied correctly
    loaded = manager.load_json("entity_store.json")
    assert loaded is not None
    assert "entities" in loaded
    assert "last_updated" in loaded
    assert "stats" in loaded
    
    # Clear entities list while preserving other data
    manager.clear_json_list("entity_store.json", "entities")
    loaded = manager.load_json("entity_store.json")
    assert loaded["entities"] == []
    assert loaded["last_updated"] == "2025-05-15"
    assert loaded["stats"]["total_entities"] == 4  # stats should remain unchanged
    
    # Add new entities
    new_entities = ["New Entity 1", "New Entity 2"]
    loaded["entities"] = new_entities
    manager.save_json("entity_store.json", loaded)
    
    # Verify new entities were saved
    final_content = manager.load_json("entity_store.json")
    assert final_content["entities"] == new_entities
    assert final_content["last_updated"] == "2025-05-15"
    
    # Clear entities list
    manager.clear_json_list("entity_store.json", "entities")
    loaded = manager.load_json("entity_store.json")
    assert loaded["entities"] == []
    assert loaded["last_updated"] == "2025-05-15"
    assert loaded["stats"]["total_entities"] == 4  # stats should remain unchanged
    
    # Add new entities
    new_entities = ["New Entity 1", "New Entity 2"]
    loaded["entities"] = new_entities
    manager.save_json("entity_store.json", loaded)
    
    # Verify new entities were saved
    final_content = manager.load_json("entity_store.json")
    assert final_content["entities"] == new_entities
    assert final_content["last_updated"] == "2025-05-15"

def test_entity_update(tmp_path):
    """Test entity list updates and accumulation"""
    # Create test file manager with specific temp directory
    manager = TestFileManager(str(tmp_path))
    
    # Initialize entity store with some entities
    initial_entities = {
        "entities": ["entity1", "entity2"],
        "last_updated": "2025-05-15"
    }
    manager.save_json("entity_store.json", initial_entities)
    
    # Clear entities list while preserving other data
    manager.clear_json_list("entity_store.json", "entities")
    
    # Verify only entities list was cleared
    loaded = manager.load_json("entity_store.json")
    assert loaded == {
        "entities": [],
        "last_updated": "2025-05-15"
    }
    
    # Add new entities
    new_entities = ["entity3", "entity4"]
    loaded["entities"] = new_entities
    manager.save_json("entity_store.json", loaded)
    
    # Verify new entities were saved
    final_content = manager.load_json("entity_store.json")
    assert final_content == {
        "entities": ["entity3", "entity4"],
        "last_updated": "2025-05-15"
    }
