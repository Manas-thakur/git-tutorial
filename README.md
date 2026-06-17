# Git Tutorial

An interactive Git tutorial that runs in your terminal. Learn Git from fundamentals to advanced workflows through reading, hands-on practice, quizzes, flashcards, challenges, and progress tracking.

## Quick Install

```bash
pip install git+https://github.com/Manas-thakur/git-tutorial.git
```

## Usage

### Textual TUI (recommended)

```bash
gittut
```

A terminal user interface with three collapsible panels:

- **Sidebar** — topic tree with progress bars and phase locking (`Ctrl+B` to toggle)
- **Content** — markdown viewer with topic navigation (`C` to toggle)
- **Terminal** — interactive git sandbox to practice commands in a real repo, with scenario mode for guided exercises

**Keybindings:**

| Key         | Action             |
|-------------|--------------------|
| `q`         | Quit               |
| `?`         | Help screen        |
| `Ctrl+B`    | Toggle sidebar     |
| `Ctrl+F`    | Search topics      |
| `Ctrl+Q`    | Quiz               |
| `Ctrl+G`    | Cheat sheet        |
| `C`         | Toggle content panel|
| `F5`        | Run command        |
| `F6`        | Show git status    |
| `F7`        | Show git log       |
| `F8`        | Show git diff      |
| `F9`        | Show commit graph  |
| `Up`/`Down` | Previous/Next topic|

### CLI

```bash
gittut-cli --help
```

| Command       | Description                                |
|---------------|--------------------------------------------|
| `list`        | List all phases and topics                 |
| `view`        | View a specific topic                      |
| `practice`    | Open sandbox with exercises for a topic    |
| `quiz`        | Take a quiz for a phase or all phases      |
| `flashcards`  | Review flashcards                          |
| `challenge`   | Run a Git challenge                        |
| `sandbox`     | Open the interactive Git sandbox           |
| `search`      | Search across all topics                   |
| `status`      | Show progress, streak, and badges          |
| `badges`      | Show earned badges                         |
| `bookmark`    | Show your current bookmark                 |
| `reset`       | Reset all progress                         |

### Examples

```bash
# List all phases and topics
gittut-cli list

# View a topic (phase 1, topic 3 — Initializing a Repository)
gittut-cli view 1 3

# Search for a keyword
gittut-cli search rebase

# Take a quiz for phase 2 (Branching & Merging)
gittut-cli quiz 2

# Open the interactive sandbox
gittut-cli sandbox

# Check your progress
gittut-cli status
```

## Content

33 topics across 6 phases:

| # | Phase                | Topics |
|---|----------------------|--------|
| 1 | Getting Started      | 8      |
| 2 | Branching & Merging  | 6      |
| 3 | Remotes              | 5      |
| 4 | Advanced             | 6      |
| 5 | Collaboration        | 5      |
| 6 | Internals            | 3      |

Each topic includes: markdown content with code examples, MCQs, and hands-on exercises.

## Features

- **Progress tracking** — XP, levels, streaks, badges, bookmarks, per-phase mastery
- **Phases unlock** sequentially — complete all topics in a phase to unlock the next
- **Git sandbox** — real git repos created on the fly; practice `add`, `commit`, `branch`, `merge`, `rebase`, and more without touching your real projects
- **Scenario mode** — guided, step-by-step practice scenarios with validation and hints
- **Collapsible panels** — hide sidebar or content to give more room to the terminal
- **Session persistence** — remembers your last topic and panel layout across restarts
- **96 quiz questions** — multiple-choice across all topics
- **18 coding challenges** — apply what you've learned in structured exercises
- **Flashcard review** — reinforce key concepts
- **Cheat sheet** — 63 git commands searchable from within the TUI (`Ctrl+G`)

## Compatibility

- **Python** >= 3.12
- **Dependencies**: `typer`, `rich`, `textual`
- **OS**: Linux, macOS, Windows (WSL recommended for Windows)
