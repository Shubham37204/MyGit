import argparse
import sys

from mygit_core.repository import init
from mygit_core.index import add_file
from mygit_core.commit import create_commit
from mygit_core.log import show_log
from mygit_core.status import show_status
from mygit_core.checkout import checkout_commit
from mygit_core.branch import create_branch, list_branches, switch_branch
from mygit_core.tag import create_tag, list_tags, delete_tag
from mygit_core.diff import diff_file, diff_all
from mygit_core.stash import stash_push, stash_pop, stash_list, stash_drop
from mygit_core.merge import merge_branch

def main():
    parser = argparse.ArgumentParser(
        prog="mygit",
        description="A simplified Git-like version control system."
    )
    subparsers = parser.add_subparsers(dest="command", metavar="command")

    # init
    subparsers.add_parser("init", help="Initialize a new repository")

    # add
    add_parser = subparsers.add_parser("add", help="Stage a file")
    add_parser.add_argument("filename", help="File to stage")

    # commit
    commit_parser = subparsers.add_parser("commit", help="Save staged snapshot")
    commit_parser.add_argument("-m", dest="message", required=True, help="Commit message")

    # log
    log_parser = subparsers.add_parser("log", help="Show commit history")
    log_parser.add_argument("--graph", action="store_true", help="Show ASCII branch graph")

    # status
    subparsers.add_parser("status", help="Show staged and modified files")

    # checkout
    checkout_parser = subparsers.add_parser("checkout", help="Restore files to a past commit")
    checkout_parser.add_argument("commit_id", help="Hash, short hash, or tag name")

    # branch
    branch_parser = subparsers.add_parser("branch", help="Create or list branches")
    branch_parser.add_argument("name", nargs="?", help="Branch name (omit to list)")

    # switch
    switch_parser = subparsers.add_parser("switch", help="Switch to a branch")
    switch_parser.add_argument("name", help="Branch name")

    # tag
    tag_parser = subparsers.add_parser("tag", help="Create, list, or delete tags")
    tag_parser.add_argument("name", nargs="?", help="Tag name (omit to list)")
    tag_parser.add_argument("commit", nargs="?", help="Commit hash to tag (default: HEAD)")
    tag_parser.add_argument("-d", dest="delete", help="Delete a tag by name")

    # diff
    diff_parser = subparsers.add_parser("diff", help="Show changes since last commit")
    diff_parser.add_argument("filename", nargs="?", help="File to diff (omit for all)")

    # stash
    stash_parser = subparsers.add_parser("stash", help="Stash or restore uncommitted changes")
    stash_parser.add_argument("subcommand", nargs="?", default="push",
                              choices=["push", "pop", "list", "drop"])
    stash_parser.add_argument("-m", dest="message", help="Stash message")

    merge_parser = subparsers.add_parser("merge", help="Merge a branch into current branch")
    merge_parser.add_argument("branch", help="Branch name to merge in")

    # ── router ──────────────────────────────────────────────
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
        show_log(graph=args.graph)
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
    elif args.command == "tag":
        if args.delete:
            delete_tag(args.delete)
        elif args.name:
            create_tag(args.name, args.commit)
        else:
            list_tags()
    elif args.command == "diff":
        if args.filename:
            diff_file(args.filename)
        else:
            diff_all()
    elif args.command == "stash":
        sub = args.subcommand
        if sub == "push":
            stash_push(args.message)
        elif sub == "pop":
            stash_pop()
        elif sub == "list":
            stash_list()
        elif sub == "drop":
            stash_drop()
    elif args.command == "merge":
        merge_branch(args.branch)
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)


if __name__ == "__main__":
    main()