## Code Review

Code review is the practice of having team members examine each other's code changes before merging. Git provides several tools to facilitate effective code review, from examining diffs to understanding the context and history of code.

### 1. git diff for Review

`git diff` is the primary command for reviewing changes. It shows the differences between two states of the repository.

**Comparing working directory to index:**

```
$ git diff
diff --git a/src/login.go b/src/login.go
index a1b2c3d..e4f5g6h 100644
--- a/src/login.go
+++ b/src/login.go
@@ -10,6 +10,8 @@ func Login(username, password string) error {
        if username == "" {
                return ErrEmptyUsername
        }
+       if len(password) < 8 {
+               return ErrWeakPassword
+       }
        return authenticate(username, password)
 }
```

**Comparing two branches (what a PR contains):**

```
$ git diff main..feature/new-feature
```

**Comparing specific files:**

```
$ git diff main..feature/new-feature -- src/login.go
```

**Showing only filenames that changed (stat):**

```
$ git diff --stat main..feature/new-feature
 src/login.go          | 10 +++++++---
 src/auth.go           |  5 +++++
 tests/login_test.go   | 20 ++++++++++++++++++++
 3 files changed, 32 insertions(+), 3 deletions(-)
```

**Ignore whitespace changes for cleaner review:**

```
$ git diff -w main..feature/new-feature
```

**Show changes in word-diff format instead of line-diff:**

```
$ git diff --word-diff main..feature/new-feature
```

### 2. Reviewing with git log -p

`git log -p` shows the full commit history with patches, which is useful for reviewing a series of commits in a pull request.

**View all commits in a branch with diffs:**

```
$ git log main..feature/new-feature -p
commit a1b2c3d... (feature/new-feature)
Author: Alice <alice@example.com>
Date:   Mon Jan 15 10:00:00 2026 -0500

    Add password strength validation

diff --git a/src/login.go b/src/login.go
index a1b2c3d..e4f5g6h 100644
--- a/src/login.go
+++ b/src/login.go
@@ -10,6 +10,8 @@
+       if len(password) < 8 {
+               return ErrWeakPassword
+       }

commit e4f5g6h... (feature/new-feature)
Author: Alice <alice@example.com>
Date:   Mon Jan 15 11:00:00 2026 -0500

    Add unit tests for password validation

diff --git a/tests/login_test.go b/tests/login_test.go
...
```

**View only the commit messages (no diffs):**

```
$ git log main..feature/new-feature --oneline
a1b2c3d Add password strength validation
e4f5g6h Add unit tests for password validation
i7j8k9l Update documentation
```

**View commits in a specific date range:**

```
$ git log --after="2026-01-01" --before="2026-01-31" --oneline
```

**View commits by a specific author:**

```
$ git log --author="Alice" --oneline
```

### 3. git blame for Context

`git blame` annotates each line of a file with the commit, author, and date that last modified that line. This is invaluable during code review for understanding who wrote what and when.

```
$ git blame src/login.go
a1b2c3d (Alice   2026-01-10) func Login(username, password string) error {
e4f5g6h (Bob     2026-01-12)     if username == "" {
e4f5g6h (Bob     2026-01-12)         return ErrEmptyUsername
e4f5g6h (Bob     2026-01-12)     }
a1b2c3d (Alice   2026-01-10)     return authenticate(username, password)
a1b2c3d (Alice   2026-01-10) }
```

**Blame with specific line ranges:**

```
$ git blame -L 10,20 src/login.go
```

**Ignore whitespace changes in blame:**

```
$ git blame -w src/login.go
```

**Show blame with the original commit's context:**

```
$ git blame -C src/refactored.go
```

The `-C` option detects lines that were moved or copied from other files, which helps track code origins across refactoring.

**Use case during review:** When you see code that looks suspicious, use `git blame` to understand whether it was part of the current PR or pre-existing:

```
$ git blame src/login.go | grep "$(git rev-parse HEAD)"
```

### 4. Commenting on Specific Lines

On GitHub/GitLab, you can comment on specific lines of code in a pull request diff. This is more precise than general comments.

**GitHub:**
1. Open the PR "Files changed" tab
2. Hover over a line and click the blue "+" icon
3. Type your comment
4. Choose "Add single comment" or "Start a review"

You can comment on a range of lines by clicking the "+" icon, dragging to select the range, or Shift-clicking.

**GitLab:**
1. Open the merge request
2. Go to "Changes" tab
3. Hover over a line and click the comment icon
4. Type your comment

**Using GitHub CLI to add a review:**

```
$ gh pr review 123 --comment --body "Looks good, but please fix the typo on line 42"
$ gh pr review 123 --approve --body "LGTM"
$ gh pr review 123 --request-changes --body "Need to fix the error handling"
```

### 5. Review Best Practices

**For the Author:**

- Keep PRs small and focused. A PR should do one thing and do it well.
- Write clear commit messages that explain the "why" not just the "what"
- Self-review your own code before requesting reviews
- Respond to all comments, even if just to acknowledge
- Use the PR description to provide context and reasoning

**For the Reviewer:**

- Be constructive and specific. Instead of "this is wrong," say "this logic fails when the input is empty"
- Focus on the code, not the person. Use "we" instead of "you"
- Separate blocking issues from non-blocking suggestions
- Look for:
  - Correctness (does the code do what it should?)
  - Edge cases (what happens with empty input, errors, concurrency?)
  - Test coverage (are new tests adequate?)
  - Performance (is there a better approach?)
  - Security (are there injection vulnerabilities, auth bypasses?)
  - Style (does it follow project conventions?)

**Checklist for Reviewers:**

```
[ ] Does the code compile/build without errors?
[ ] Are there adequate tests for the changes?
[ ] Do all existing tests still pass?
[ ] Is error handling appropriate?
[ ] Are there any security concerns?
[ ] Is the code readable and maintainable?
[ ] Are there any unnecessary dependencies?
[ ] Is documentation updated?
```

**What to look for in a diff:**

```
$ git diff main..feature | head -20

+// IMPORTANT FIX: This function needs to handle...
```

If you see a comment like the above, ask why the code needs an explanatory comment. Clear, self-documenting code is preferred over complex code with explanations.

### Quiz: Code Review

**Question 1:** During a code review, you want to see who last modified each line of a specific file. Which command should you use?

a) `git log src/file.go`
b) `git blame src/file.go`
c) `git show src/file.go`
d) `git status src/file.go`

**Question 2:** You are reviewing a PR and want to see only the filenames and number of changes without the full diff. Which command is most appropriate?

a) `git diff --name-only main..feature`
b) `git diff --stat main..feature`
c) `git log --oneline main..feature`
d) `git show --stat HEAD`

**Question 3:** What is a best practice for making code review comments more actionable?

a) Only comment on things that are definitely wrong
b) Be specific about the issue and suggest a concrete improvement
c) Leave all comments as general feedback on the PR description
d) Approve the PR first, then leave comments for future improvement

---

**Answers:** 1-b, 2-b, 3-b
