from dataclasses import dataclass, field
from typing import Callable, Optional
import re

from .sandbox import GitSandbox


@dataclass
class Step:
    expected_pattern: str
    description: str
    hint: str


@dataclass
class Scenario:
    phase: int
    topic: int
    title: str
    goal: str
    setup_commands: list[str] = field(default_factory=list)
    steps: list[Step] = field(default_factory=list)
    start_message: str = ""


def _matches(cmd: str, pattern: str) -> bool:
    return bool(re.search(pattern, cmd.strip(), re.IGNORECASE))


def _run_setup(sandbox: GitSandbox, setup: list[str]) -> None:
    for c in setup:
        sandbox.run_command(c)


def _get_branches(sandbox: GitSandbox) -> list[str]:
    r = sandbox._safe_run(["git", "branch"])
    if r["success"] and r["stdout"]:
        return [b.strip().lstrip("* ") for b in r["stdout"].splitlines() if b.strip()]
    return []


def _get_commits(sandbox: GitSandbox) -> int:
    r = sandbox._safe_run(["git", "log", "--oneline"])
    if r["success"] and r["stdout"]:
        return len(r["stdout"].splitlines())
    return 0


def _has_merge_commit(sandbox: GitSandbox) -> bool:
    r = sandbox._safe_run(["git", "log", "--oneline", "--merges", "-1"])
    return r["success"] and bool(r["stdout"].strip())


def _file_exists(sandbox: GitSandbox, path: str) -> bool:
    return (sandbox.repo_path / path).exists()


def _git_modified(sandbox: GitSandbox) -> bool:
    r = sandbox._safe_run(["git", "status", "--porcelain"])
    return r["success"] and bool(r["stdout"].strip())


