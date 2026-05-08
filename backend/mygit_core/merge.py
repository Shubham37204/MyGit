import os
import json
from mygit_core.repository import (
    get_mygit_path, is_initialized,
    get_current_branch, get_head_commit
)
from mygit_core.hash_object import restore_object, store_object, hash_file
from mygit_core.commit import create_commit
from mygit_core.index import read_index, write_index


def _load_commit(commit_hash):
    """Load a commit JSON by hash. Returns dict or None."""
    if not commit_hash:
        return None
    path = get_mygit_path("commits", f"{commit_hash}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)


def _get_commit_chain(commit_hash):
    """
    Walk the parent chain from commit_hash to the root.
    Returns an ordered list of commit hashes, newest first.
    """
    chain = []
    current = commit_hash
    while current:
        chain.append(current)
        commit = _load_commit(current)
        if not commit:
            break
        current = commit.get("parent")
    return chain


def _find_common_ancestor(hash_a, hash_b):
    """
    Find the most recent commit reachable from both hash_a and hash_b.
    This is the merge base — the point where the two branches diverged.
    """
    ancestors_a = set(_get_commit_chain(hash_a))
    for commit in _get_commit_chain(hash_b):
        if commit in ancestors_a:
            return commit
    return None


def _read_object_text(file_hash):
    """Read a stored blob as text lines."""
    obj_path = get_mygit_path("objects", file_hash)
    with open(obj_path, "rb") as f:
        return f.read().decode("utf-8", errors="replace").splitlines()


def _three_way_merge_file(base_hash, ours_hash, theirs_hash, filepath):
    """
    Merge three versions of a file.
    Returns (merged_lines, has_conflict).
    Inserts conflict markers where both sides changed the same region.
    """
    base   = _read_object_text(base_hash)   if base_hash   else []
    ours   = _read_object_text(ours_hash)   if ours_hash   else []
    theirs = _read_object_text(theirs_hash) if theirs_hash else []

    import difflib
    matcher_ours   = difflib.SequenceMatcher(None, base, ours)
    matcher_theirs = difflib.SequenceMatcher(None, base, theirs)

    opcodes_ours   = matcher_ours.get_opcodes()
    opcodes_theirs = matcher_theirs.get_opcodes()

    merged = []
    has_conflict = False

    our_changes    = {old: new for tag, i1, i2, j1, j2
                      in opcodes_ours   if tag != "equal"
                      for old, new in zip(base[i1:i2], ours[j1:j2])}
    their_changes  = {old: new for tag, i1, i2, j1, j2
                      in opcodes_theirs if tag != "equal"
                      for old, new in zip(base[i1:i2], theirs[j1:j2])}

    for line in base:
        in_ours   = line in our_changes
        in_theirs = line in their_changes

        if in_ours and in_theirs:
            if our_changes[line] == their_changes[line]:
                merged.append(our_changes[line])
            else:
                has_conflict = True
                merged.append(f"<<<<<<< ours")
                merged.append(our_changes[line])
                merged.append("=======")
                merged.append(their_changes[line])
                merged.append(">>>>>>> theirs")
        elif in_ours:
            merged.append(our_changes[line])
        elif in_theirs:
            merged.append(their_changes[line])
        else:
            merged.append(line)

    return merged, has_conflict


def merge_branch(branch_name):
    """
    Merge branch_name into the current branch.
    Attempts fast-forward first, falls back to three-way merge.
    """
    if not is_initialized():
        print("Not a mygit repository. Run 'init' first.")
        return

    current_branch = get_current_branch()
    if not current_branch:
        print("Cannot merge in detached HEAD state. Switch to a branch first.")
        return

    if branch_name == current_branch:
        print("Already on this branch — nothing to merge.")
        return

    target_branch_file = get_mygit_path("refs", "heads", branch_name)
    if not os.path.exists(target_branch_file):
        print(f"Branch '{branch_name}' does not exist.")
        return

    with open(target_branch_file, "r") as f:
        their_hash = f.read().strip()

    our_hash = get_head_commit()

    if not our_hash:
        print("No commits on current branch. Commit something first.")
        return

    print(f"Merging '{branch_name}' into '{current_branch}'...")

    their_chain = _get_commit_chain(their_hash)
    if our_hash in their_chain:
        branch_file = get_mygit_path("refs", "heads", current_branch)
        with open(branch_file, "w") as f:
            f.write(their_hash)

        their_commit = _load_commit(their_hash)
        for filepath, file_hash in their_commit["files"].items():
            parent_dir = os.path.dirname(filepath)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
            restore_object(file_hash, filepath)

        print(f"Fast-forward merge complete → {their_hash[:7]}")
        print(f"Files updated: {list(their_commit['files'].keys())}")
        return

    ancestor_hash = _find_common_ancestor(our_hash, their_hash)
    print(f"Common ancestor: {ancestor_hash[:7] if ancestor_hash else 'none'}")

    our_commit    = _load_commit(our_hash)
    their_commit  = _load_commit(their_hash)
    base_commit   = _load_commit(ancestor_hash) if ancestor_hash else None

    our_files    = our_commit["files"]
    their_files  = their_commit["files"]
    base_files   = base_commit["files"] if base_commit else {}

    all_files    = set(our_files) | set(their_files)
    has_conflict = False
    new_index    = dict(our_files)  

    for filepath in all_files:
        base_hash  = base_files.get(filepath)
        our_hash_f = our_files.get(filepath)
        their_hash_f = their_files.get(filepath)

        if our_hash_f == base_hash and their_hash_f != base_hash:
            if their_hash_f:
                restore_object(their_hash_f, filepath)
                new_index[filepath] = their_hash_f
                print(f"  Updated (theirs): {filepath}")
            continue

        if their_hash_f == base_hash:
            continue

        if our_hash_f and their_hash_f:
            merged_lines, conflict = _three_way_merge_file(
                base_hash, our_hash_f, their_hash_f, filepath
            )
            merged_content = "\n".join(merged_lines) + "\n"
            with open(filepath, "w") as f:
                f.write(merged_content)

            if conflict:
                has_conflict = True
                print(f"  \033[31mCONFLICT: {filepath} — resolve manually\033[0m")
            else:
                file_hash = store_object(filepath)
                new_index[filepath] = file_hash
                print(f"  Merged: {filepath}")
        elif their_hash_f and not our_hash_f:
            restore_object(their_hash_f, filepath)
            new_index[filepath] = their_hash_f

    if has_conflict:
        write_index(new_index)
        print(f"\n\033[31mMerge has conflicts. Fix files marked with <<<<<<< then commit.\033[0m")
        return

    write_index(new_index)
    create_commit(f"Merge branch '{branch_name}' into '{current_branch}'")
    print(f"\nMerge complete.")