## Stashing

Stashing temporarily saves uncommitted changes so you can work on something else, then reapply them later. It is useful when you need to switch branches, pull updates, or start a different task without committing half-finished work.

### 1. When to Use Stash

Stash is ideal for these situations:

- You are working on a feature but need to switch branches to fix a critical bug
- You want to pull updates from remote but have uncommitted changes
- You want to test a different approach without losing current work
- You need to clean your working tree temporarily to run a build or test

**Not a substitute for commits**: Stashes are local and easy to lose. Use commits for work you want to keep long-term.

### 2. git stash push (save) - Creating a Stash

The basic command:

```
$ git stash
Saved working directory and index state WIP on main: 1a2b3c4 Add authentication
```

This stashes both staged and unstaged changes (but not untracked files by default).

**Include untracked files:**

```
$ git stash --include-untracked
$ git stash -u                # short form
```

**Include all files (including ignored):**

```
$ git stash --all
```

**Stash with a descriptive message:**

```
$ git stash push -m "WIP: login form validation"
Saved working directory and index state On main: WIP: login form validation
```

**Stash specific files:**

```
$ git stash push -m "only styles" src/styles.css src/components/
```

### 3. git stash list - Viewing Stashes

```
$ git stash list
stash@{0}: On main: WIP: login form validation
stash@{1}: On main: WIP: header styles
stash@{2}: On main: WIP: experimental
```

Each stash is identified by `stash@{n}` where `n` is the index (0 = most recent).

```
$ git stash list --oneline
1a2b3c4 refs/stash@{0}: On main: WIP: login form validation
```

### 4. git stash show - Inspecting a Stash

See a summary of changes in the most recent stash:

```
$ git stash show
 src/login.js | 10 +++++++++-
 1 file changed, 9 insertions(+), 1 deletion(-)
```

See the full diff:

```
$ git stash show -p
```

Inspect a specific stash:

```
$ git stash show stash@{2}
$ git stash show -p stash@{1}
```

### 5. git stash pop - Applying and Removing

`git stash pop` applies the most recent stash and removes it from the stash list:

```
$ git stash pop
On branch main
Changes not staged for commit:
  modified:   src/login.js

no changes added to commit
Dropped refs/stash@{0} (1a2b3c4...)
```

Pop a specific stash:

```
$ git stash pop stash@{1}
```

### 6. git stash apply - Applying Without Removing

`git stash apply` is like `pop` but does NOT remove the stash from the list:

```
$ git stash apply
On branch main
Changes not staged for commit:
  modified:   src/login.js

no changes added to commit

$ git stash list
stash@{0}: On main: WIP: login form validation
```

Use `apply` when you want to keep the stash for later or apply it to multiple branches.

### 7. git stash drop - Removing a Stash

Remove a stash without applying it:

```
$ git stash drop stash@{0}
Dropped refs/stash@{0} (1a2b3c4...)
```

Drop the most recent stash:

```
$ git stash drop
```

### 8. git stash clear - Removing All Stashes

Remove every stash:

```
$ git stash clear
```

WARNING: This is irreversible. There is no way to recover cleared stashes.

### 9. Stashing Untracked Files

By default, `git stash` does not stash untracked files. To include them:

```
$ git stash -u
```

Verify what was stashed:

```
$ git status
On branch main
nothing to commit, working tree clean

$ git stash show
 src/login.js     | 10 ++++++++++
 new-file.js      |  5 +++++
 2 files changed, 15 insertions(+)
```

### 10. Creating a Branch from a Stash

If conflicts occur when popping or applying a stash, create a branch:

```
$ git stash branch fix-feature stash@{0}
Switched to a new branch 'fix-feature'
On branch fix-feature
Changes not staged:
  modified:   src/login.js

no changes added to commit
Dropped refs/stash@{0} (1a2b3c4...)
```

This creates a new branch from the commit where the stash was originally made, applies the stash, and drops it. This is the safest way to recover from stash conflicts.

### 11. Full Workflow Example

```
# Start working on a feature
$ echo "function login() {}" > auth.js
$ git add auth.js

# Bug report! Need to switch to main
$ git stash push -m "WIP: auth feature"

# Verify clean state
$ git status
On branch main
nothing to commit, working tree clean

# Fix the bug
$ git checkout main
$ echo "bugfix" > fix.js
$ git add fix.js && git commit -m "Critical bugfix"

# Go back to feature branch
$ git checkout feature-auth

# Apply the stash
$ git stash pop
Auto-merging auth.js
On branch feature-auth
Changes to be committed:
  new file:   auth.js

$ git commit -m "Add auth module"
```

### Quiz: 3 MCQs

**Q1.** What is the difference between `git stash pop` and `git stash apply`?

a) `pop` applies the stash and removes it from the list; `apply` applies it but keeps the stash
b) `pop` only applies the most recent stash; `apply` can apply any stash
c) `pop` works with untracked files; `apply` does not
d) There is no difference

**Q2.** You have both tracked and untracked changes. You run `git stash` (without options). What happens to the untracked files?

a) They are stashed along with tracked files
b) They remain in the working directory, unstashed
c) They are deleted
d) They are automatically committed

**Q3.** After applying a stash with `git stash apply`, you realize you want to keep that stash for another branch. What should you do?

a) Nothing; `apply` already keeps the stash
b) Run `git stash save` again to re-stash it
c) Run `git stash pop` instead
d) Recreate the changes manually
