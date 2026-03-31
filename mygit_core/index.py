import os
import json
import fnmatch
from mygit_core.repository import get_mygit_path, is_initialized
from mygit_core.hash_object import store_object


def read_index():
    index_path = get_mygit_path("index.json")
    with open(index_path, "r") as f:
        return json.load(f)


def write_index(index):
    index_path = get_mygit_path("index.json")
    with open(index_path, "w") as f:
        json.dump(index, f, indent=2)


def get_staged_files():
    return read_index()


def clear_index():
    write_index({})


def _load_ignore_patterns():
    patterns = [".mygit", ".mygit/*", "__pycache__", "*.pyc", ".git", ".git/*"]
    ignore_file = ".mygitignore"
    if os.path.exists(ignore_file):
        with open(ignore_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(line)
    return patterns

def _is_ignored(filepath, patterns):
    """Return True if filepath matches any ignore pattern."""
    filepath_norm = filepath.replace("\\", "/")
    for pattern in patterns:
        if fnmatch.fnmatch(filepath_norm, pattern):
            return True
        if fnmatch.fnmatch(filepath_norm, f"{pattern}/*"):
            return True
        if fnmatch.fnmatch(os.path.basename(filepath), pattern):
            return True
    return False


def add_file(filepath):
    """Stage a single file or all files if filepath is '.'"""
    if not is_initialized():
        print("Not a mygit repository. Run 'init' first.")
        return

    if filepath == ".":
        _add_all()
        return

    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    file_hash = store_object(filepath)
    index = read_index()
    index[filepath] = file_hash
    write_index(index)
    print(f"Staged: {filepath} ({file_hash[:7]})")


def _add_all():
    """Stage every non-ignored file in the working directory."""
    patterns = _load_ignore_patterns()
    index    = read_index()
    staged   = 0

    for root, dirs, files in os.walk("."):
        # Prune ignored directories so os.walk doesn't descend into them
        dirs[:] = [
            d for d in dirs
            if not _is_ignored(os.path.join(root, d), patterns)
        ]
        for filename in files:
            filepath = os.path.normpath(os.path.join(root, filename))
            if not _is_ignored(filepath, patterns):
                file_hash       = store_object(filepath)
                index[filepath] = file_hash
                print(f"Staged: {filepath} ({file_hash[:7]})")
                staged += 1

    write_index(index)
    print(f"\n{staged} file(s) staged.")