import json
import os
from mygit_core.repository import get_mygit_path, is_initialized


def show_log(graph=False):
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

    if graph:
        _show_graph(log)
    else:
        for entry in log:
            branch = entry.get("branch", "")
            branch_label = f" \033[33m({branch})\033[0m" if branch else ""
            print(f"\033[33mcommit {entry['id']}\033[0m{branch_label}")
            print(f"Author: {entry['author']}")
            print(f"Date:   {entry['timestamp']}")
            print(f"\n    {entry['message']}\n")
            print("-" * 40)


def _show_graph(log):
    """
    Render an ASCII branch graph from the commit log.
    Groups commits by branch and draws connecting lines.
    """
    # Collect unique branches in order they appear
    branch_order = []
    seen = set()
    for entry in log:
        b = entry.get("branch", "detached")
        if b not in seen:
            branch_order.append(b)
            seen.add(b)

    col_width = 4  # characters per branch column

    for entry in log:
        branch  = entry.get("branch", "detached")
        col_idx = branch_order.index(branch)
        short   = entry["id"][:7]

        # Build graph line: pipes for active branches, node for current
        graph_part = ""
        for i, b in enumerate(branch_order):
            if i == col_idx:
                graph_part += "\033[33m*\033[0m   "   # yellow asterisk = commit node
            else:
                graph_part += "\033[34m|\033[0m   "   # blue pipe = branch line

        print(f"{graph_part}\033[33m{short}\033[0m  {entry['message']}  "
              f"\033[90m({entry.get('branch','?')} · {entry['author']} · "
              f"{entry['timestamp'][:10]})\033[0m")

    # Print branch name footer
    footer = ""
    for b in branch_order:
        footer += f"\033[34m|\033[0m   "
    print(footer)
    print("  ".join(f"\033[34m{b}\033[0m" for b in branch_order))