# mygit_core/tag.py

import os
from mygit_core.repository import (
    get_mygit_path, is_initialized, get_head_commit
)


def create_tag(tag_name, commit_hash=None):
    """
    Create a tag pointing to a specific commit.
    If no commit_hash given, tag the current HEAD commit.
    """
    if not is_initialized():
        print("Not a mygit repository. Run 'init' first.")
        return

    tag_file = get_mygit_path("refs", "tags", tag_name)

    if os.path.exists(tag_file):
        print(f"Tag '{tag_name}' already exists.")
        return

    target = commit_hash or get_head_commit()

    if not target:
        print("Cannot create tag — no commits yet.")
        return

    # Validate the commit exists if a hash was provided manually
    if commit_hash:
        commit_path = get_mygit_path("commits", f"{commit_hash}.json")
        if not os.path.exists(commit_path):
            print(f"Commit '{commit_hash}' not found.")
            return

    with open(tag_file, "w") as f:
        f.write(target)

    print(f"Tagged '{tag_name}' → {target[:7]}")


def list_tags():
    """List all tags with their commit hashes."""
    if not is_initialized():
        print("Not a mygit repository. Run 'init' first.")
        return

    tags_dir = get_mygit_path("refs", "tags")
    tags = sorted(os.listdir(tags_dir))

    if not tags:
        print("No tags yet.")
        return

    for tag in tags:
        tag_file = get_mygit_path("refs", "tags", tag)
        with open(tag_file, "r") as f:
            commit_hash = f.read().strip()
        print(f"  {tag}  →  {commit_hash[:7]}")


def resolve_tag(name):
    """
    Given a name, check if it's a tag and return the commit hash.
    Returns None if no tag with that name exists.
    Used by checkout.py to support 'checkout v1.0'.
    """
    tag_file = get_mygit_path("refs", "tags", name)
    if not os.path.exists(tag_file):
        return None
    with open(tag_file, "r") as f:
        return f.read().strip()


def delete_tag(tag_name):
    """Delete a tag by name."""
    if not is_initialized():
        print("Not a mygit repository. Run 'init' first.")
        return

    tag_file = get_mygit_path("refs", "tags", tag_name)
    if not os.path.exists(tag_file):
        print(f"Tag '{tag_name}' does not exist.")
        return

    os.remove(tag_file)
    print(f"Deleted tag '{tag_name}'")