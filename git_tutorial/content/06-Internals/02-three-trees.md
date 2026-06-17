## The Three Trees

Git manages three distinct tree-like structures that represent the state of your repository at different levels: HEAD, the Index (staging area), and the Working Directory. Understanding how these three trees interact is fundamental to mastering Git.

### 1. The Three Trees: HEAD, Index, Working Directory

**HEAD** is a reference to the current commit (or branch, which points to a commit). It represents the last committed state of the repository.

- HEAD is the tip of the current branch
- It points to a commit object, which points to a tree object
- It represents the state of the project at the last commit

**The Index** (also called the staging area or cache) is a binary file (`.git/index`) that stores a snapshot of what will go into the next commit.

- It tracks file names, their metadata, and the blob hash of staged changes
- It is the intermediate state between the working directory and HEAD
- It is what `git add` modifies

**The Working Directory** (also called the working tree) is the actual files on your filesystem that you edit.

- It is a checkout of the current commit plus any local modifications
- It is what you edit with your text editor or IDE

```
Three trees visualized:

HEAD (last commit)     Index (staging area)    Working Directory
     |                       |                       |
     v                       v                       v
  commit                   .git/index             files on disk
     |
     v
   tree
     |
     v
  blob(s)
```

### 2. How add/commit/reset Affect the Trees

Each Git command modifies the three trees in specific ways.

**git add: Working Directory -> Index**

```
$ git add file.txt

Before:
HEAD: file.txt v1
Index: file.txt v1
Working: file.txt v2 (modified)

After:
HEAD: file.txt v1
Index: file.txt v2 (staged)
Working: file.txt v2 (modified)
```

`git add` copies the file from the working directory into the index, creating or updating the blob object.

**git commit: Index -> HEAD**

```
$ git commit -m "Update file"

Before:
HEAD: file.txt v1
Index: file.txt v2
Working: file.txt v2

After:
HEAD: file.txt v2 (committed)
Index: file.txt v2
Working: file.txt v2
```

`git commit` creates a new commit using the current index, then updates HEAD to point to this new commit.

**git reset HEAD: HEAD -> Index (with --mixed, the default)**

```
$ git reset HEAD file.txt

Before:
HEAD: file.txt v2
Index: file.txt v1 (older version)
Working: file.txt v2

After:
HEAD: file.txt v2
Index: file.txt v2 (copied from HEAD)
Working: file.txt v2
```

**git reset --soft: Only moves HEAD back**

```
$ git reset --soft HEAD~1

Before:
HEAD: commit C
Index: matches commit C
Working: matches commit C

After:
HEAD: commit B (moved back)
Index: still matches commit C (staged!)
Working: matches commit C
```

Changes from commit C become "staged" for a new commit.

**git reset --hard: HEAD, Index, Working all change**

```
$ git reset --hard HEAD~1

Before:
HEAD: commit C
Index: matches commit C
Working: matches commit C

After:
HEAD: commit B
Index: matches commit B
Working: matches commit B
```

All three trees now match commit B. Changes from commit C are discarded.

**Full state diagram for common commands:**

```
              Working            Index              HEAD
              Directory
                                   
git add              ----->                           
git commit                      ----->               
git reset (--mixed)         <-----                   
git reset (--soft)                          <-----   
git reset (--hard)  <-----  <-----          <-----   
git checkout HEAD   <-----  <-----                  
git checkout <file> <-----                            
git rm                      <-----                   
```

### 3. git ls-files, git ls-tree

These plumbing commands inspect the index and tree objects.

**git ls-files: Inspect the Index**

`git ls-files` lists files tracked in the index.

```
$ git ls-files
README.md
src/main.go
src/utils.go
tests/main_test.go

$ git ls-files --stage
100644 a1b2c3d4... 0 README.md
100644 e4f5g6h7... 0 src/main.go
100644 i7j8k9l0... 0 src/utils.go
100755 m1n2o3p4... 0 tests/main_test.go
```

The `--stage` output shows: mode, blob hash, stage number (0 for normal, 1-3 for merge conflicts), and filename.

**git ls-tree: Inspect a Tree Object**

`git ls-tree` lists the contents of a tree object (typically from a commit).

