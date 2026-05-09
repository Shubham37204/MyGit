import os
from mygit_core.repository import (
    get_mygit_path, is_initialized,
    get_current_branch, get_head_commit
)

def create_branch(branch_name):
    """
    Create a new branch pointing to the current HEAD commit.
    Does NOT switch to it — just creates the pointer file.
    """
    if not is_initialized():
        print("Not a mygit repository. Run 'init' first.")
        return

    branch_file = get_mygit_path("refs", "heads", branch_name)

    if os.path.exists(branch_file):
        print(f"Branch '{branch_name}' already exists.")
        return

    current_commit = get_head_commit()
    if not current_commit:
        print("Cannot create branch — no commits yet. Make a commit first.")
        return

    with open(branch_file, "w") as f:
        f.write(current_commit)

    print(f"Created branch '{branch_name}' at {current_commit[:7]}")


def list_branches():
    """List all branches, marking the current one with a star."""
    if not is_initialized():
        print("Not a mygit repository. Run 'init' first.")
        return

    heads_dir = get_mygit_path("refs", "heads")
    current   = get_current_branch()

    branches = sorted(os.listdir(heads_dir))
    if not branches:
        print("No branches yet.")
        return

    for branch in branches:
        marker = "* " if branch == current else "  "
        print(f"{marker}{branch}")


def switch_branch(branch_name):
    """
    Switch to an existing branch.
    Updates HEAD to point to the new branch.
    Restores all files from that branch's latest commit.
    """
    if not is_initialized():
        print("Not a mygit repository. Run 'init' first.")
        return

    branch_file = get_mygit_path("refs", "heads", branch_name)
    if not os.path.exists(branch_file):
        print(f"Branch '{branch_name}' does not exist.")
        return

    with open(get_mygit_path("HEAD"), "w") as f:
        f.write(f"ref: refs/heads/{branch_name}")

    with open(branch_file, "r") as f:
        commit_hash = f.read().strip()

    if commit_hash:
        import json
        from mygit_core.hash_object import restore_object
        commit_path = get_mygit_path("commits", f"{commit_hash}.json")
        with open(commit_path, "r") as f:
            commit = json.load(f)
        for filepath, file_hash in commit["files"].items():
            parent_dir = os.path.dirname(filepath)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
            restore_object(file_hash, filepath)

    print(f"Switched to branch '{branch_name}'")