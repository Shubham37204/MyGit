import os
import json
import glob
from mygit_core.repository import get_mygit_path, is_initialized
from mygit_core.hash_object import restore_object


def resolve_to_commit_hash(ref):
    """
    Given a ref (short hash, full hash, or tag name),
    return a full commit hash. Returns None if nothing matches.
    """
    # Try as a tag first
    from mygit_core.tag import resolve_tag
    tag_hash = resolve_tag(ref)
    if tag_hash:
        return tag_hash

    # Try as a full or short commit hash
    commits_dir = get_mygit_path("commits")
    matches = glob.glob(os.path.join(commits_dir, f"{ref}*.json"))
    if len(matches) == 1:
        return os.path.basename(matches[0]).replace(".json", "")
    if len(matches) > 1:
        print(f"Ambiguous ref '{ref}' — be more specific.")
        return None

    return None


def checkout_commit(ref):
    """
    Restore working files to the state of any past commit.
    Accepts: full hash, short hash, or tag name.
    """
    if not is_initialized():
        print("Not a mygit repository. Run 'init' first.")
        return

    commit_hash = resolve_to_commit_hash(ref)

    if not commit_hash:
        print(f"No commit, branch, or tag found matching: '{ref}'")
        return

    commit_path = get_mygit_path("commits", f"{commit_hash}.json")
    with open(commit_path, "r") as f:
        commit = json.load(f)

    for filepath, file_hash in commit["files"].items():
        parent_dir = os.path.dirname(filepath)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        restore_object(file_hash, filepath)
        print(f"Restored: {filepath}")

    # Detached HEAD — point directly at the commit hash
    with open(get_mygit_path("HEAD"), "w") as f:
        f.write(commit_hash)

    print(f"\nChecked out → {commit_hash[:7]}: {commit['message']}")
    print("(detached HEAD — you are not on any branch)")