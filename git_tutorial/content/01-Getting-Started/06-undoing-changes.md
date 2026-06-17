## Undoing Changes

Mistakes happen. Git provides several tools to undo changes at various levels: uncommitted modifications, staged changes, and committed history. The right tool depends on what you want to undo and whether the changes have been shared.

### 1. git restore - Discarding Changes in the Working Tree

If you modified a file but want to discard those changes and revert to the version in the last commit:

```
$ git restore index.html
```

This overwrites `index.html` in the working directory with the version from `HEAD`. The change is irreversible (the modified content is lost).

You can also restore from a specific commit:

```
$ git restore --source=1a2b3c4 index.html
```

### 2. git restore --staged - Unstaging Files

If you staged a file (with `git add`) but decide not to include it in the next commit:

```
$ git add index.html       # oops, staged too early
$ git restore --staged index.html
$ git status
On branch main
Changes not staged for commit:
  modified:   index.html
```

The file is removed from the staging area but its working tree modifications are preserved.

### 3. git reset - Rewinding the Current Branch

`git reset` moves the current branch pointer backward or forward. It operates in three modes.

**--soft**: Moves HEAD to the specified commit. Staging area and working tree are unchanged. All changes since that commit become staged.

```
$ git reset --soft HEAD~1
```

Useful when you want to redo a commit message or combine commits.

**--mixed** (default): Moves HEAD. Resets the staging area to match the specified commit. Working tree is unchanged. Changes become unstaged (modified but not staged).

```
$ git reset HEAD~1
$ git reset --mixed HEAD~1    # same as above
```

**--hard**: Moves HEAD. Resets staging area AND working tree to match the specified commit. All uncommitted changes are lost.

```
$ git reset --hard HEAD~1
HEAD is now at 9b8c7d6 Fix login redirect bug
```

WARNING: `--hard` permanently discards uncommitted changes. There is no recovery from the working tree. However, commits that were made are still in the reflog for a time.

**Resetting to a specific commit:**

```
$ git reset --hard 9b8c7d6
```

**Resetting a specific file** with checkout-style syntax (older Git):

```
$ git reset HEAD index.html     # unstage, equivalent to git restore --staged
```

### 4. git commit --amend - Fixing the Last Commit

If you need to change the most recent commit's message or add forgotten changes:

```
$ git commit -m "Initial commit"
$ echo "missing file" > missing.txt
$ git add missing.txt
$ git commit --amend -m "Initial commit with all files"
```

This creates a new commit that replaces the old one. The old commit is no longer reachable (except via reflog).

WARNING: Never amend commits that have been pushed to a shared branch. It rewrites history and will cause divergent histories for anyone who has pulled the original commit.

### 5. git revert - Safe Undo for Shared History

`git revert` creates a new commit that inverses the changes of a specified commit. Unlike `git reset`, it does not rewrite history, so it is safe to use on public branches.

```
$ git log --oneline
1a2b3c4 Add authentication
9b8c7d6 Fix login bug
f4e3d2c Initial commit

$ git revert 1a2b3c4
Removing src/auth.js
[main 5d6e7f8] Revert "Add authentication"
 1 file changed, 20 deletions(-)
 delete mode 100644 src/auth.js
```

The result:

```
$ git log --oneline
5d6e7f8 (HEAD -> main) Revert "Add authentication"
1a2b3c4 Add authentication
9b8c7d6 Fix login bug
f4e3d2c Initial commit
```

The original commit `1a2b3c4` remains in history (it is not deleted). A new commit `5d6e7f8` undoes its changes.

Reverting a merge commit:

```
$ git revert -m 1 <merge-commit-hash>
```

The `-m 1` tells Git to revert to the first parent (the mainline) when reverting a merge.

### 6. Safety Net: git reflog

The reflog records every movement of HEAD. It is your safety net for recovering "lost" commits.

```
$ git reflog
1a2b3c4 (HEAD -> main) HEAD@{0}: commit: Add authentication
9b8c7d6 HEAD@{1}: reset: moving to HEAD~1
f4e3d2c HEAD@{2}: commit: Fix login bug
a1b2c3d HEAD@{3}: commit: Initial commit
```

If you do `git reset --hard HEAD~1` and realize you lost a commit, you can recover it:

```
$ git reflog
1a2b3c4 HEAD@{0}: reset: moving to HEAD~1
9b8c7d6 HEAD@{1}: commit: IMPORTANT COMMIT I LOST

$ git reset --hard 9b8c7d6
```

The reflog expires entries after 90 days by default (30 for unreachable commits).

### 7. Summary: Which Tool to Use

| Situation | Command | Safe for shared history? |
|-----------|---------|--------------------------|
| Discard unstaged changes in a file | `git restore <file>` | Yes |
| Unstage a file but keep changes | `git restore --staged <file>` | Yes |
| Unstage everything | `git reset` (or `git restore --staged .`) | Yes |
| Change last commit message | `git commit --amend` | No (rewrites history) |
| Undo last commit, keep changes unstaged | `git reset HEAD~1` | No |
| Undo last commit, keep changes staged | `git reset --soft HEAD~1` | No |
| Discard last commit and changes entirely | `git reset --hard HEAD~1` | No |
| Undo a specific commit safely | `git revert <commit>` | Yes |
| Recover a "lost" commit | `git reset --hard <hash>` (from reflog) | N/A |

### Quiz: 3 MCQs

**Q1.** You have committed and pushed a buggy change to a shared branch. Team members have pulled it. What is the safest way to undo it?

a) `git reset --hard HEAD~1 && git push --force`
b) `git commit --amend` to change the commit
c) `git revert <commit-hash>` and push the new revert commit
d) Delete the repository and re-clone

**Q2.** You ran `git add *.js` but want to unstage all JavaScript files before committing. Which command do you use?

a) `git reset --hard`
b) `git restore --staged *.js`
c) `git rm --cached *.js`
d) `git commit --amend`

**Q3.** What is stored in the reflog?

a) Only tags and annotated references
b) A record of every movement of HEAD, including resets and rebases
c) Only commits that were garbage collected
d) The contents of the staging area
