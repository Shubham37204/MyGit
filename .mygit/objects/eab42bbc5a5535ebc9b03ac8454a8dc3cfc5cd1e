import os
import json

MYGIT_DIR = ".mygit"

def get_mygit_path(*paths):
    """Build a path inside .mygit/"""
    return os.path.join(MYGIT_DIR, *paths)

def is_initialized():
    """Returns True if .mygit/ exists"""
    return os.path.isdir(MYGIT_DIR)

def init():
    """Creates the entire .mygit/ folder structure"""
    if is_initialized():
        print("Repository already initialized.")
        return

    os.makedirs(get_mygit_path("commits"))
    os.makedirs(get_mygit_path("objects"))
    os.makedirs(get_mygit_path("refs", "heads"))  
    os.makedirs(get_mygit_path("refs", "tags")) 


    with open(get_mygit_path("HEAD"), "w") as f:
        f.write("ref: refs/heads/main")           

    with open(get_mygit_path("index.json"), "w") as f:
        json.dump({}, f)

    with open(get_mygit_path("log.json"), "w") as f:
        json.dump([], f)

    with open(get_mygit_path("config.json"), "w") as f:
        json.dump({"author": "Your Name", "email": "you@example.com"}, f, indent=2)

    print("Initialized empty mygit repository in .mygit/")
    print("On branch: main")


def get_current_branch():
    """
    Read HEAD. If it contains 'ref: refs/heads/main' return 'main'.
    If it contains a raw hash (detached HEAD), return None.
    """
    head_path = get_mygit_path("HEAD")
    with open(head_path, "r") as f:
        content = f.read().strip()

    if content.startswith("ref: refs/heads/"):
        return content[len("ref: refs/heads/"):]   
    return None  


def get_head_commit():
    """
    Resolve HEAD all the way to a commit hash.
    Works whether HEAD is a branch ref or a raw hash.
    Returns None if no commits exist yet.
    """
    head_path = get_mygit_path("HEAD")
    with open(head_path, "r") as f:
        content = f.read().strip()

    if content.startswith("ref: refs/heads/"):
        branch = content[len("ref: refs/heads/"):]
        branch_file = get_mygit_path("refs", "heads", branch)
        if not os.path.exists(branch_file):
            return None   
        with open(branch_file, "r") as f:
            return f.read().strip() or None
    return content if content else None