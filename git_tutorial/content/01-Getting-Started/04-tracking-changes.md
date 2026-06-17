## Tracking Changes

The core workflow of Git revolves around the three states of files: modified, staged, and committed. Understanding how files move through these states is essential to using Git effectively.

### 1. File Lifecycle in Git

Every file in your working directory falls into one of these states:

```
Untracked  ---- git add ---->  Staged  ---- git commit ---->  Committed
                                   ^                             |
                                   |                             |
Modified  ------ git add ----------+                             |
   ^                                                             |
   +--------------------- git commit -a -------------------------+
```

- **Untracked**: Git does not know about this file. It exists in the working directory but has never been added.
- **Unmodified**: The file is tracked and has not changed since the last commit.
- **Modified**: The file has been changed but not yet staged for commit.
- **Staged**: The modified file has been added to the staging area and will be included in the next commit.

### 2. git status - Checking the State

`git status` shows the current state of your working directory and staging area.

**Long format** (default):

```
$ git status
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   index.html

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        styles.css
```

**Short format** (`-s`):

```
$ git status -s
 M index.html
?? styles.css
```

The short format uses two columns. The first column is the staging area status; the second is the working tree status.

| Symbol | Meaning |
|--------|---------|
| ` `  | Unmodified |
| `M` | Modified |
| `A` | Added (staged) |
| `D` | Deleted |
| `??` | Untracked |
| `R` | Renamed |
| `!!` | Ignored |

Examples:

```
$ git status -s
MM index.html        # Modified in working tree, modified in staging
A  new-file.js       # Staged (new file)
 D deleted-file.js   # Deleted in working tree, not yet staged
R  renamed.js -> old.js   # Renamed
```

### 3. git add - Staging Changes

`git add` tells Git to include a file's current content in the next commit.

Stage a single file:

```
$ git add README.md
```

Stage all changes in the current directory and subdirectories:

```
$ git add .
```

Stage all changes in the entire repository:

```
$ git add -A
```

Stage only modified and deleted files (not new untracked files):

```
$ git add -u
```

**Interactive staging** (`-p` or `--patch`):

This lets you stage parts of a file (hunks) individually:

```
$ git add -p index.html
diff --git a/index.html b/index.html
index 1234567..89abcde 100644
--- a/index.html
+++ b/index.html
@@ -10,7 +10,7 @@
 <h1>Welcome</h1>
-<p>Old paragraph with outdated info.</p>
+<p>New and improved paragraph.</p>
 Stage this hunk [y,n,q,a,d,s,e,?]? y
```

Options: `y` (yes), `n` (no), `s` (split), `e` (edit), `q` (quit).

### 4. git commit - Saving Changes

A commit is a snapshot of the staging area. Each commit has a unique hash, author, timestamp, and message.

**Basic commit with a message**:

```
$ git commit -m "Fix typo in header"
[main 1a2b3c4] Fix typo in header
 1 file changed, 1 insertion(+), 1 deletion(-)
```

**Commit without -m** (opens editor):

```
$ git commit
```

This opens the editor set in `core.editor`. Write a message on the first line (max 50 characters recommended), a blank line, then a detailed body.

**Commit all modified tracked files** (`-a`):

This combines `git add` for all tracked files and `git commit` in one step. Untracked files are not included.

```
$ git commit -a -m "Update multiple files"
```

**Amending the last commit** (`--amend`):

This replaces the most recent commit with a new one. Use it to fix the commit message or add forgotten changes.

```
$ git add forgotten-file.js
$ git commit --amend -m "Better commit message"
```

CAUTION: Never amend commits that have been pushed to a shared branch. It rewrites history and causes problems for collaborators.

### 5. git rm - Removing Files

`git rm` removes a file from both the working directory and the staging area, then stages the removal.

```
$ git rm obsolete.py
rm 'obsolete.py'
$ git commit -m "Remove obsolete script"
```

If you already deleted the file manually, use `git rm` with the `--cached` flag to stage the deletion without touching the working tree (the file is already gone):

```
$ rm obsolete.py
$ git rm obsolete.py
```

Remove a file from tracking but keep it on disk (useful for files that should have been ignored):

```
$ git rm --cached secrets.env
$ echo "secrets.env" >> .gitignore
$ git add .gitignore
$ git commit -m "Stop tracking secrets.env"
```

### 6. git mv - Moving and Renaming Files

`git mv` moves or renames a file and stages the change.

```
$ git mv old-name.js new-name.js
$ git status
On branch main
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        renamed:    old-name.js -> new-name.js

$ git commit -m "Rename old-name.js to new-name.js"
```

This is equivalent to:

```
$ mv old-name.js new-name.js
$ git rm old-name.js
$ git add new-name.js
```

### 7. Full Workflow Example

```
# Start a new project
$ mkdir my-app && cd my-app
$ git init
$ git config user.email "dev@example.com"
$ git config user.name "Dev"

# Create and commit a file
$ echo "console.log('hello')" > main.js
$ git status
$ git add main.js
$ git commit -m "Initial commit"

# Make changes
$ echo "console.log('world')" >> main.js
$ git status -s
$ git add -p main.js     # stage only some hunks
$ git status -s
$ git commit -m "Add world log"
```

### Quiz: 3 MCQs

**Q1.** You modified `app.js` and then ran `git add app.js`. After that, you modified `app.js` again without staging. What does `git status -s` show for `app.js`?

a) ` M` (modified in working tree, not staged)
b) `M ` (modified in staging area, not in working tree)
c) `MM` (modified in both staging area and working tree)
d) `A ` (staged as new)

**Q2.** What does `git commit -a -m "Fix bugs"` do?

a) Commits only staged changes
b) Automatically stages all tracked files that have been modified or deleted and then commits them
c) Stages all untracked files and commits them
d) Creates a new branch before committing

**Q3.** You accidentally committed a sensitive file `passwords.json` and want to stop tracking it but keep it on disk. Which commands should you use?

a) `git rm passwords.json && git commit`
b) `git rm --cached passwords.json && echo "passwords.json" >> .gitignore && git add .gitignore && git commit`
c) `git reset --soft HEAD~1`
d) `git restore --staged passwords.json`