```
$ git ls-tree HEAD
100644 blob a1b2c3d4... README.md
100755 blob e4f5g6h7... script.sh
040000 tree i7j8k9l0... src/

$ git ls-tree -r HEAD
100644 blob a1b2c3d4... README.md
100755 blob e4f5g6h7... script.sh
100644 blob m1n2o3p4... src/main.go
100644 blob q1r2s3t4... src/utils.go
```

The `-r` flag recurses into subtrees.

**Comparing index and HEAD:**

```
$ git diff --cached --name-only
```

This shows files that differ between HEAD and the index (staged changes).

```
$ git ls-files --stage > index-files
$ git ls-tree -r HEAD > head-files
$ diff index-files head-files
```

### 4. Tree Walk Example

Let's trace what happens internally during a typical workflow.

**Step 1: Initial state**

```
$ git log --oneline
a1b2c3d Initial commit

$ git ls-tree -r HEAD
100644 blob 1111111... README.md
100644 blob 2222222... src/main.go

$ git ls-files --stage
100644 1111111... README.md
100644 2222222... src/main.go
```

All three trees are in sync.

**Step 2: Edit a file**

```
$ echo "print('Hello')" >> src/main.go

$ git ls-files --stage
100644 1111111... README.md
100644 2222222... src/main.go   # Index unchanged

$ git status
Changes not staged for commit:
  modified: src/main.go
```

Working directory differs from Index.

**Step 3: Stage the change**

```
$ git add src/main.go

$ git ls-files --stage
100644 1111111... README.md
100644 3333333... src/main.go   # New blob hash!
```

A new blob object was created for the modified file. The Index now points to the new blob.

**Step 4: Commit**

```
$ git commit -m "Add print statement"

$ git ls-tree -r HEAD
100644 blob 1111111... README.md
100644 blob 3333333... src/main.go   # HEAD now matches Index

$ git ls-files --stage
100644 1111111... README.md
100644 3333333... src/main.go
```

All three trees are back in sync. A new commit and tree object were created.

**Step 5: View the underlying objects**

```
$ git rev-parse HEAD
a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0

$ git cat-file -p HEAD
tree b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0
parent 1111111111111111111111111111111111111111
author Alice <alice@example.com> 1705320000 -0500
committer Alice <alice@example.com> 1705320000 -0500

Add print statement

$ git cat-file -p b1c2d3e4f5
100644 blob 1111111111111111111111111111111111111111 README.md
100644 blob 3333333333333333333333333333333333333333 src/main.go
```

**Visual representation of the object graph:**

```
Commit (HEAD)
  |
  +-- Tree (root)
  |     |
  |     +-- blob 1111111... README.md
  |     +-- blob 3333333... src/main.go
  |
  +-- parent -> previous commit (initial commit)
```

### 5. Three Trees and Merge Conflicts

When a merge conflict occurs, the Index temporarily holds three versions of the conflicted file (stages 1, 2, and 3).

```
$ git ls-files --stage
100644 1111111... 0 README.md
100644 aaaaaaa... 1 src/main.go  # stage 1: merge base
100644 bbbbbbb... 2 src/main.go  # stage 2: HEAD version
100644 ccccccc... 3 src/main.go  # stage 3: MERGE_HEAD version
```

After resolving the conflict and running `git add`, the staged version replaces all three stages:

```
$ git add src/main.go
$ git ls-files --stage
100644 1111111... 0 README.md
100644 ddddddd... 0 src/main.go  # resolved version at stage 0
```

### Quiz: Three Trees

**Question 1:** What does `git add` do to the three trees?

a) Moves changes from HEAD to the Index
b) Copies the file from the Working Directory into the Index, updating or creating a blob object
c) Commits changes directly from the Working Directory to HEAD
d) Deletes the file from the Index

**Question 2:** You run `git reset --soft HEAD~1`. What happens to the Index and Working Directory?

a) Both the Index and Working Directory are reset to match HEAD~1
b) The Index is reset but the Working Directory is unchanged
c) HEAD moves back, but the Index and Working Directory are unchanged, leaving the last commit's changes staged
d) Nothing changes; the command has no effect

**Question 3:** During a merge conflict, what do stages 1, 2, and 3 in the Index represent?

a) The three most recent commits on the current branch
b) The merge base (1), the HEAD version (2), and the MERGE_HEAD version (3)
c) The three files that are in conflict
d) The good, bad, and skipped states from git bisect

---

**Answers:** 1-b, 2-c, 3-b
