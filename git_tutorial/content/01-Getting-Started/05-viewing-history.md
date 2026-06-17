## Viewing History

Git's history is a directed acyclic graph (DAG) of commits. Learning to navigate this history is critical for understanding what happened, when, and why.

### 1. git log - Viewing Commit History

`git log` displays the commit history in reverse chronological order (most recent first).

**Default format:**

```
$ git log
commit 1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0 (HEAD -> main)
Author: Alice Johnson <alice@example.com>
Date:   Tue Jun 17 14:30:00 2026 -0500

    Add user authentication module

commit 9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c
Author: Bob Smith <bob@example.com>
Date:   Mon Jun 16 09:15:00 2026 -0500

    Fix login redirect bug
```

**One-line format** (`--oneline`):

```
$ git log --oneline
1a2b3c4 (HEAD -> main) Add user authentication module
9b8c7d6 Fix login redirect bug
f4e3d2c Update README with setup instructions
a1b2c3d Initial commit
```

**Graph format** (`--graph`):

```
$ git log --oneline --graph --all
*   8d4e5f6 (HEAD -> main) Merge feature-branch into main
|\
| * 7c8d9e0 (feature-branch) Add search feature
| * 6b7c8d9 Implement search index
* | 5a6b7c8 Fix nav bar styling
* | 4c5d6e7 Update dependencies
|/
* 3a4b5c6 Initial commit
```

**Decorate format** (`--decorate`) -- shows branch and tag pointers:

```
$ git log --oneline --decorate
1a2b3c4 (HEAD -> main, tag: v1.0) Release v1.0
9b8c7d6 (origin/main, origin/HEAD) Fix login redirect bug
f4e3d2c Update README
a1b2c3d Initial commit
```

**Useful git log options:**

| Option | Effect |
|--------|--------|
| `--oneline` | One commit per line with abbreviated hash |
| `--graph` | ASCII graph showing branch structure |
| `--all` | Show all branches, not just the current one |
| `--decorate` | Show branch and tag names |
| `--stat` | Show which files changed and how many insertions/deletions |
| `-p` | Show the full diff (patch) for each commit |
| `--author="Alice"` | Filter by author |
| `--since="2 weeks ago"` | Filter by date |
| `--grep="bug"` | Search commit messages for "bug" |
| `-n 5` | Limit to 5 commits |
| `--format=format:"%h - %an: %s"` | Custom format |

**Custom format example:**

```
$ git log --format="%h | %an | %s | %ar"
1a2b3c4 | Alice Johnson | Add user authentication | 2 hours ago
9b8c7d6 | Bob Smith | Fix login redirect bug | 1 day ago
```

Format placeholders: `%h` (hash), `%an` (author name), `%ae` (author email), `%s` (subject), `%ar` (relative date), `%d` (ref names).

### 2. git show - Viewing a Specific Commit

`git show` displays the details of a single commit: the changes (diff), metadata, and message.

```
$ git show 1a2b3c4
commit 1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0 (HEAD -> main)
Author: Alice Johnson <alice@example.com>
Date:   Tue Jun 17 14:30:00 2026 -0500

    Add user authentication module

diff --git a/src/auth.js b/src/auth.js
new file mode 100644
index 0000000..abc1234
--- /dev/null
+++ b/src/auth.js
@@ -0,0 +1,20 @@
+function login(username, password) {
+    // authenticate user
+}
```

Show the version of a file at a specific commit:

```
$ git show 1a2b3c4:README.md
# My Project

This is the README at the time of commit 1a2b3c4.
```

### 3. git diff - Comparing Changes

`git diff` shows differences between various states of the repository.

**Working tree vs staging area** (unstaged changes):

```
$ git diff
diff --git a/index.html b/index.html
index abc1234..def5678 100644
--- a/index.html
+++ b/index.html
@@ -10,6 +10,7 @@
 <h1>Welcome</h1>
+<p>New paragraph added but not staged.</p>
 <p>Existing content.</p>
```

**Staging area vs last commit** (staged changes ready to be committed):

```
$ git diff --cached
$ git diff --staged      # equivalent
```

**Working tree vs last commit** (all changes since last commit):

```
$ git diff HEAD
```

**Between two commits:**

```
$ git diff 1a2b3c4 9b8c7d6
```

**Between two branches:**

```
$ git diff main feature-branch
$ git diff main..feature-branch    # same as above
$ git diff main...feature-branch   # changes on feature-branch since it diverged from main
```

**Comparing a file across two commits:**

```
$ git diff 1a2b3c4 9b8c7d6 -- README.md
```

### 4. git blame - Who Changed What

`git blame` annotates each line of a file with the commit hash, author, and date that last modified it.

```
$ git blame app.js
1a2b3c4d (Alice Johnson 2026-06-17 14:30:00 -0500 1) const express = require('express');
9b8c7d6e (Bob Smith     2026-06-16 09:15:00 -0500 2) const auth = require('./auth');
1a2b3c4d (Alice Johnson 2026-06-17 14:30:00 -0500 3) 
f4e3d2c1 (Alice Johnson 2026-06-15 11:00:00 -0500 4) const app = express();
9b8c7d6e (Bob Smith     2026-06-16 09:15:00 -0500 5) app.use(auth.middleware);
```

Useful options:

```
$ git blame -L 10,30 app.js        # only lines 10-30
$ git blame -w app.js              # ignore whitespace changes
$ git blame -C app.js              # detect moved/copied lines
```

### Quiz: 3 MCQs

**Q1.** You want to see a compact ASCII graph of all branches in the repository. Which command do you use?

a) `git log --oneline --all`
b) `git log --oneline --graph --all --decorate`
c) `git graph`
d) `git show --graph`

**Q2.** What does `git diff` (with no arguments) compare?

a) The staging area against the last commit
b) The working tree against the staging area (unstaged changes)
c) The working tree against the last commit
d) The current branch against `origin/main`

**Q3.** You see a bug in `app.js` at line 42 and need to find which commit last modified that line. What command do you use?

a) `git log app.js`
b) `git blame -L 42,42 app.js`
c) `git show app.js`
d) `git diff HEAD app.js`

**Answers**: 1-b, 2-b, 3-b
