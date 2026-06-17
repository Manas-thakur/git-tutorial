## Merge Conflicts

Merge conflicts happen when Git cannot automatically combine changes from two branches. They are a normal part of collaboration, and every developer encounters them. This chapter explains how to resolve them.

### 1. What Causes Conflicts

A conflict occurs when two branches modify the **same part of the same file** in different ways. Git cannot decide which change to keep.

**Common scenarios:**

- Two developers edit the same line of a file on different branches
- One developer deletes a file while another modifies it
- One developer renames a file while another edits it

**Example:**

Branch `main` has:

```python
def greet():
    print("Hello")
```

On `feature-x`, someone changes `"Hello"` to `"Hi"`.

On `feature-y`, someone changes `"Hello"` to `"Hey"`.

When you merge `feature-x` and then `feature-y` (or vice versa), Git finds both changes to the same line and reports a conflict.

### 2. Conflict Markers

When a conflict occurs, Git modifies the affected file with conflict markers:

```python
def greet():
<<<<<<< HEAD
    print("Hi")
=======
    print("Hey")
>>>>>>> feature-y
```

The markers mean:

| Marker | Meaning |
|--------|---------|
| `<<<<<<< HEAD` | Start of the conflicting section (your current branch) |
| `=======` | Separator between the two conflicting versions |
| `>>>>>>> feature-y` | End of the conflict; shows the incoming branch |

Your job is to edit the file to remove the markers and decide what the final code should look like.

### 3. Resolving Conflicts Manually

**Step-by-step process:**

```
$ git merge feature-y
Auto-merging greet.py
CONFLICT (content): Merge conflict in greet.py
Automatic merge failed; fix conflicts and then commit the result.

$ git status
On branch main
You have unmerged paths.
  (fix conflicts and run "git commit")
  (use "git merge --abort" to abort the merge)

Unmerged paths:
  both modified:   greet.py
```

Open `greet.py` in an editor:

```python
def greet():
<<<<<<< HEAD
    print("Hi")
=======
    print("Hey")
>>>>>>> feature-y
```

Edit to the desired result:

```python
def greet():
    print("Hello World")
```

Save the file, then:

```
$ git add greet.py
$ git commit
```

Git opens an editor with a pre-populated merge commit message. Save and close to complete the merge.

### 4. git mergetool - Visual Conflict Resolution

For complex conflicts, visual merge tools are easier than editing markers by hand.

```
$ git mergetool
```

This opens the configured merge tool. Popular tools include:

| Tool | Command to set up |
|------|------------------|
| Vimdiff | `git config --global merge.tool vimdiff` |
| Meld | `git config --global merge.tool meld` |
| KDiff3 | `git config --global merge.tool kdiff3` |
| VS Code | Built-in; use `code .` and click conflict markers |
| Beyond Compare | `git config --global merge.tool bc3` |

**Using VS Code for conflict resolution:**

VS Code highlights conflicts with color coding and provides clickable options: "Accept Current", "Accept Incoming", "Accept Both", or "Compare Changes".

### 5. Merge Strategies for Conflicts

You can tell Git how to auto-resolve conflicts without manual intervention:

**Ours** (keep the target branch version):

```
$ git merge -X ours feature-branch
```

**Theirs** (keep the incoming branch version):

```
$ git merge -X theirs feature-branch
```

CAUTION: These options resolve conflicts automatically but may lose important changes. Use them only when you are certain one side should always win.

### 6. Aborting a Merge

If a merge is too complex or you want to rethink your approach:

```
$ git merge --abort
```

This undoes the merge and returns your branch to the state before `git merge` was run.

### 7. Practice Scenario

```
# Setup
$ mkdir conflict-practice && cd conflict-practice
$ git init
$ echo "line1\nline2\nline3" > file.txt
$ git add file.txt && git commit -m "Initial"

# Create branch and modify
$ git checkout -b feature-a
$ echo "line1\nline2-modified\nline3" > file.txt
$ git add file.txt && git commit -m "Modify line2 on feature-a"

# Back to main and modify same line differently
$ git checkout main
$ echo "line1\nline2-different\nline3" > file.txt
$ git add file.txt && git commit -m "Modify line2 on main"

# Attempt merge
$ git merge feature-a
Auto-merging file.txt
CONFLICT (content): Merge conflict in file.txt
Automatic merge failed; fix conflicts and then commit the result.

# Resolve
# Edit file.txt to the desired content
$ echo "line1\nline2-resolved\nline3" > file.txt
$ git add file.txt
$ git commit -m "Merge feature-a with resolved conflict"
```

### 8. Preventing Conflicts

- **Communicate**: Tell teammates what files you are working on.
- **Pull frequently**: `git pull` (or `git fetch && git merge`) often to stay current.
- **Small, focused commits**: Small changes are easier to merge than large ones.
- **Short-lived branches**: Merge feature branches frequently rather than letting them diverge for weeks.
- **Rebase before merging**: `git rebase main` on your feature branch can produce a cleaner history with fewer conflicts.

### Quiz: 3 MCQs

**Q1.** What is shown between `<<<<<<< HEAD` and `=======`?

a) The incoming branch's version of the conflicting section
b) The current branch's version of the conflicting section
c) The merge base version
d) The original file content

**Q2.** After resolving a merge conflict, what must you do to complete the merge?

a) Run `git merge --continue`
b) Stage the resolved file with `git add` and then run `git commit`
c) Run `git merge --finish`
d) Run `git rebase --continue`

**Q3.** You start a merge that introduces many conflicts. You decide the merge was a bad idea. What command undoes the merge entirely?

a) `git reset --hard HEAD`
b) `git merge --abort`
c) `git revert HEAD`
d) `git checkout main`
