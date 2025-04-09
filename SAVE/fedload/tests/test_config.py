import os
from utils import load_config

def test_load_config_defaults():
    config = load_config("nonexistent_config.yml")
    assert config['output_dir'] == 'output'
    assert config['software_version'].startswith('v')

def test_load_config_custom():
    with open("fedload_test.yml", "w") as f:
        f.write("output_dir: custom\nsoftware_version: vTEST")
    config = load_config("fedload_test.yml")
    os.remove("fedload_test.yml")
    assert config['output_dir'] == 'custom'
    assert config['software_version'] == 'vTEST'