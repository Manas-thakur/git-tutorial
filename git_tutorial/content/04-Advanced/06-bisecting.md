## Bisecting

`git bisect` is a powerful debugging tool that uses binary search to find the exact commit that introduced a bug. Instead of manually checking each commit in a range, bisect systematically narrows down the search space.

### 1. git bisect (Binary Search for Bugs)

The principle behind `git bisect` is simple: given a range of commits where one end is "good" (the bug does not exist) and the other end is "bad" (the bug exists), Git performs a binary search to find the first commit that introduced the bug.

```
Good commit (no bug)  --->  Bad commit (bug present)

Known good: commit A
Known bad:  commit Z

Git checks out the middle commit M:
- If M is good, the bug is between M and Z
- If M is bad, the bug is between A and M
```

With this approach, each test halves the remaining search space. With 1000 commits, bisect finds the buggy commit in about 10 steps (2^10 = 1024).

### 2. git bisect start / bad / good

The basic bisect workflow involves three main steps: starting the bisect, marking the bad commit, and marking the good commit.

**Step 1: Start the bisect session**

```
$ git bisect start
```

You can specify the range directly:

```
$ git bisect start HEAD v1.0
```

This starts bisecting between HEAD (bad) and v1.0 (good).

**Step 2: Mark the current commit as bad**

```
$ git bisect bad
```

Or specify a specific commit as bad:

```
$ git bisect bad HEAD
```

**Step 3: Mark a known good commit**

```
$ git bisect good v2.0
```

Or specify a tag or commit hash:

```
$ git bisect good a1b2c3d
```

After marking good and bad, Git checks out the midpoint commit:

```
$ git bisect start
$ git bisect bad
$ git bisect good v1.0
Bisecting: 7 revisions left to test after this (roughly 3 steps)
[4a5b6c7d] Refactor login handler
```

**Step 4: Test the current commit**

At each step, you test whether the bug exists on the checked-out commit:

```
$ git bisect good
# or
$ git bisect bad
```

Continue until Git identifies the first bad commit:

```
4a5b6c7d is the first bad commit
commit 4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3
Author: Alice <alice@example.com>
Date:   Mon Jan 10 14:30:00 2026 -0500

    Refactor login handler

 login.go | 10 +++++-----
 1 file changed, 5 insertions(+), 5 deletions(-)
```

**Step 5: End the bisect session**

```
$ git bisect reset
```

This returns your working directory to the state it was in before starting the bisect.

### 3. Automating with git bisect run

For bugs that can be detected automatically (e.g., a failing test), you can use `git bisect run` with a script. Git will automatically test each commit by running the script, which should exit with code 0 for "good" and non-zero for "bad".

```
$ git bisect start HEAD v1.0
$ git bisect run npm test
```

The script can be any executable. Common patterns:

```
$ git bisect run make test
$ git bisect run python -m pytest
$ git bisect run ./test-bug.sh
```

If the script returns 125, Git skips that commit (useful for commits that cannot be tested):

```
#!/bin/bash
if [ ! -f "test.sh" ]; then
    exit 125  # Skip commits without tests
fi
./test.sh
```

Creating a custom bisect script:

```
$ cat > bisect-test.sh << 'EOF'
#!/bin/bash
npm install --silent 2>/dev/null
npm run test:integration 2>/dev/null
EOF
$ chmod +x bisect-test.sh
$ git bisect run ./bisect-test.sh
```

Git prints the progress as it goes:

```
$ git bisect run npm test
running npm test
# ... test output ...
Bisecting: 15 revisions left to test after this (roughly 4 steps)
running npm test
# ... test output ...
Bisecting: 7 revisions left to test after this (roughly 3 steps)
...
4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3 is the first bad commit
bisect run success
```

### 4. git bisect visualize

During a bisect session, you can visualize the remaining commits using `git bisect visualize`. This opens `git log` with only the commits in the bisect range.

```
$ git bisect visualize
```

This shows a log of commits that are still being searched. You can pass options to customize the view:

```
$ git bisect visualize --oneline --decorate
```

Or view the bisect range as a graph:

```
$ git bisect visualize --graph --oneline
```

You can also view all commits marked as good or bad:

```
$ git log --oneline --bisect
```

This shows only the commits in the bisect range, with `bisect/bad` and `bisect/good` markers.

### 5. Skip and Log Commands

Sometimes a commit cannot be tested (e.g., it doesn't compile). Use `git bisect skip` to skip it:

```
$ git bisect skip
```

You can skip specific commits:

```
$ git bisect skip a1b2c3d e4f5g6h
```

If there are many unskippable commits, `git bisect` can still find the bug by using the remaining commits.

View the current bisect log:

```
$ git bisect log
```

This outputs the log of all bisect operations, which can be replayed:

```
$ git bisect log > bisect-log.txt
$ git bisect reset
$ git bisect replay bisect-log.txt
```

Replaying a log is useful for repeating the same bisect or sharing the exact steps with another developer.

Get a summary of the bisect state:

```
$ git bisect visualize
$ git bisect log
```

### 6. Practical Bisect Workflow Example

```
$ git log --oneline
a1b2c3d (HEAD) Add error handling
e4f5g6h Refactor database layer
i7j8k9l Add caching
m1n2o3p Fix typo in config
q1r2s3t Initial working version

$ git bisect start
$ git bisect bad HEAD       # Current commit is bad
$ git bisect good q1r2s3t   # Initial version was good

Bisecting: 2 revisions left to test after this (roughly 1 step)
[i7j8k9l] Add caching

# Test: does the bug exist here?
# After testing, mark:
$ git bisect bad

Bisecting: 0 revisions left to test after this (roughly 0 steps)
[e4f5g6h] Refactor database layer

# Test again:
$ git bisect good

e4f5g6h is the first bad commit
commit e4f5g6h7i8j9k0l1m2n3o4p5q6r7s8t9u0v1w
Refactor database layer

$ git bisect reset
```

### Quiz: Bisecting

**Question 1:** What is the minimum number of test steps needed to find a buggy commit using `git bisect` in a range of 100 commits?

a) Exactly 100 steps
b) At most 7 steps (binary search reduces 2^7 = 128)
c) Exactly 50 steps (half the range)
d) The number of steps depends on where the bug is in the history

**Question 2:** What exit code should your bisect script return to tell Git to skip the current commit?

a) 0
b) 1
c) 125
d) 255

**Question 3:** After completing a `git bisect` session, what command should you run to return to your normal working state?

a) `git bisect end`
b) `git bisect stop`
c) `git bisect reset`
d) `git bisect finish`

---

**Answers:** 1-b, 2-c, 3-c
