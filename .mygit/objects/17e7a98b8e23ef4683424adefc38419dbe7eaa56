import json
import os
import hashlib
from datetime import datetime, timezone
from mygit_core.repository import get_mygit_path, is_initialized, get_head_commit, get_current_branch
from mygit_core.index import get_staged_files, clear_index

import os

def get_current_head():
    head_path = os.path.join(".mygit", "HEAD")
    
    if not os.path.exists(head_path):
        return None

    with open(head_path, "r") as f:
        return f.read().strip()

def get_author():
    config_path = get_mygit_path("config.json")
    with open(config_path, "r") as f:
        config = json.load(f)
    return config.get("author", "Unknown"), config.get("email", "")


def generate_commit_hash(message, timestamp, files):
    raw = f"{message}{timestamp}{json.dumps(files, sort_keys=True)}"
    return hashlib.sha1(raw.encode()).hexdigest()


def create_commit(message):
    if not is_initialized():
        print("Not a mygit repository. Run 'init' first.")
        return

    staged = get_staged_files()
    if not staged:
        print("Nothing to commit. Stage files with 'add' first.")
        return

    author, email   = get_author()
    timestamp       = datetime.now(timezone.utc).isoformat()
    parent          = get_head_commit()          
    commit_hash     = generate_commit_hash(message, timestamp, staged)

    commit_data = {
        "id":        commit_hash,
        "message":   message,
        "author":    author,
        "email":     email,
        "timestamp": timestamp,
        "parent":    parent,
        "files":     staged
    }

    commit_path = get_mygit_path("commits", f"{commit_hash}.json")
    with open(commit_path, "w") as f:
        json.dump(commit_data, f, indent=2)

    branch = get_current_branch()
    if branch:
        branch_file = get_mygit_path("refs", "heads", branch)
        with open(branch_file, "w") as f:
            f.write(commit_hash)
    else:
        with open(get_mygit_path("HEAD"), "w") as f:
            f.write(commit_hash)

    log_path = get_mygit_path("log.json")
    with open(log_path, "r") as f:
        log = json.load(f)
    log.insert(0, {
        "id":        commit_hash,
        "message":   message,
        "author":    author,
        "timestamp": timestamp,
        "branch":    branch or "detached"       
    })
    with open(log_path, "w") as f:
        json.dump(log, f, indent=2)

    clear_index()
    branch_label = f"({branch})" if branch else "(detached HEAD)"
    print(f"Committed: {message}")
    print(f"ID: {commit_hash[:7]}  {branch_label}")

