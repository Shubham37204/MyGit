# MyGit — A Git Clone Built from Scratch in Python

A fully functional version control system built from the ground up in Python,
implementing Git's core internals: content-addressable storage, branching,
three-way merging, diffing, stashing, and conflict detection.

> Built to deeply understand how Git works under the hood — not as a tutorial
> exercise, but as a production-structured project with a real CLI, modular
> architecture, and 20 passing unit tests.

## Features

| Command | Description |
|---|---|
| `mygit init` | Initialize repository — creates full `.mygit/` structure |
| `mygit add <file>` | Stage a file — SHA1 hash + store blob in `objects/` |
| `mygit add .` | Stage all files, respecting `.mygitignore` patterns |
| `mygit commit -m "msg"` | Snapshot staged files with parent chaining |
| `mygit log` | Commit history, newest first |
| `mygit log --graph` | ASCII branch graph showing divergence points |
| `mygit status` | Staged / modified / untracked file comparison |
| `mygit diff <file>` | Colored line-by-line diff against last commit |
| `mygit branch` | List branches — marks current with `*` |
| `mygit branch <name>` | Create a new branch at current HEAD |
| `mygit switch <name>` | Switch branches — restores working directory |
| `mygit merge <branch>` | Fast-forward or three-way merge with conflict markers |
| `mygit tag` | List all tags |
| `mygit tag <name>` | Tag current HEAD commit with a human-readable name |
| `mygit tag -d <name>` | Delete a tag |
| `mygit checkout <ref>` | Restore files to any commit hash, short hash, or tag |
| `mygit stash` | Save uncommitted changes, restore working dir to HEAD |
| `mygit stash pop` | Restore most recent stash entry |
| `mygit stash list` | Show all stash entries |
| `mygit stash drop` | Discard a stash entry without applying it |


## Architecture
```
mygit/
├── mygit.py                 # CLI entry point (argparse — routes to core)
│
├── mygit_core/
│   ├── repository.py        # Path management, init, HEAD + branch resolution
│   ├── hash_object.py       # SHA1 content-addressable blob storage
│   ├── index.py             # Staging area + .mygitignore support
│   ├── commit.py            # Snapshot creation, parent chaining
│   ├── branch.py            # Branch create / list / switch
│   ├── tag.py               # Tag create / list / delete / resolve
│   ├── merge.py             # Fast-forward + three-way merge + conflict detection
│   ├── diff.py              # Unified diff with color output (difflib)
│   ├── stash.py             # Stash stack — push / pop / list / drop
│   ├── log.py               # History display + ASCII branch graph
│   ├── status.py            # Working tree vs index vs last commit
│   └── checkout.py          # Ref resolution + file restore
└── tests/
    ├── test_hash.py         # SHA1 hashing, deduplication, blob restore
    ├── test_index.py        # Staging, re-staging, clear, multi-file
    └── test_commit.py       # Commit creation, HEAD, log, parent chain
```

## How It Works — Key Design Decisions

### Content-addressable storage

Every file is stored by the SHA1 hash of its content — identical to how
real Git stores objects. Duplicate content is stored exactly once,
regardless of how many commits reference it.
```
README.md  →  SHA1(content)  →  "a1b2c3..."
                                 .mygit/objects/a1b2c3...  ← raw bytes
```

The hash is the file's address. If content changes by one character,
the hash is completely different. If content is identical, the hash
is the same and the blob is not written twice.

### Branches are just files

A branch is a text file inside `.mygit/refs/heads/` containing a commit hash.
Creating a branch costs one file write — O(1), no copying, no duplication.
```
.mygit/
├── HEAD                     → "ref: refs/heads/main"   (symbolic ref)
└── refs/heads/
    ├── main                 → "4e63f43..."
    └── feature-x            → "38b463c..."
```

`HEAD` points to a branch name, not a commit directly. When you commit,
the current branch file updates. When you switch, HEAD changes and files
are restored from that branch's tip commit.

### Three-way merge

When two branches diverge, merge walks the parent chain to find the
common ancestor commit, then applies changes from both sides independently.
If both sides modified the same line differently, conflict markers are inserted:
```
<<<<<<< ours
your version of the line
=======
their version of the line
>>>>>>> theirs
```

Fast-forward merge is attempted first — if one branch is a direct ancestor
of the other, the pointer simply moves forward with no new commit needed.

### The three-layer model
```
Layer 1 — .mygit/objects/    committed blobs      permanent, content-addressed
Layer 2 — .mygit/index.json  staging area         intentional, pre-commit snapshot
Layer 3 — working directory  current files        in progress, uncommitted

stash captures layers 2 + 3, drops you back to layer 1
```


## Setup
```bash
git clone <repo-url>
cd mygit
python mygit.py init
```

No external dependencies — uses Python standard library only:
`hashlib`, `difflib`, `argparse`, `json`, `os`, `fnmatch`, `datetime`, `glob`.


## Run Tests
```bash
python -m unittest discover -s tests -v
```

20 tests covering SHA1 correctness, deduplication, blob restore,
staging, re-staging after modification, commit creation, HEAD tracking,
log ordering, parent chaining, and graceful failure on edge cases.


## What I Learned Building This

- How Git's object store achieves deduplication through content-addressing
- Why branches are cheap — they are 40-byte pointer files, nothing more
- How `HEAD` is a symbolic ref to a branch, not a direct commit pointer
- The difference between fast-forward and three-way merge, and when
  each applies
- How `difflib.unified_diff` produces the same `+`/`-` format as `git diff`
- Why the staging area exists as a deliberate layer — decoupling
  "what changed" from "what I want to commit"
- How stash operates on the three-layer working tree model
