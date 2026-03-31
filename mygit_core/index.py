import os
import json
from mygit_core.repository import get_mygit_path, is_initialized
from mygit_core.hash_object import store_object

def read_index():
    """Load current staging area from index.json."""
    index_path = get_mygit_path("index.json")
    with open(index_path, "r") as f:
        return json.load(f)

def write_index(index):
    """Write dict back to index.json."""
    index_path = get_mygit_path("index.json")
    with open(index_path, "w") as f:
        json.dump(index, f, indent=2)

def add_file(filepath):
    """Stage a file: store its blob and record it in index.json."""
    if not is_initialized():
        print("Not a mygit repository. Run 'init' first.")
        return

    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    file_hash = store_object(filepath)

    index = read_index()
    index[filepath] = file_hash
    write_index(index)

    print(f"Staged: {filepath} ({file_hash[:7]})")

def get_staged_files():
    """Return staged files dict. Used by commit and status."""
    return read_index()

def clear_index():
    """Reset staging area to empty after a commit."""
    write_index({})