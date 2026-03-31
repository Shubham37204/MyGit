# mygit.py

import argparse
import sys
from mygit_core.log import show_log
from mygit_core.repository import init
from mygit_core.index import add_file
from mygit_core.commit import create_commit
from mygit_core.status import show_status
from mygit_core.checkout import checkout_commit
from mygit_core.branch import create_branch, list_branches, switch_branch

def main():
    parser = argparse.ArgumentParser(
        prog="mygit",
        description="A simplified Git-like version control system."
    )

    subparsers = parser.add_subparsers(
        dest="command",
        metavar="command"
    )

    # init — no extra arguments
    subparsers.add_parser(
        "init",
        help="Initialize a new mygit repository"
    )

    subparsers.add_parser("log", help="Show commit history")
    subparsers.add_parser("status", help="Show staged and modified files")
    checkout_parser = subparsers.add_parser("checkout", help="Restore files to a past commit")
    checkout_parser.add_argument("commit_id", help="Full or short commit hash")

    # branch — create or list branches
    branch_parser = subparsers.add_parser("branch", help="Create or list branches")
    branch_parser.add_argument("name", nargs="?", help="Branch name to create (omit to list)")

    # switch — change current branch
    switch_parser = subparsers.add_parser("switch", help="Switch to a branch")
    switch_parser.add_argument("name", help="Branch name to switch to")

    # add — requires a filename
    add_parser = subparsers.add_parser(
        "add",
        help="Stage a file for the next commit"
    )
    add_parser.add_argument(
        "filename",
        help="Path to the file to stage"
    )
    # commit — requires -m "message"
    commit_parser = subparsers.add_parser(
        "commit",
        help="Save staged files as a commit snapshot"
    )
    commit_parser.add_argument(
        "-m",
        dest="message",
        required=True,
        help="Commit message"
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "init":
        init()

    elif args.command == "add":
        add_file(args.filename)

    elif args.command == "commit":
        create_commit(args.message)

    elif args.command == "log":
        show_log()

    elif args.command == "status":
        show_status()

    elif args.command == "checkout":
        checkout_commit(args.commit_id)
    elif args.command == "branch":
        if args.name:
            create_branch(args.name)
        else:
            list_branches()

    elif args.command == "switch":
        switch_branch(args.name)

    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)


if __name__ == "__main__":
    main()

