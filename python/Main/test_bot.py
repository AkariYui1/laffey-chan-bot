import os
import json

from .consts import DATA_DIR, WARNINGS_FILE, QUARANTINE_FILE, COUNTING_FILE

# Test if data folder paths work correctly
def test_data_paths():
    base_dir = os.path.dirname(__file__)
    data_dir = DATA_DIR
    
    print(f"Base directory: {base_dir}")
    print(f"Data directory: {data_dir}")
    print(f"Data directory exists: {os.path.isdir(data_dir)}")
    
    # Test each JSON file
    for file in [WARNINGS_FILE, QUARANTINE_FILE, COUNTING_FILE]:
        print(f"{file} exists as a file: {os.path.isfile(file)}")

if __name__ == "__main__":
    test_data_paths()