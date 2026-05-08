import os
import difflib
import json
from mygit_core.repository import get_mygit_path, is_initialized, get_head_commit
from mygit_core.hash_object import hash_file


def _read_text_smart(filepath):
    """Read a file trying UTF-8 first, then UTF-16, then latin-1 as fallback."""
    for enc in ("utf-8-sig", "utf-16", "latin-1"):
        try:
            with open(filepath, "r", encoding=enc) as f:
                return f.readlines()
        except (UnicodeDecodeError, UnicodeError):
            continue
    return []


def get_file_lines_from_blob(file_hash):
    """Read a stored object blob and return its lines."""
    object_path = get_mygit_path("objects", file_hash)
    with open(object_path, "rb") as f:
        raw = f.read()
    for enc in ("utf-8-sig", "utf-16", "latin-1"):
        try:
            return raw.decode(enc).splitlines(keepends=True)
        except (UnicodeDecodeError, UnicodeError):
            continue
    return []


def diff_file(filepath):
    """
    Compare current working file against its last committed version.
    Output mimics real git diff format.
    """
    if not is_initialized():
        print("Not a mygit repository. Run 'init' first.")
        return

    head = get_head_commit()
    if not head:
        print("No commits yet — nothing to diff against.")
        return

    commit_path = get_mygit_path("commits", f"{head}.json")
    with open(commit_path, "r") as f:
        commit = json.load(f)

    if filepath not in commit["files"]:
        print(f"'{filepath}' was not in the last commit.")
        return

    if not os.path.exists(filepath):
        print(f"'{filepath}' has been deleted.")
        return

    committed_hash = commit["files"][filepath]
    current_hash   = hash_file(filepath)

    if committed_hash == current_hash:
        print(f"No changes in '{filepath}'")
        return

    old_lines = get_file_lines_from_blob(committed_hash)
    new_lines = _read_text_smart(filepath)

    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=f"a/{filepath}",
        tofile=f"b/{filepath}",
        lineterm=""
    )

    for line in diff:
        if line.startswith("+++") or line.startswith("---"):
            print(line)
        elif line.startswith("+"):
            print(f"\033[32m{line}\033[0m")
        elif line.startswith("-"):
            print(f"\033[31m{line}\033[0m")
        elif line.startswith("@@"):
            print(f"\033[36m{line}\033[0m")
        else:
            print(line)


def diff_all():
    """Run diff on every file that was in the last commit."""
    if not is_initialized():
        print("Not a mygit repository. Run 'init' first.")
        return

    head = get_head_commit()
    if not head:
        print("No commits yet.")
        return

    commit_path = get_mygit_path("commits", f"{head}.json")
    with open(commit_path, "r") as f:
        commit = json.load(f)

    changed = False
    for filepath in commit["files"]:
        if not os.path.exists(filepath):
            print(f"\033[31mdeleted: {filepath}\033[0m")
            changed = True
            continue
        current_hash = hash_file(filepath)
        if current_hash != commit["files"][filepath]:
            diff_file(filepath)
            changed = True

    if not changed:
        print("No changes since last commit.")