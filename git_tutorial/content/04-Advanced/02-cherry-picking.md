## Cherry-Picking

Cherry-picking is a Git feature that allows you to apply specific commits from one branch onto another branch. Unlike merging or rebasing, which bring over a range of commits, cherry-picking gives you fine-grained control over exactly which commits to apply.

### 1. git cherry-pick (Apply Specific Commits)

The `git cherry-pick` command takes one or more existing commits and applies their changes as new commits on the current branch.

```
$ git cherry-pick <commit-hash>
```

When you run this command, Git computes the diff introduced by the specified commit and applies it to the current branch, creating a new commit with a new hash but preserving the original commit message and author information.

```
Before cherry-pick:
A---B---C (feature)
 \
  D---E---F (main)

$ git checkout main
$ git cherry-pick C

After cherry-pick:
A---B---C (feature)
 \
  D---E---F---C' (main)
```

Commit C' contains the same changes as commit C but is a completely new commit object with a different parent (F instead of B).

Cherry-picking is useful when:
- You need a specific bug fix from a release branch on main
- A developer committed to the wrong branch and you need the change elsewhere
- You want to selectively apply features from one branch to another

### 2. Cherry-Pick Ranges

You can cherry-pick a range of commits using the `A..B` syntax, where A is exclusive and B is inclusive:

```
$ git cherry-pick A..B
```

This applies all commits from A (exclusive) to B (inclusive) onto the current branch.

```
$ git cherry-pick main~5..main~2
```

This picks the 3 commits starting from main~5 (exclusive) through main~2 (inclusive).

You can also cherry-pick multiple individual commits by specifying them as separate arguments:

```
$ git cherry-pick a1b2c3d e4f5g6h i7j8k9l
```

The commits are applied in the order they are listed. If you encounter conflicts during a range cherry-pick, you resolve them per-commit, just like a rebase.

### 3. Cherry-Pick Conflicts

Cherry-picking can cause conflicts, especially when the context around the changes differs between branches. When a conflict occurs, Git pauses the cherry-pick and marks the conflicted files.

```
$ git cherry-pick a1b2c3d
error: could not apply a1b2c3d... Fix login bug
hint: after resolving the conflicts, mark them with
hint: "git add <file>" and run "git cherry-pick --continue"
hint: or run "git cherry-pick --abort" to cancel
```

Options for handling cherry-pick conflicts:

- **Resolve manually**: Edit the conflicted files, stage them, then continue
  ```
  $ git add <file>
  $ git cherry-pick --continue
  ```

- **Skip the commit**: Do not apply this particular commit
  ```
  $ git cherry-pick --skip
  ```

- **Abort the entire operation**: Return to the original state before cherry-pick started
  ```
  $ git cherry-pick --abort
  ```

The `--signoff` option adds a Signed-off-by line to the cherry-picked commit, which is useful for tracking provenance:

```
$ git cherry-pick --signoff a1b2c3d
```

The `-x` option appends a note indicating which commit was cherry-picked:

```
$ git cherry-pick -x a1b2c3d
```

This adds a line like `(cherry picked from commit a1b2c3d...)` to the commit message.

### 4. Use Cases (Hotfixes, Backporting)

**Hotfixes** are the most common use case for cherry-picking. When a critical bug is found in production, you fix it on main but need to apply the same fix to a release branch without bringing in unrelated changes.

```
$ git checkout release/v2.0
$ git cherry-pick -x a1b2c3d   # Apply the hotfix commit
$ git push origin release/v2.0
```

**Backporting** involves applying a fix or feature from a newer version to an older supported version. For example, if a security patch is developed for version 3.0, you may need to apply it to version 2.0 as well.

```
$ git checkout release/v2.0
$ git cherry-pick -x f6e5d4c   # Security patch from v3.0
```

**Moving commits between branches** when someone commits to the wrong branch:

```
$ git checkout correct-branch
$ git cherry-pick wrong-branch-commit
$ git checkout wrong-branch
$ git reset --hard HEAD~1   # Remove the mistaken commit
```

**Selective feature adoption** allows teams working on different release cycles to pick specific features without waiting for a full merge:

```
$ git checkout stable
$ git cherry-pick feature-commit-1 feature-commit-3
# Only picks specific features, skipping feature-commit-2 which was not ready
```

### Quiz: Cherry-Picking

**Question 1:** When you cherry-pick commit X from branch A onto branch B, what happens?

a) Commit X is moved from branch A to branch B
b) A new commit with the same changes as X is created on branch B, and X remains on branch A
c) The changes from X are applied to branch A's working directory but not committed
d) Git creates a merge commit between branch A and branch B

**Question 2:** You are cherry-picking a range of commits and encounter a conflict on the third commit. What happens?

a) Git automatically skips the third commit and continues with the rest
b) Git aborts the entire cherry-pick operation immediately
c) Git pauses, allowing you to resolve the conflict and continue, skip, or abort
d) Git applies the conflict markers into the files and commits them anyway

**Question 3:** Which option appends a note to the commit message indicating the source commit when cherry-picking?

a) `--signoff`
b) `--note`
c) `-x`
d) `--reference`

---

**Answers:** 1-b, 2-c, 3-c
