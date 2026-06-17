## Viewing Differences

Comparing different versions of files and branches is a fundamental Git skill. `git diff` and its related tools let you see exactly what changed between any two points in your repository.

### 1. git diff - Comparing the Working Tree and Staging Area

Without arguments, `git diff` shows unstaged changes -- modifications in the working tree that have not been added to the staging area.

```
$ git diff
diff --git a/index.html b/index.html
index abc1234..def5678 100644
--- a/index.html
+++ b/index.html
@@ -10,6 +10,7 @@
 <h1>Welcome</h1>
+<p>This paragraph is new and not yet staged.</p>
 <p>Existing paragraph.</p>
```

The diff format shows:

- `--- a/index.html` -- the original version (in the staging area or HEAD)
- `+++ b/index.html` -- the new version (in the working tree)
- `@@ -10,6 +10,7 @@` -- hunk header: old file starts at line 10, shows 6 lines; new file starts at line 10, shows 7 lines
- Lines starting with `+` are additions
- Lines starting with `-` are deletions
- Lines starting with space are context

### 2. git diff --cached (--staged) - Comparing Staging Area and Last Commit

Shows changes that have been staged and will be included in the next commit:

```
$ git diff --cached
$ git diff --staged         # equivalent
```

```
$ git add index.html
$ git diff --cached
diff --git a/index.html b/index.html
index abc1234..def5678 100644
--- a/index.html
+++ b/index.html
@@ -10,6 +10,7 @@
 <h1>Welcome</h1>
+<p>This paragraph is staged and ready to commit.</p>
 <p>Existing paragraph.</p>
```

### 3. git diff HEAD - All Changes Since Last Commit

Shows both staged and unstaged changes combined:

```
$ git diff HEAD
```

This is equivalent to `git diff --cached` plus `git diff`.

### 4. Comparing Specific Files

Limit the diff to specific files:

```
$ git diff -- index.html
$ git diff --cached -- index.html style.css
$ git diff HEAD -- src/
```

The `--` separates file paths from other arguments.

### 5. Comparing Two Commits

```
$ git diff 1a2b3c4 9b8c7d6
$ git diff 1a2b3c4..9b8c7d6       # same as above
```

Shows changes between two specific commits.

Show what changed in a file between two commits:

```
$ git diff 1a2b3c4 9b8c7d6 -- README.md
```

### 6. Comparing Branches

```
$ git diff main feature-login
```

This shows the diff from `main` to `feature-login` -- changes that would be applied if you merged `feature-login` into `main`.

**Three-dot syntax** (changes on `feature-login` that are not on `main`):

```
$ git diff main...feature-login
```

This shows only the changes that `feature-login` introduced since it diverged from `main`. This is usually what you want when reviewing a feature branch.

Compare what is different between two branches for a specific directory:

```
$ git diff main...feature-login -- src/components/
```

### 7. git difftool - Visual Diffing

For complex diffs, a visual tool is easier to work with:

```
$ git difftool
```

This opens the configured diff tool. Configuration:

```
$ git config --global diff.tool meld
$ git config --global difftool.prompt false
```

Popular diff tools:

| Tool | Config value |
|------|-------------|
| Meld | `meld` |
| KDiff3 | `kdiff3` |
| VS Code | `code --diff` |
| Vimdiff | `vimdiff` |

Use difftool with the same arguments as diff:

```
$ git difftool main...feature-login
$ git difftool --cached
$ git difftool HEAD~3 HEAD~1 -- src/
```

### 8. Useful git diff Options

| Option | Effect |
|--------|--------|
| `--stat` | Show summary of changes (files changed, insertions, deletions) |
| `--name-only` | Show only file names that changed |
| `--name-status` | Show file names and status (M, A, D, R) |
| `--ignore-space-change` | Ignore whitespace changes |
| `--ignore-all-space` | Ignore all whitespace |
| `--word-diff` | Show word-level diff (not line-level) |
| `--color-words` | Highlight changed words inline |
| `-w` | Short for `--ignore-all-space` |

**Examples:**

```
$ git diff --stat
 index.html | 3 ++-
 1 file changed, 2 insertions(+), 1 deletion(-)

$ git diff --name-only
index.html
src/login.js

$ git diff --word-diff
diff --git a/README.md b/README.md
index abc1234..def5678 100644
--- a/README.md
+++ b/README.md
@@ -1,4 +1,4 @@
Welcome to [-the-]{+our+} project. This is a {+fantastic+} tool.
```

### 9. Comparing Date Ranges

Show changes between dates:

```
$ git diff --since="2 weeks ago" --until="yesterday"
```

This compares the state of the repository at two points in time.

### 10. Diff Shortcuts for Branch Comparisons

```
# What is different between the current branch and main
$ git diff main HEAD

# What did my feature branch introduce (three-dot)
$ git diff main...my-feature

# Compare a specific file across branches
$ git diff main feature -- package.json
```

### Quiz: 3 MCQs

**Q1.** You have staged changes (with `git add`) and also have unstaged modifications. What does `git diff` (with no arguments) show?

a) Both staged and unstaged changes
b) Only the staged changes
c) Only the unstaged changes (working tree vs staging area)
d) Nothing; it errors

**Q2.** You want to see only the changes that `feature-branch` introduced since it diverged from `main`. Which command do you use?

a) `git diff main feature-branch`
b) `git diff main..feature-branch`
c) `git diff main...feature-branch`
d) `git diff feature-branch main`

**Q3.** What does `git diff --cached` compare?

a) The working tree against the staging area
b) The staging area against the last commit
c) Two arbitrary commits
d) The current branch against origin/main
