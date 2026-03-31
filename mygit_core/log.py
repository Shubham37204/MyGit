import json
from mygit_core.repository import get_mygit_path, is_initialized

def show_log():
    """Read log.json and display commit history, newest first."""
    if not is_initialized():
        print("Not a mygit repository. Run 'init' first.")
        return

    log_path = get_mygit_path("log.json")
    with open(log_path, "r") as f:
        log = json.load(f)

    if not log:
        print("No commits yet.")
        return

    for entry in log:
        print(f"commit {entry['id']}")
        print(f"Author: {entry['author']}")
        print(f"Date:   {entry['timestamp']}")
        print(f"\n    {entry['message']}\n")
        print("-" * 40)