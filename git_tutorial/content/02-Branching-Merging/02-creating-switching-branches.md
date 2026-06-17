## Creating and Switching Branches

Git makes branch creation and switching fast and simple. This chapter covers the commands to create, list, rename, delete, and switch between branches.

### 1. git branch - Listing Branches

List all local branches. The current branch is marked with an asterisk:

```
$ git branch
* main
  feature-login
  bugfix-header
```

List remote-tracking branches:

```
$ git branch -r
  origin/main
  origin/feature-login
```

List all branches (local + remote):

```
$ git branch -a
* main
  feature-login
  bugfix-header
  remotes/origin/main
  remotes/origin/feature-login
```

Verbose listing (shows the latest commit on each branch):

```
$ git branch -v
* main           5d6e7f8 Add feature
  feature-login  7c8d9e0 Add login validation
  bugfix-header  3a4b5c6 Fix header alignment
```

### 2. git branch - Creating Branches

Create a new branch at the current commit:

```
$ git branch feature-search
```

This creates a new pointer called `feature-search` at the same commit as HEAD. You are still on `main`.

Create a branch at a specific commit:

```
$ git branch feature-search 1a2b3c4
```

Create a branch at a specific tag:

```
$ git branch hotfix v1.0.0
```

### 3. git checkout - Switching Branches (Legacy)

`git checkout` is the traditional command for switching branches:

```
$ git checkout feature-search
Switched to branch 'feature-search'

$ git log --oneline
1a2b3c4 (HEAD -> feature-search, main) Add authentication
```

`git checkout` does two things:

1. Moves HEAD to point to `feature-search`
2. Updates the working tree to match the commit that `feature-search` points to

If you have uncommitted changes, Git checks if they conflict with the target branch. If they do not, Git carries them along. If they do, Git refuses to switch and tells you to commit or stash.

**Create and switch in one command:**

```
$ git checkout -b new-branch
Switched to a new branch 'new-branch'
```

This is equivalent to:

```
$ git branch new-branch
$ git checkout new-branch
```

### 4. git switch - Modern Branch Switching

Git 2.23+ introduced `git switch` as a cleaner alternative to `git checkout` for branch operations.

**Switch to an existing branch:**

```
$ git switch feature-search
Switched to branch 'feature-search'
```

**Create and switch:**

```
$ git switch -c new-branch
Switched to a new branch 'new-branch'
```

**Return to the previous branch:**

```
$ git switch -
Switched to branch 'main'
```

This is a handy shortcut equivalent to `git checkout @{-1}`.

**Differences between switch and checkout:**

- `git switch` only does branch switching (no file restoration).
- `git checkout` has dual purposes: switching branches AND restoring files.
- `git switch` is safer because it reduces the chance of accidental detached HEAD.

### 5. Moving Between Branches

When you switch branches, Git does the following:

1. Updates HEAD to point to the target branch
2. Updates the index (staging area) to match the target branch's commit
3. Updates the working tree files to match the target branch

**Rules for switching with uncommitted changes:**

| Working tree state | Can switch? | Behavior |
|-------------------|-------------|----------|
| No changes | Yes | Clean switch |
| Unstaged modifications that do not conflict | Yes | Changes carried over |
| Unstaged modifications that conflict | No | Git refuses; stash or commit first |
| Staged changes that do not conflict | Yes | Staged changes carried over |
| Staged changes that conflict | No | Git refuses |

**Example of a conflict:**

```
$ git switch feature-search
error: Your local changes to the following files would be overwritten by checkout:
        index.html
Please commit your changes or stash them before you switch branches.
Aborting
```

### 6. Renaming Branches

Rename the current branch:

```
$ git branch -m new-name
```

Rename any branch:

```
$ git branch -m old-name new-name
```

If the new name already exists, Git will refuse. Force rename with `-M`:

```
$ git branch -M old-name new-name
```

### 7. Deleting Branches

Delete a fully merged branch:

```
$ git branch -d feature-login
Deleted branch feature-login (was 7c8d9e0).
```

Git will refuse to delete a branch that contains unmerged commits (to prevent data loss):

```
$ git branch -d feature-experiment
error: The branch 'feature-experiment' is not fully merged.
If you are sure you want to delete it, run 'git branch -D feature-experiment'.
```

Force delete (discards commits):

```
$ git branch -D feature-experiment
Deleted branch feature-experiment (was 9b8c7d6).
```

Delete a remote branch:

```
$ git push origin --delete feature-login
$ git branch -d feature-login   # also delete local copy
```

### 8. Practical Workflow

```
# Start from main
$ git checkout main

# Create a feature branch and switch to it
$ git checkout -b user-profile-page

# Make changes
$ echo "<h1>Profile</h1>" > profile.html
$ git add profile.html
$ git commit -m "Add profile page HTML"

# Switch back to main to start another task
$ git checkout main
$ git checkout -b fix-nav-styling

# List all branches
$ git branch -v

# Delete the feature branch after merging
$ git checkout main
$ git merge user-profile-page
$ git branch -d user-profile-page
```

### Quiz: 3 MCQs

**Q1.** What is the difference between `git branch feature-x` and `git checkout -b feature-x`?

a) `git branch` creates the branch and switches to it; `git checkout -b` only creates it
b) `git branch` only creates the branch; `git checkout -b` creates and switches to it
c) They are identical
d) `git branch` creates the branch from origin/main; `git checkout -b` creates from current commit

**Q2.** You are on `main` with uncommitted changes that conflict with `feature-x`. What happens when you run `git switch feature-x`?

a) Git auto-merges the conflicts
b) The switch succeeds and overwrites your changes
c) Git refuses to switch and shows an error
d) Git stashes your changes automatically

**Q3.** What does `git switch -` do?

a) Creates a new branch with a hyphen in the name
b) Switches to the previous branch you were on
c) Deletes the current branch
d) Shows a diff of all branches
