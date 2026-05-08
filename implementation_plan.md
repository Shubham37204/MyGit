# Implementation Plan - MyGit Professional UI & Reorganization

This plan outlines the restructuring of the MyGit project into a modern Full-Stack application and the implementation of a professional, developer-centric UI.

## User Review Required

> [!IMPORTANT]
> The project structure will change. Existing scripts will need to be run from the `backend/` directory.

> [!NOTE]
> The UI will follow a "Developer Tool" aesthetic: charcoal/slate tones, high-density information, and no flashy AI-style effects.

## Proposed Changes

### Project Restructuring

#### [NEW] `backend/`
- Move `mygit.py`, `mygit_core/`, and `tests/` into this directory.
- This keeps the core logic isolated and clean.

#### [NEW] `frontend/`
- Initialize a React + Vite + Tailwind CSS project here.

---

### Backend Layer (Python/FastAPI)

#### [NEW] `backend/api.py`
- Create a FastAPI application.
- Import existing functions from `mygit_core`.
- Implement endpoints for:
    - Status (staged/unstaged/untracked)
    - History (log with graph data)
    - Branching (list/create/switch)
    - Diffing (file-specific diffs)
    - Operations (add, commit, stash, merge)

---

### Frontend Layer (React + Tailwind)

#### [NEW] Design System
- **Theme**: Charcoal (`#121212`) background, Slate (`#1e293b`) panels, Muted Blue (`#3b82f6`) highlights.
- **Typography**: Inter (UI), JetBrains Mono (Code).
- **Layout**: 3-panel system (Navigation Sidebar, Status/Files Panel, Main Content/Diff Area).

#### [NEW] Key Components
- `FileStatusList`: Interactive list of changed files with staging toggles.
- `DiffViewer`: Clean, syntax-highlighted code comparison.
- `CommitHistory`: Vertical timeline with a structural branch graph.
- `CommitControls`: Message input and primary action buttons.

---

## Verification Plan

### Automated Tests
- Run existing unit tests in `backend/` using `python -m unittest discover`.
- Verify API endpoints using FastAPI's Swagger UI (`/docs`).

### Manual Verification
1. Open the UI and verify the repository status matches the CLI output.
2. Stage a file via the UI and verify it shows as staged in `mygit status`.
3. Switch a branch via the UI and check the working directory files.
4. Perform a commit and verify it appears in the History view.