SCENARIOS: dict[str, Scenario] = {
    "1.2": Scenario(
        phase=1, topic=2,
        title="Your First Repo",
        goal="Initialize a Git repository, create a file, stage it, and make your first commit.",
        start_message="Let's create your first Git repository! Follow the steps below.",
        setup_commands=[],
        steps=[
            Step(r"git init", "Initialize a new repository", "Type: git init"),
            Step(r"echo.*>?\s*READ", "Create a README file", "Type: echo '# My Project' > README.md"),
            Step(r"git add README", "Stage the README file", "Type: git add README.md"),
            Step(r'git commit.*-m.*first|git commit.*-m.*initial', "Commit the staged file", "Type: git commit -m 'First commit'"),
            Step(r"git log", "View commit history", "Type: git log --oneline"),
        ],
    ),
    "1.4": Scenario(
        phase=1, topic=4,
        title="Tracking Changes",
        goal="Modify a tracked file, stage the change, and commit it. Practice the edit-stage-commit cycle.",
        start_message="You have a repo with one commit. Now make changes and track them.",
        setup_commands=[
            "git init",
            "git config user.name Test",
            "git config user.email test@test.com",
            "echo 'line 1' > file.txt",
            "git add file.txt",
            "git commit -m 'Initial commit'",
        ],
        steps=[
            Step(r"echo.*line 2.*>>? *file", "Add a second line to file.txt", "Type: echo 'line 2' >> file.txt"),
            Step(r"git status", "Check the status of your changes", "Type: git status"),
            Step(r"git diff( file\.txt)?$", "View the diff of unstaged changes", "Type: git diff"),
            Step(r"git add file\.txt|git add \.", "Stage the modified file", "Type: git add file.txt"),
            Step(r"git diff --staged|git diff --cached", "View the staged diff", "Type: git diff --staged"),
            Step(r'git commit.*-m.*', "Commit the staged change", "Type: git commit -m 'Add line 2'"),
        ],
    ),
    "1.5": Scenario(
        phase=1, topic=5,
        title="Viewing History",
        goal="Create multiple commits and explore the commit history.",
        start_message="Build a small history by making commits, then explore it.",
        setup_commands=[
            "git init",
            "git config user.name Test",
            "git config user.email test@test.com",
        ],
        steps=[
            Step(r"echo.*>?\s*[fF]ile1?", "Create the first file", "Type: echo 'alpha' > file1.txt"),
            Step(r"git add.*", "Stage the first file", "Type: git add file1.txt"),
            Step(r'git commit.*-m.*first|git commit.*-m.*1', "Commit the first file", "Type: git commit -m 'First file'"),
            Step(r"echo.*>?\s*[fF]ile2?", "Create a second file", "Type: echo 'beta' > file2.txt"),
            Step(r"git add.*", "Stage the second file", "Type: git add file2.txt"),
            Step(r'git commit.*-m.*second|git commit.*-m.*2', "Commit the second file", "Type: git commit -m 'Second file'"),
            Step(r"echo.*>?\s*[fF]ile3?", "Create a third file", "Type: echo 'gamma' > file3.txt"),
            Step(r"git add.*", "Stage the third file", "Type: git add file3.txt"),
            Step(r'git commit.*-m.*third|git commit.*-m.*3', "Commit the third file", "Type: git commit -m 'Third file'"),
            Step(r"git log( --oneline)?$", "View the commit history", "Type: git log --oneline"),
            Step(r"git log --oneline --graph", "View history as a graph", "Type: git log --oneline --graph"),
        ],
    ),
    "2.2": Scenario(
        phase=2, topic=2,
        title="Creating and Switching Branches",
        goal="Create a new branch, switch between branches, and see how the working tree changes.",
        start_message="You have a repo with commits on main. Create a branch and work on it.",
        setup_commands=[
            "git init",
            "git config user.name Test",
            "git config user.email test@test.com",
            "echo 'main content' > main.txt",
            "git add main.txt",
            "git commit -m 'Initial on main'",
            "echo 'second commit' > second.txt",
            "git add second.txt",
            "git commit -m 'Second on main'",
        ],
        steps=[
            Step(r"git branch", "List existing branches", "Type: git branch"),
            Step(r"git branch feature", "Create a branch named 'feature'", "Type: git branch feature"),
            Step(r"git branch$", "Verify the new branch exists", "Type: git branch"),
            Step(r"git switch feature|git checkout feature", "Switch to the feature branch", "Type: git switch feature"),
            Step(r"echo.*>?\s*feature\.txt", "Create a file on the feature branch", "Type: echo 'feature work' > feature.txt"),
            Step(r"git add.*", "Stage the new file", "Type: git add feature.txt"),
            Step(r'git commit.*-m.*', "Commit on the feature branch", "Type: git commit -m 'Feature work'"),
            Step(r"git switch main|git checkout main", "Switch back to main", "Type: git switch main"),
            Step(r"git log --oneline --all", "See branches diverging", "Type: git log --oneline --all --graph"),
        ],
    ),
    "2.3": Scenario(
        phase=2, topic=3,
        title="Merging Branches",
        goal="Create divergent branches, then merge one into the other.",
        start_message="Let's practice merging. You'll create branches, make commits on each, and merge them.",
        setup_commands=[
            "git init",
            "git config user.name Test",
            "git config user.email test@test.com",
            "echo 'base' > base.txt",
            "git add base.txt",
            "git commit -m 'Base commit'",
            "git switch -c feature",
            "echo 'feature work' > feature.txt",
            "git add feature.txt",
            "git commit -m 'Feature commit'",
            "git switch main",
            "echo 'main work' > main-work.txt",
            "git add main-work.txt",
            "git commit -m 'Main commit'",
        ],
        steps=[
            Step(r"git branch", "List branches to see feature and main", "Type: git branch"),
            Step(r"git log --oneline --all --graph", "View the divergent history", "Type: git log --oneline --all --graph"),
            Step(r"git merge feature", "Merge feature into main", "Type: git merge feature"),
            Step(r"git log --oneline --graph", "View the merged history", "Type: git log --oneline --graph"),
        ],
    ),
}


def get_scenario(phase: int, topic: int) -> Optional[Scenario]:
    key = f"{phase}.{topic}"
    return SCENARIOS.get(key)


def setup_scenario(sandbox: GitSandbox, scenario: Scenario) -> None:
    _run_setup(sandbox, scenario.setup_commands)


def validate_step(cmd: str, scenario: Scenario, step_index: int) -> tuple[bool, str]:
    if step_index >= len(scenario.steps):
        return False, "All steps complete! Type 'done' to finish."
    step = scenario.steps[step_index]
    if _matches(cmd, step.expected_pattern):
        return True, f"[green]Step {step_index + 1}/{len(scenario.steps)} complete: {step.description}[/]"
    return False, f"[yellow]Hint: {step.hint}[/]"


def verify_scenario_complete(sandbox: GitSandbox, scenario: Scenario, completed_steps: list[int]) -> str:
    pending = [i for i in range(len(scenario.steps)) if i not in completed_steps]
    if not pending:
        return "[bold green]Scenario complete! Great work.[/]"
    return f"Steps remaining: {len(pending)}/{len(scenario.steps)}"
