import json
import os
import tempfile
import shutil


class FileTestUtils:
    """Utility class for managing JSON files in tests
    
    Note: This class is not a test class - it's a utility for tests.
    The __test__ = False attribute prevents pytest from trying to collect it.
    """
    __test__ = False  # Prevent pytest from collecting this as a test class
    
    def __init__(self, base_dir=None):
        """Initialize with optional base directory"""
        self.base_dir = base_dir or tempfile.mkdtemp()
        
    def __enter__(self):
        """Enter context manager"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager and clean up"""
        self.cleanup()
        return False
    
    def cleanup(self):
        """Clean up temporary directory"""
        if os.path.exists(self.base_dir):
            shutil.rmtree(self.base_dir)
            os.makedirs(self.base_dir, exist_ok=True)
    
    def get_test_file_path(self, filename):
        """Get full path to test file"""
        return os.path.join(self.base_dir, filename)
    
    def load_json(self, filename):
        """Load JSON file with error handling"""
        file_path = self.get_test_file_path(filename)
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
        except json.JSONDecodeError:
            return None
    
    def save_json(self, filename, data):
        """Save JSON file"""
        file_path = self.get_test_file_path(filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def clear_json_file(self, filename):
        """Clear entire JSON file content"""
        self.save_json(filename, {})
    
    def clear_json_list(self, filename, list_key):
        """Clear specific list in JSON file"""
        data = self.load_json(filename) or {}
        if list_key in data:
            data[list_key] = []
        self.save_json(filename, data)
    
    def clear_json_entry(self, filename, entry_key):
        """Remove specific entry from JSON file"""
        data = self.load_json(filename) or {}
        if entry_key in data:
            del data[entry_key]
        self.save_json(filename, data)
    
    def copy_test_file(self, source_path, target_filename):
        """Copy a test file to the test directory"""
        # If source_path is just a filename, assume it's in the tests directory
        if not os.path.isabs(source_path):
            source_path = os.path.join(os.path.dirname(__file__), source_path)
        
        target_path = self.get_test_file_path(target_filename)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        shutil.copy2(source_path, target_path)
        return target_path
    
    def get_temp_dir(self):
        """Get the temporary directory path"""
        return self.base_dir


# Alias for backward compatibility
FileManager = FileTestUtils
