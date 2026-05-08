# mygit_core/stash.py

import os
import json
import shutil
from mygit_core.repository import get_mygit_path, is_initialized, get_head_commit
from mygit_core.hash_object import hash_file, store_object, restore_object
from mygit_core.index import get_staged_files, clear_index


def _read_stash():
    stash_path = get_mygit_path("stash.json")
    if not os.path.exists(stash_path):
        return []
    with open(stash_path, "r") as f:
        return json.load(f)


def _write_stash(stash):
    stash_path = get_mygit_path("stash.json")
    with open(stash_path, "w") as f:
        json.dump(stash, f, indent=2)


def stash_push(message=None):
    """
    Save current staged + working directory changes.
    Restore files to last committed state.
    """
    if not is_initialized():
        print("Not a mygit repository. Run 'init' first.")
        return

    head = get_head_commit()
    staged = get_staged_files()

    # Collect all files to stash: staged + modified tracked files
    head_files = {}
    if head:
        commit_path = get_mygit_path("commits", f"{head}.json")
        with open(commit_path, "r") as f:
            head_files = json.load(f)["files"]

    all_tracked = set(staged) | set(head_files)
    if not all_tracked:
        print("Nothing to stash.")
        return

    # Snapshot current state of all tracked files
    working_snapshot = {}
    for filepath in all_tracked:
        if os.path.exists(filepath):
            file_hash = store_object(filepath)
            working_snapshot[filepath] = file_hash

    stash_entry = {
        "message":  message or f"WIP on {head[:7] if head else 'no-commit'}",
        "staged":   staged,
        "working":  working_snapshot,
        "base":     head
    }

    stash = _read_stash()
    stash.insert(0, stash_entry)
    _write_stash(stash)

    # Restore files to last committed state
    for filepath in all_tracked:
        if filepath in head_files:
            restore_object(head_files[filepath], filepath)
        elif os.path.exists(filepath):
            os.remove(filepath)

    clear_index()
    print(f"Stashed: {stash_entry['message']}")
    print(f"Working directory restored to last commit.")


def stash_pop():
    """Restore the most recent stash entry and remove it from stack."""
    if not is_initialized():
        print("Not a mygit repository. Run 'init' first.")
        return

    stash = _read_stash()
    if not stash:
        print("No stash entries found.")
        return

    entry = stash.pop(0)

    # Restore working directory files
    for filepath, file_hash in entry["working"].items():
        parent_dir = os.path.dirname(filepath)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        restore_object(file_hash, filepath)

    # Restore staged index
    stash_index_path = get_mygit_path("index.json")
    with open(stash_index_path, "w") as f:
        json.dump(entry["staged"], f, indent=2)

    _write_stash(stash)
    print(f"Restored stash: {entry['message']}")


def stash_list():
    """Show all stash entries."""
    stash = _read_stash()
    if not stash:
        print("No stash entries.")
        return
    for i, entry in enumerate(stash):
        print(f"  stash@{{{i}}}: {entry['message']}")


def stash_drop(index=0):
    """Remove a stash entry without applying it."""
    stash = _read_stash()
    if not stash or index >= len(stash):
        print("No such stash entry.")
        return
    dropped = stash.pop(index)
    _write_stash(stash)
    print(f"Dropped stash@{{{index}}}: {dropped['message']}")