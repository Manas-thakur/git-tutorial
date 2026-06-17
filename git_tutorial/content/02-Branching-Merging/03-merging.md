## Merging

Merging integrates changes from one branch into another. Git's merge algorithm handles everything from simple linear histories to complex combinations of divergent branches.

### 1. git merge - The Basics

`git merge` combines the changes from a source branch into the current branch.

```
$ git checkout main
$ git merge feature-login
```

This takes all commits on `feature-login` that are not on `main` and applies them to `main`.

**Prerequisites:**

- You must be on the branch that will receive the changes (the target).
- There should be no uncommitted changes that conflict with the merge.
- The source branch (e.g., `feature-login`) should contain the work you want to bring in.

### 2. Fast-Forward Merge

A fast-forward merge happens when the target branch has not diverged from the source branch. Git simply moves the branch pointer forward.

```
Before:
      A --- B --- C (main)
                    \
                     D --- E (feature)

After (fast-forward):
      A --- B --- C --- D --- E (main, feature)
```

Git does not create a merge commit. It just advances `main` to where `feature` is.

```
$ git checkout main
$ git merge feature
Updating 1a2b3c4..5d6e7f8
Fast-forward
 login.html | 10 ++++++++++
 1 file changed, 10 insertions(+)
```

### 3. Three-Way Merge

A three-way merge happens when the branches have diverged. Git finds the common ancestor commit (the merge base) and combines the changes from both branches.

```
Before:
      A --- B --- C (main)
       \
        D --- E (feature)

During:
      A --- B --- C (main)
       \         /
        D --- E (feature)

After:
      A --- B --- C --- F (main)
       \         /
        D --- E (feature)
```

Git takes three snapshots:

- **Merge base**: commit A (the common ancestor)
- **Target tip**: commit C (where main is)
- **Source tip**: commit E (where feature is)

Git computes the diff from A to C and from A to E, then combines both sets of changes into commit F.

```
$ git checkout main
$ git merge feature
Merge made by the 'ort' strategy.
 login.html | 5 +++++
 style.css  | 3 +++
 2 files changed, 8 insertions(+)
```

### 4. Merge Commits

A merge commit has **two parents** (or more for octopus merges). You can see them in the log:

```
$ git log --oneline --graph
*   8d4e5f6 (HEAD -> main) Merge feature-login into main
|\
| * 7c8d9e0 (feature-login) Add login validation
| * 6b7c8d9 Create login page
* | 5a6b7c8 Update footer
* | 4c5d6e7 Fix header styles
|/
* 3a4b5c6 Initial commit
```

The first parent (`5a6b7c8`) is where `main` was before the merge. The second parent (`7c8d9e0`) is the tip of `feature-login`.

Viewing a merge commit:

```
$ git show 8d4e5f6
commit 8d4e5f6a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6
Merge: 5a6b7c8 7c8d9e0
Author: Alice Johnson <alice@example.com>
Date:   Tue Jun 17 15:00:00 2026 -0500

    Merge feature-login into main
```

The `Merge:` line shows the two parent hashes.

### 5. git merge --no-ff (No Fast-Forward)

Sometimes you want to force a merge commit even when a fast-forward is possible. This preserves the branch history visually.

```
$ git merge --no-ff feature-login
Merge made by the 'ort' strategy.
```

With `--no-ff`:

```
Before:
      A --- B (main, feature)

After (--no-ff):
      A --- B --- C (main)
                  /
             (feature)
```

Commit C is a merge commit. The branch `feature` is still separate visually. This is useful for:

- Preserving feature branch history
- Making it clear that a feature was merged as a unit
- Allowing easy revert of the entire feature (`git revert -m 1 <merge-commit>`)

The opposite, `git merge --ff-only`, forces Git to only merge if a fast-forward is possible, failing otherwise:

```
$ git merge --ff-only feature
Already up to date.
fatal: Not possible to fast-forward, aborting.
```

### 6. Git Merge Strategies

Git uses different strategies depending on the situation:

| Strategy | When used |
|----------|-----------|
| `ort` (default since Git 2.33) | Recursive three-way merge; handles most cases |
| `recursive` | Older default; replaced by `ort` |
| `resolve` | Simple two-way merge for small repos |
| `ours` | Keeps the target branch version entirely |
| `octopus` | Merging more than two branches |
| `subtree` | Merging a subproject into a subdirectory |

You can specify a strategy:

```
$ git merge -s ours feature-branch
$ git merge -s recursive -X theirs feature-branch   # auto-resolve conflicts in favor of theirs
```

### 7. Aborting a Merge

If a merge has conflicts or you change your mind:

```
$ git merge --abort
```

This returns your repository to the state before the merge started.

### Quiz: 3 MCQs

**Q1.** What condition triggers a fast-forward merge?

a) The source branch has more commits than the target
b) The target branch has not diverged from the source branch; it is an ancestor
c) Both branches have exactly the same number of commits
d) The merge is done with `--no-ff`

**Q2.** How many parents does a typical merge commit have?

a) One
b) Two
c) Three
d) None

**Q3.** When would you use `git merge --no-ff`?

a) When you want to discard the source branch changes
b) When you want to force a merge commit even if a fast-forward is possible, to preserve branch history
c) When you want to merge without creating a commit
d) When you want to skip the merge message prompt
