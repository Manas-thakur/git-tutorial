from dataclasses import dataclass
from typing import Optional

from .sandbox import GitSandbox
from .progress import ProgressTracker


@dataclass
class Challenge:
    phase: int
    topic: int
    title: str
    description: str
    setup_script: str
    validation_script: str
    hint: str
    difficulty: str  # easy, medium, hard


CHALLENGES: list[Challenge] = [
    # Phase 1: Getting Started
    Challenge(1, 1, "Create Your First Commit",
        "Initialize a git repo, create a file, stage it, and make your first commit.",
        "git init && git config user.name 'Test' && git config user.email 'test@test.com' && echo 'hello' > file.txt",
        "git log --oneline | wc -l | xargs test 1 -eq",
        "Use 'git add' to stage the file, then 'git commit -m \"message\"'",
        "easy"),
    Challenge(1, 1, "Stage and Unstage",
        "Stage a file, then unstage it before committing. Show that it is back in the working tree.",
        "git init && git config user.name 'Test' && git config user.email 'test@test.com' && echo 'data' > file.txt && git add file.txt",
        "git status --porcelain | grep -q '^??'",
        "Use 'git restore --staged file.txt' or 'git reset HEAD file.txt' to unstage",
        "medium"),
    Challenge(1, 1, "View Commit History",
        "Create multiple commits and use git log to view history in different formats.",
        "git init && git config user.name 'Test' && git config user.email 'test@test.com' && echo 'a' > a.txt && git add a.txt && git commit -m 'Commit A' && echo 'b' > b.txt && git add b.txt && git commit -m 'Commit B'",
        "git log --oneline | wc -l | xargs test 2 -eq",
        "Use 'git log --oneline' for a compact view, 'git log --graph' for branching view",
        "easy"),

    # Phase 2: Branching and Merging
    Challenge(2, 1, "Create and Switch Branches",
        "Create a new branch called 'feature', switch to it, create a file, and commit.",
        "git init && git config user.name 'Test' && git config user.email 'test@test.com' && echo 'init' > readme.md && git add readme.md && git commit -m 'Initial'",
        "git branch --list | grep -q feature",
        "Use 'git branch feature' to create and 'git checkout feature' or 'git switch feature' to switch",
        "easy"),
    Challenge(2, 1, "Merge a Feature Branch",
        "Create a feature branch, make a commit, switch back to main, and merge the feature branch.",
        "git init && git config user.name 'Test' && git config user.email 'test@test.com' && echo 'init' > readme.md && git add readme.md && git commit -m 'Initial' && git checkout -b feature && echo 'feature work' > feature.txt && git add feature.txt && git commit -m 'Feature commit' && git checkout main",
        "git log --oneline --all | wc -l | xargs test 3 -eq",
        "Use 'git merge feature' while on main. The merge will be a fast-forward or create a merge commit",
        "medium"),
    Challenge(2, 1, "Resolve a Merge Conflict",
        "Create conflicting changes on two branches and resolve the conflict.",
        "git init && git config user.name 'Test' && git config user.email 'test@test.com' && echo 'line1' > conflict.txt && git add conflict.txt && git commit -m 'Base' && git checkout -b side && echo 'side change' > conflict.txt && git add conflict.txt && git commit -m 'Side change' && git checkout main && echo 'main change' > conflict.txt && git add conflict.txt && git commit -m 'Main change'",
        "git diff --name-only --diff-filter=M | grep -q conflict",
        "Edit the conflicted file to resolve markers (<<<<<<<, =======, >>>>>>>), then 'git add' and 'git commit'",
        "hard"),

    # Phase 3: Remotes
    Challenge(3, 1, "Add a Remote Repository",
        "Create a bare repository and add it as a remote to another repository.",
        "mkdir /tmp/remote.git && git init --bare /tmp/remote.git && git init && git config user.name 'Test' && git config user.email 'test@test.com' && echo 'repo' > readme.md && git add readme.md && git commit -m 'Initial'",
        "git remote -v | grep -q origin",
        "Use 'git remote add origin /tmp/remote.git' to add the remote",
        "easy"),
    Challenge(3, 1, "Push to Remote",
        "Push local commits to a bare remote repository.",
        "mkdir /tmp/push_remote.git && git init --bare /tmp/push_remote.git && git init && git config user.name 'Test' && git config user.email 'test@test.com' && echo 'data' > file.txt && git add file.txt && git commit -m 'First' && git remote add origin /tmp/push_remote.git",
        "git -C /tmp/push_remote.git log --oneline | wc -l | xargs test 1 -eq",
        "Use 'git push origin main' after adding the remote",
        "medium"),
    Challenge(3, 1, "Fetch and Pull",
        "Push to a bare remote, clone it into another repo, then fetch and pull changes.",
        "mkdir /tmp/fetch_remote.git && git init --bare /tmp/fetch_remote.git && git init repo1 && cd repo1 && git config user.name 'Test' && git config user.email 'test@test.com' && echo 'init' > f.txt && git add f.txt && git commit -m 'Initial' && git remote add origin ../fetch_remote.git && git push origin main && cd .. && git clone /tmp/fetch_remote.git repo2 && cd repo1 && echo 'more' >> f.txt && git add f.txt && git commit -m 'Update' && git push origin main && cd ../repo2",
        "test -f repo2/f.txt && grep -q more repo2/f.txt",
        "Use 'git pull origin main' in repo2 to get the latest changes",
        "medium"),

    # Phase 4: Advanced
    Challenge(4, 1, "Rebase a Feature Branch",
        "Create a feature branch, make a commit on main, then rebase the feature branch onto main.",
        "git init && git config user.name 'Test' && git config user.email 'test@test.com' && echo 'base' > base.txt && git add base.txt && git commit -m 'Base' && git checkout -b feature && echo 'feat' > feat.txt && git add feat.txt && git commit -m 'Feature work' && git checkout main && echo 'main update' >> base.txt && git add base.txt && git commit -m 'Main update' && git checkout feature",
        "git log --oneline main..feature | wc -l | xargs test 1 -eq",
        "Use 'git rebase main' while on the feature branch",
        "hard"),
    Challenge(4, 2, "Cherry-Pick a Commit",
        "Create a commit on one branch and cherry-pick it onto another branch.",
        "git init && git config user.name 'Test' && git config user.email 'test@test.com' && echo 'base' > base.txt && git add base.txt && git commit -m 'Base' && git checkout -b source && echo 'bugfix' > fix.txt && git add fix.txt && git commit -m 'Bug fix commit' && git checkout main",
        "git log --oneline --all | grep -q Bug",
        "Use 'git cherry-pick <commit-hash>' where the hash is from the source branch",
        "medium"),
    Challenge(4, 1, "Interactive Rebase - Squash Commits",
        "Create multiple small commits on a feature branch, then squash them into one using interactive rebase.",
        "git init && git config user.name 'Test' && git config user.email 'test@test.com' && echo 'first' > file.txt && git add file.txt && git commit -m 'First commit' && echo 'second' >> file.txt && git add file.txt && git commit -m 'Second commit' && echo 'third' >> file.txt && git add file.txt && git commit -m 'Third commit'",
        "git log --oneline | wc -l | xargs test 1 -eq",
        "Use 'git rebase -i HEAD~3' and change 'pick' to 'squash' or 's' for the second and third commits",
        "hard"),

    # Phase 5: Collaboration
    Challenge(5, 1, "Recover a Lost Commit with Reflog",
        "Reset HEAD to an older commit, then use reflog to recover the 'lost' commit.",
        "git init && git config user.name 'Test' && git config user.email 'test@test.com' && echo 'v1' > data.txt && git add data.txt && git commit -m 'Version 1' && echo 'v2' >> data.txt && git add data.txt && git commit -m 'Version 2' && echo 'v3' >> data.txt && git add data.txt && git commit -m 'Version 3' && git reset --hard HEAD~1",
        "git log --oneline | wc -l | xargs test 3 -eq",
        "Use 'git reflog' to find the lost commit hash, then 'git cherry-pick <hash>' or 'git reset --hard <hash>'",
        "hard"),
    Challenge(5, 1, "Stash Changes",
        "Make uncommitted changes, stash them, verify clean working tree, then pop the stash.",
        "git init && git config user.name 'Test' && git config user.email 'test@test.com' && echo 'init' > readme.md && git add readme.md && git commit -m 'Initial' && echo 'unstaged work' >> readme.md",
        "git stash list | grep -q stash",
        "Use 'git stash' to save changes, 'git stash pop' to restore them",
        "medium"),
    Challenge(5, 1, "Create and Apply a Patch",
        "Create a diff patch from a commit and apply it to another branch.",
        "git init && git config user.name 'Test' && git config user.email 'test@test.com' && echo 'base' > base.txt && git add base.txt && git commit -m 'Base' && echo 'patch content' > patch.txt && git add patch.txt && git commit -m 'Add patch file' && git checkout -b feature HEAD~1",
        "test -f patch.txt",
        "Use 'git format-patch' or 'git diff' to create a patch, then 'git apply' to apply it",
        "medium"),

    # Phase 6: Internals
    Challenge(6, 1, "View Git Objects",
        "Use git cat-file to inspect the SHA-1 hash and content of a git object.",
        "git init && git config user.name 'Test' && git config user.email 'test@test.com' && echo 'hello git' > hello.txt && git hash-object -w hello.txt",
        "git cat-file -p $(git hash-object hello.txt) | grep -q 'hello git'",
        "Use 'git cat-file -p <hash>' to view content, 'git cat-file -t <hash>' to view type",
        "hard"),
    Challenge(6, 1, "Explore the .git Directory",
        "Examine the structure of the .git directory: list its contents and show the HEAD file.",
        "git init && git config user.name 'Test' && git config user.email 'test@test.com' && echo 'init' > f.txt && git add f.txt && git commit -m 'Init'",
        "test -f .git/HEAD && head -1 .git/HEAD | grep -q ref",
        "Look at .git/HEAD, .git/config, .git/objects/, .git/refs/ to understand the structure",
        "medium"),
    Challenge(6, 1, "Tag a Commit",
        "Create an annotated tag on the current commit and verify it points to the correct commit.",
        "git init && git config user.name 'Test' && git config user.email 'test@test.com' && echo 'release' > release.txt && git add release.txt && git commit -m 'Release 1.0'",
        "git tag -l | grep -q v1.0",
        "Use 'git tag -a v1.0 -m \"message\"' for annotated tags",
        "easy"),
]


def get_challenges(phase: int, topic: int) -> list[Challenge]:
    return [c for c in CHALLENGES if c.phase == phase and c.topic == topic]


def get_next_challenge(progress: ProgressTracker, phase: int, topic: int) -> Optional[Challenge]:
    challenges = get_challenges(phase, topic)
    for i, c in enumerate(challenges):
        if not progress.is_challenge_done(phase, topic, i):
            return c
    return None


def run_challenge_setup(challenge: Challenge, sandbox: GitSandbox) -> bool:
    result = sandbox.run_command(challenge.setup_script)
    return result["success"]


def validate_challenge(challenge: Challenge, sandbox: GitSandbox) -> bool:
    result = sandbox.run_command(challenge.validation_script)
    return result["success"]
