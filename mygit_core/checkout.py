import os
import json
import glob
from mygit_core.repository import get_mygit_path, is_initialized
from mygit_core.hash_object import restore_object

def checkout_commit(commit_id_prefix):
    """Restore working files to the state of any past commit."""
    if not is_initialized():
        print("Not a mygit repository. Run 'init' first.")
        return

    commits_dir = get_mygit_path("commits")
    matches = glob.glob(os.path.join(commits_dir, f"{commit_id_prefix}*.json"))

    if not matches:
        print(f"No commit found matching: {commit_id_prefix}")
        return
    if len(matches) > 1:
        print(f"Ambiguous hash — be more specific.")
        return

    with open(matches[0], "r") as f:
        commit = json.load(f)

    for filepath, file_hash in commit["files"].items():
        parent_dir = os.path.dirname(filepath)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        restore_object(file_hash, filepath)
        print(f"Restored: {filepath}")

    with open(get_mygit_path("HEAD"), "w") as f:
        f.write(commit["id"])

    print(f"\nChecked out → {commit['id'][:7]}: {commit['message']}")