## Interactive Rebase

Interactive rebase is one of Git's most powerful features. It allows you to modify a series of commits before they are reapplied, giving you the ability to squash, reword, reorder, edit, and drop commits. This is essential for maintaining a clean, readable project history.

### 1. git rebase -i (Squash, Reword, Reorder, Edit, Drop)

Interactive rebase is invoked with the `-i` flag:

```
$ git rebase -i HEAD~5
```

This opens an editor showing the last 5 commits in reverse order (oldest first):

```
pick a1b2c3d Add login page
pick e4f5g6h Fix typo in login form
pick i7j8k9l Add validation to login
pick m1n2o3p Fix validation edge case
pick q1r2s3t Add unit tests for login
```

Each line has a command keyword followed by the abbreviated commit hash and the commit message. You can change the command keyword to modify how that commit is handled.

Available commands:

| Command   | Short form | Description                                    |
|-----------|------------|------------------------------------------------|
| pick      | p          | Use the commit as-is                           |
| reword    | r          | Use the commit but edit its message            |
| edit      | e          | Use the commit but stop to amend               |
| squash    | s          | Combine the commit with the previous one       |
| fixup     | f          | Like squash but discard the commit message     |
| exec      | x          | Run a shell command                            |
| break     | b          | Stop here for further operations               |
| drop      | d          | Remove the commit entirely                     |

### 2. Squashing Commits

Squashing combines multiple commits into a single commit. This is useful for cleaning up "work in progress" commits before sharing your work.

To squash several commits, change `pick` to `squash` (or `s`) for all commits except the first one in the series:

```
pick a1b2c3d Add login page
squash e4f5g6h Fix typo in login form
squash i7j8k9l Add validation to login
squash m1n2o3p Fix validation edge case
squash q1r2s3t Add unit tests for login
```

After saving and closing the editor, Git will prompt you to create a combined commit message. It will show all the individual commit messages as a template:

```
# This is a combination of 5 commits.
# This is the 1st commit message:

Add login page

# This is the 2nd commit message:

Fix typo in login form

# This is the 3rd commit message:
...
```

Edit the message to describe the combined changes, save, and exit. The result is a single commit containing all the changes.

Using `fixup` (or `f`) is like squash but discards the commit message of the fixup commit:

```
pick a1b2c3d Add login page
fixup e4f5g6h Fix typo in login form
```

This combines the changes into a single commit with the message "Add login page" and discards "Fix typo in login form".

### 3. Rewording and Reordering Commits

**Rewording** lets you change a commit message without altering the commit's content:

```
pick a1b2c3d Add login page
reword e4f5g6h Fix typo in login form
pick i7j8k9l Add validation
```

Git will stop at the reworded commit and open an editor for you to change the message.

**Reordering** is as simple as moving lines in the editor:

```
pick a1b2c3d Add login page
pick i7j8k9l Add validation            # Moved before the fixup
pick e4f5g6h Fix typo in login form
```

**Dropping** a commit removes it entirely:

```
pick a1b2c3d Add login page
drop e4f5g6h Fix typo in login form   # This commit will not be applied
pick i7j8k9l Add validation
```

**Editing** a commit pauses the rebase so you can make changes:

```
pick a1b2c3d Add login page
edit e4f5g6h Fix typo in login form
pick i7j8k9l Add validation
```

When Git reaches the edit commit, it stops and returns you to the shell. You can then:
1. Make additional changes to files
2. Run `git commit --amend` to modify the commit
3. Run `git rebase --continue` to proceed

### 4. Splitting Commits

Splitting allows you to break one commit into multiple smaller commits. This is useful when a single commit contains unrelated changes.

To split a commit using interactive rebase:

1. Mark the commit you want to split with `edit`:
   ```
   edit a1b2c3d Large commit with unrelated changes
   pick e4f5g6h Next commit
   ```

2. When Git stops at the commit, reset to keep the changes in the working directory:
   ```
   $ git reset HEAD^
   ```

3. Now stage and commit changes in logical groups:
   ```
   $ git add file1
   $ git commit -m "First logical change"
   $ git add file2
   $ git commit -m "Second logical change"
   ```

4. Continue the rebase:
   ```
   $ git rebase --continue
   ```

### 5. Danger and Safety with Reflog

Interactive rebase rewrites commit history, which means it creates new commits and discards old ones. This is dangerous on shared branches because it creates divergent history.

**The Reflog as a Safety Net**: Git's reflog records every change to HEAD, including rebase operations. If you make a mistake during an interactive rebase, you can recover using the reflog.

```
$ git reflog
a1b2c3d HEAD@{0}: rebase -i (finish): returning to refs/heads/feature
e4f5g6h HEAD@{1}: rebase -i (squash): Add login page
i7j8k9l HEAD@{2}: rebase -i (start): checkout HEAD~5
m1n2o3p HEAD@{3}: commit: Add unit tests for login
```

To undo an entire interactive rebase:

```
$ git reset --hard HEAD@{3}
```

This resets your branch to the state it was in before the rebase started.

**Best Practices for Safe Interactive Rebasing:**

- Only rebase local commits that haven't been pushed to a shared branch
- Use `--force-with-lease` instead of `--force` when pushing a rebased branch
- Make a backup branch before starting a complex rebase:
  ```
  $ git branch backup/feature-before-rebase
  $ git rebase -i HEAD~10
  ```
- If something goes wrong, use `git rebase --abort` to cancel before the rebase completes
- After a rebase completes, you can still use reflog to recover lost commits

### Quiz: Interactive Rebase

**Question 1:** Which command combines a commit with the previous one but discards the commit message of the squashed commit?

a) squash
b) fixup
c) merge
d) drop

**Question 2:** You mark a commit with `edit` during an interactive rebase. When Git pauses, what should you do to split this commit into multiple commits?

a) Run `git commit --split` and specify the number of commits
b) Run `git reset HEAD^`, then stage and commit changes in logical groups, then run `git rebase --continue`
c) Use `git rebase --split` to divide the commit automatically
d) Delete the commit from the rebase todo list and recreate it manually

**Question 3:** What is the safest way to recover from a mistake made during an interactive rebase after it has completed?

a) Use `git rebase --undo`
b) Use `git reflog` to find the previous state and `git reset --hard` to return to it
c) Use `git revert` on each commit created by the rebase
d) Delete the local branch and re-clone the repository

---

**Answers:** 1-b, 2-b, 3-b
