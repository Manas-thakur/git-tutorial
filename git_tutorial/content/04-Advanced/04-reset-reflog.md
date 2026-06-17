## Reset and Reflog

Git's reset command and reflog mechanism are essential tools for undoing changes and recovering lost work. Understanding them deeply is critical for advanced Git usage.

### 1. git reset --soft / --mixed / --hard

The `git reset` command moves the HEAD and branch pointer to a specified commit, with three modes controlling what happens to the index (staging area) and working directory.

```
$ git reset [--soft | --mixed | --hard] [<commit>]
```

**--soft**: Moves HEAD to the specified commit but leaves the index and working directory unchanged. All changes from the commits between the old HEAD and the target commit become "staged" (in the index).

```
$ git reset --soft HEAD~1
# HEAD moves back one commit
# Changes from that commit are now staged
# Working directory is untouched
```

Use case: Undoing a commit while keeping the changes staged and ready for a new commit.

```
$ git commit -m "WIP: incomplete feature"
$ git reset --soft HEAD~1
# Now you can make more changes or rewrite the commit
```

**--mixed** (default): Moves HEAD to the specified commit and resets the index to match, but leaves the working directory untouched. Changes become "unstaged" in the working directory.

```
$ git reset --mixed HEAD~1
# HEAD moves back one commit
# Index is reset to match the target commit
# Changes are now unstaged but still in working directory
$ git status
# Shows modified files as unstaged
```

Use case: Unstaging a commit to re-commit it in smaller, logical pieces.

```
$ git reset HEAD~1
# Changes are now unstaged modified files
$ git add file1
$ git commit -m "Part 1"
$ git add file2
$ git commit -m "Part 2"
```

**--hard**: Moves HEAD, resets the index, and discards all changes in the working directory. This is destructive -- files will match exactly the target commit.

```
$ git reset --hard HEAD~1
# HEAD moves back one commit
# Index and working directory are reset
# All uncommitted changes are LOST
```

Use case: Discarding all local changes and resetting to a known good state.

```
$ git reset --hard origin/main
# Reset local branch to match remote exactly
```

### 2. ORIG_HEAD

Before certain dangerous operations (merge, rebase, reset), Git saves the original HEAD position as a special reference called `ORIG_HEAD`. This provides a simple way to undo those operations.

```
$ git reset --hard HEAD~3
$ git reset --hard ORIG_HEAD    # Undo the reset
```

After a merge, you can undo it with:

```
$ git merge some-feature
# Merge conflicts or unwanted merge
$ git reset --hard ORIG_HEAD    # Back to before the merge
```

`ORIG_HEAD` is overwritten each time Git performs a potentially destructive operation. Only the most recent operation is saved. For older references, use the reflog.

### 3. git reflog (Recovery Tool)

The reflog (reference log) records every change to the HEAD pointer, including commits, checkouts, resets, merges, rebases, and cherry-picks. It is your primary safety net for recovering lost work.

```
$ git reflog
a1b2c3d HEAD@{0}: reset: moving to HEAD~3
e4f5g6h HEAD@{1}: commit: Add feature X
i7j8k9l HEAD@{2}: commit: Fix bug in login
m1n2o3p HEAD@{3}: commit: Add login page
q1r2s3t HEAD@{4}: checkout: moving from main to feature
```

Each entry shows:
- The commit hash at that point
- The reflog selector (HEAD@{n})
- The operation performed
- Details about the operation

To recover a lost commit, check the reflog and reset to it:

```
$ git reflog
a1b2c3d HEAD@{0}: reset: moving to HEAD~3
e4f5g6h HEAD@{1}: commit: IMPORTANT WORK
# Oops, HEAD@{1} was the important work before the reset

$ git reset --hard HEAD@{1}
# Now you're back to where you were
```

You can view the reflog for a specific branch:

```
$ git reflog feature-branch
```

The reflog has a default expiration of 90 days for reachable commits and 30 days for unreachable commits.

### 4. git reflog expire

Git automatically expires reflog entries based on age. You can manually expire entries with:

```
$ git reflog expire --expire=30.days --all
```

This removes all reflog entries older than 30 days for all references.

To expire specific references:

```
$ git reflog expire --expire=now --ref=refs/heads/feature
```

Use `git reflog delete` to remove specific entries:

```
$ git reflog delete HEAD@{5}
```

Warning: Expiring the reflog removes your safety net. Only do this when you are certain you no longer need the history.

### 5. Recovering Lost Commits

There are several scenarios where commits become "lost" and can be recovered using reflog.

**Recovering from a bad reset:**

```
$ git reset --hard HEAD~5   # Lost 5 commits
$ git reflog
# Find the commit before the reset
$ git reset --hard HEAD@{1}  # Recover
```

**Recovering from a rebase gone wrong:**

```
$ git rebase --abort  # During a rebase
# Or after rebase completed:
$ git reflog
# Find the entry before "rebase (start)"
$ git reset --hard HEAD@{rebase-start-index}
```

**Recovering dropped commits from interactive rebase:**

```
$ git rebase -i HEAD~10
# Dropped a commit accidentally
$ git reflog
a1b2c3d HEAD@{3}: rebase -i (finish): returning to refs/heads/feature
e4f5g6h HEAD@{4}: commit: The commit I dropped
$ git cherry-pick e4f5g6h  # Recover the dropped commit
```

**Recovering after deleting a branch:**

```
$ git branch -D old-feature  # Deleted a branch
$ git reflog
# Find the last commit that was on that branch
$ git branch recovered-branch <commit-hash>
```

You can also use `git fsck` to find dangling commits that are not referenced by any branch or tag but still exist in the object database:

```
$ git fsck --lost-found
Checking object directories: 100% (256/256), done.
dangling commit a1b2c3d...
dangling blob e4f5g6h...

$ git show a1b2c3d  # Inspect the dangling commit
$ git branch recovered-branch a1b2c3d  # Recover it
```

### Quiz: Reset and Reflog

**Question 1:** You run `git reset --hard HEAD~2` and realize you accidentally lost two important commits. What is the safest way to recover?

a) The commits are permanently lost and cannot be recovered
b) Use `git reset --soft HEAD@{1}` to undo the reset
c) Run `git reflog` to find the commit hash before the reset, then use `git reset --hard <hash>`
d) Run `git checkout HEAD~2` to get the files back

**Question 2:** Which `git reset` mode leaves the working directory unchanged but unstages all changes?

a) `--soft`
b) `--mixed`
c) `--hard`
d) `--keep`

**Question 3:** What is `ORIG_HEAD` in Git?

a) A reference to the initial commit in the repository
b) A reference to the previous HEAD before a dangerous operation like merge or reset
c) A backup of the HEAD created every hour
d) The same as `HEAD~1`

---

**Answers:** 1-c, 2-b, 3-b
