## Fetch vs Pull

Understanding the difference between `git fetch` and `git pull` is crucial for maintaining control over your repository. While `git pull` is convenient, `git fetch` gives you the opportunity to review changes before integrating them.

### 1. git fetch in Detail

`git fetch` downloads commits, files, and references from a remote repository into your local repository. It updates remote-tracking branches but does NOT touch your working tree or current branch.

```
$ git fetch origin
remote: Enumerating objects: 8, done.
remote: Counting objects: 100% (8/8), done.
remote: Compressing objects: 100% (5/5), done.
remote: Total 5 (delta 2), reused 0 (delta 0), pack-reused 0
Unpacking objects: 100% (5/5), 456 bytes | 456.00 KiB/s, done.
From https://github.com/user/repo.git
   1a2b3c4..9b8c7d6  main         -> origin/main
   * [new branch]      experiment  -> origin/experiment
```

After fetch:

- `origin/main` now points to the latest commit from the remote
- Your local `main` branch is unchanged
- Your working tree is unchanged
- You can inspect `origin/main` before merging

```
$ git log --oneline origin/main
9b8c7d6 Update README
1a2b3c4 Initial commit

$ git log --oneline main
1a2b3c4 Initial commit
```

**Fetch all remotes:**

```
$ git fetch --all
Fetching origin
Fetching upstream
```

**Fetch specific branch:**

```
$ git fetch origin feature-login
From https://github.com/user/repo.git
 * branch            feature-login -> FETCH_HEAD
```

### 2. git pull = fetch + merge

`git pull` is a convenience command that runs `git fetch` followed by `git merge` (by default).

```
$ git pull
remote: Enumerating objects: 5, done.
remote: Counting objects: 100% (5/5), done.
remote: Total 3 (delta 1), reused 0 (delta 0), pack-reduced 0
Unpacking objects: 100% (3/3), 345 bytes | 345.00 KiB/s, done.
From https://github.com/user/repo.git
   1a2b3c4..9b8c7d6  main       -> origin/main
Updating 1a2b3c4..9b8c7d6
Fast-forward
 README.md | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

This is equivalent to:

```
$ git fetch origin
$ git merge origin/main
```

`git pull` with remote and branch:

```
$ git pull origin main
```

**What happens internally:**

1. Fetch downloads `origin/main` (updates remote-tracking branch)
2. Merge integrates `origin/main` into your current local branch

### 3. git pull --rebase

Instead of merging, `git pull --rebase` fetches and then rebases your local commits on top of the fetched changes.

```
$ git pull --rebase
From https://github.com/user/repo.git
   1a2b3c4..9b8c7d6  main       -> origin/main
Successfully rebased and updated refs/heads/main.
```

This rewrites your local commits to sit on top of the latest remote commits, resulting in a linear history.

**Before pull --rebase:**

```
Local:   A --- B --- C (main, your commits)
Remote:  A --- D --- E (origin/main, team's commits)
```

**After git pull (merge):**

```
Local:   A --- D --- E --- M (main, merge commit)
                  \       /
                   B --- C
```

**After git pull --rebase:**

```
Local:   A --- D --- E --- B' --- C' (main, linear history)
```

**Configure rebase as the default pull behavior:**

```
$ git config --global pull.rebase true
$ git config --global branch.autoSetupRebase always
```

**When to use --rebase:**

- You want a clean, linear history
- You are working on a feature branch and want to incorporate upstream changes
- You have not yet pushed your commits (or are prepared to force-push)

**When NOT to use --rebase:**

- You have pushed your commits to a shared branch
- You are collaborating on a branch with others

### 4. When to Fetch vs Pull

**Use git fetch when:**

- You want to review what others have changed before integrating
- You want to see if the remote has new branches
- You want to compare your local branch with the remote
- You want to merge at a specific time, not immediately
- You want to merge with a custom strategy (e.g., `--no-ff`)

```
$ git fetch origin
$ git log --oneline main..origin/main    # see what is new
$ git diff main origin/main              # see the actual changes
$ git merge origin/main                  # merge when ready
```

**Use git pull when:**

- You want the fastest way to sync with the remote
- You are confident the merge will be clean
- You are in a hurry and the branch is not complex
- You are working alone or on a branch with little divergence

### 5. Reviewing Before Merging

With fetch, you can inspect changes before integrating:

**See what commits are incoming:**

```
$ git fetch origin
$ git log --oneline main..origin/main
9b8c7d6 Fix login redirect bug
f4e3d2c Update dependencies
```

**See what files changed:**

```
$ git diff --stat main...origin/main
 src/login.js  | 10 ++++++++--
 src/utils.js  |  5 +++++
 2 files changed, 13 insertions(+), 2 deletions(-)
```

**See the full diff:**

```
$ git diff main origin/main
```

Only after reviewing, decide to merge:

```
$ git merge origin/main
```

Or if you do not like what you see:

```
# Do not merge. Revert or discuss with the team.
```

### 6. Dealing with Diverged History

When both your local branch and the remote have diverged, `git pull` creates a merge commit. This is often undesirable.

```
$ git fetch origin
$ git status
On branch main
Your branch and 'origin/main' have diverged,
and have 2 and 3 different commits each, respectively.
```

Options:

1. **Merge** (creates a merge commit):

```
$ git merge origin/main
```

2. **Rebase** (linear history, rewrites your commits):

```
$ git rebase origin/main
```

3. **Reset to remote** (discard your local commits):

```
$ git reset --hard origin/main
```

### 7. Best Practices Summary

| Situation | Use |
|-----------|-----|
| Solo project, single branch | `git pull` |
| Team project, main branch | `git fetch` then review then `git merge` |
| Feature branch, want clean history | `git fetch` then `git rebase origin/main` or `git pull --rebase` |
| Need to see what changed | `git fetch` then `git log`/`git diff` |
| CI/CD or automated scripts | `git fetch --depth 1` (shallow) |

### Quiz: 3 MCQs

**Q1.** What does `git pull` do internally?

a) Only downloads remote data without changing local files
b) Runs `git fetch` followed by `git merge` on the current branch
c) Runs `git fetch` followed by `git rebase` (always)
d) Synchronizes all branches with the remote

**Q2.** After running `git fetch`, where can you find the latest changes from the remote?

a) In your local branch's working tree
b) In the remote-tracking branch (e.g., `origin/main`)
c) In the staging area
d) In the `.git/objects` directory only

**Q3.** You want to see what commits are on `origin/main` that are not on your local `main` before merging. What should you do?

a) `git pull` and check `git log`
b) `git fetch origin` then `git log main..origin/main`
c) `git remote show origin`
d) `git fetch origin` then `git merge origin/main`
