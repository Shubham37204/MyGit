import os
import json
from mygit_core.repository import get_mygit_path, is_initialized, get_head_commit
from mygit_core.index import get_staged_files
from mygit_core.hash_object import hash_file


def get_last_commit_files():
    """Return the files dict from the last commit, or empty dict if no commits yet."""
    head = get_head_commit()          
    if not head:
        return {}
    commit_path = get_mygit_path("commits", f"{head}.json")
    with open(commit_path, "r") as f:
        commit = json.load(f)
    return commit["files"]


def show_status():
    """Compare working directory against staged index and last commit."""
    if not is_initialized():
        print("Not a mygit repository. Run 'init' first.")
        return

    staged    = get_staged_files()
    committed = get_last_commit_files()

    print("\nChanges staged for commit:")
    if staged:
        for f in staged:
            if f not in committed:
                print(f"  new file:   {f}")
            elif staged[f] != committed[f]:
                print(f"  modified:   {f}")
            else:
                print(f"  unchanged:  {f}")
    else:
        print("  (nothing staged)")

    print("\nChanges not staged for commit:")
    unstaged = []
    for f in committed:
        if os.path.exists(f):
            if hash_file(f) != committed[f] and f not in staged:
                unstaged.append(f)
    if unstaged:
        for f in unstaged:
            print(f"  modified:   {f}")
    else:
        print("  (nothing)")

    print("\nUntracked files:")
    all_known = set(staged) | set(committed)
    untracked = [
        f for f in os.listdir(".")
        if os.path.isfile(f)
        and f not in all_known
        and not f.startswith(".")
        and f not in ("mygit.py", "requirements.txt")
    ]
    if untracked:
        for f in untracked:
            print(f"  {f}")
    else:
        print("  (nothing)")
    print()