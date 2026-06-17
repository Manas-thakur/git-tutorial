## Plumbing and Porcelain

Git's command set is divided into two categories: porcelain and plumbing. Porcelain commands are the user-friendly commands you use daily. Plumbing commands are the low-level building blocks that the porcelain commands call internally.

### 1. Plumbing Commands vs Porcelain Commands

The terms come from the analogy of a kitchen: the porcelain is the attractive surface you interact with, while the plumbing is the pipes and mechanisms that make things work behind the walls.

**Porcelain commands** are designed for everyday use. They have intuitive names and behavior.

| Porcelain   | What it does                        |
|-------------|-------------------------------------|
| git add     | Stage changes for commit            |
| git commit  | Record changes to the repository    |
| git status  | Show the state of the working tree  |
| git diff    | Show differences                     |
| git log     | Show commit history                  |
| git branch  | List, create, or delete branches     |
| git checkout| Switch branches or restore files    |
| git merge   | Join two or more development histories |

**Plumbing commands** are low-level commands that expose Git's internal operations. They are rarely used directly but are essential for scripting and understanding Git internals.

| Plumbing          | What it does                                |
|-------------------|---------------------------------------------|
| git hash-object   | Compute object ID and optionally create blob|
| git cat-file      | Display content or metadata of an object    |
| git write-tree    | Create a tree object from the current index |
| git read-tree     | Read tree into the index                    |
| git commit-tree   | Create a new commit object                  |
| git update-ref    | Update a reference safely                   |
| git rev-parse     | Parse revision specifications               |
| git ls-files      | Show information about files in the index   |
| git ls-tree       | List the contents of a tree object          |
| git mktree        | Build a tree object from ls-tree formatted text|

### 2. Key Plumbing Commands

**git hash-object:**
Computes the SHA-1 hash of a file and optionally stores it as a blob object.

```
$ echo "Hello, Git!" | git hash-object --stdin -w
a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0
```

**git cat-file:**
Displays information about a Git object.

```
$ git cat-file -p a1b2c3d4
Hello, Git!

$ git cat-file -t a1b2c3d4
blob
```

**git write-tree:**
Creates a tree object from the current state of the index and returns its hash.

```
$ git write-tree
4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b
```

**git read-tree:**
Reads a tree object into the index. This replaces the current index contents.

```
$ git read-tree --prefix=new-dir/ 4a5b6c7d
```

**git commit-tree:**
Creates a commit object from a tree object and optional parent(s).

```
$ echo "Initial commit" | git commit-tree 4a5b6c7d
e4f5g6h7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3
```

**git update-ref:**
Updates a reference (branch, tag, HEAD) to point to a new object.

```
$ git update-ref refs/heads/my-branch e4f5g6h7
```

**git rev-parse:**
Parses revision specifications and resolves them to hashes.

```
$ git rev-parse HEAD
a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0

$ git rev-parse --abbrev-ref HEAD
main

$ git rev-parse HEAD~3
1111111111111111111111111111111111111111

$ git rev-parse main..feature
2222222222222222222222222222222222222222
```

### 3. Building a Commit from Scratch with Plumbing

Let's create a commit using only plumbing commands. This demonstrates exactly what `git add` and `git commit` do internally.

**Step 1: Create a blob object from a file**

```
$ echo "Hello from plumbing" > hello.txt
$ git hash-object -w hello.txt
a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0

$ git cat-file -p a1b2c3d4
Hello from plumbing
```

**Step 2: Create a tree object**

We need to tell Git that hello.txt should be in the tree with specific permissions.

```
$ git update-index --add --cacheinfo 100644 \
  a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0 hello.txt

$ git write-tree
b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2

$ git cat-file -p b2c3d4e5
100644 blob a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0 hello.txt
```

Alternatively, use `git mktree` to create the tree directly:

```
$ echo "100644 blob a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0 hello.txt" | git mktree
b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2
```

**Step 3: Create a commit object**

```
$ echo "First commit using plumbing" | git commit-tree b2c3d4e5
c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3

$ git cat-file -p c3d4e5f6
tree b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2
author Alice <alice@example.com> 1705320000 -0500
committer Alice <alice@example.com> 1705320000 -0500

First commit using plumbing
```

**Step 4: Update HEAD to point to the new commit**

```
$ git update-ref refs/heads/main c3d4e5f6
# OR, if creating a new branch:
$ git update-ref refs/heads/my-branch c3d4e5f6
$ git symbolic-ref HEAD refs/heads/my-branch
```

**Step 5: Verify our work**

```
$ git log
commit c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3
Author: Alice <alice@example.com>
Date:   Wed Jan 15 10:00:00 2025 -0500

    First commit using plumbing

$ git status
nothing to commit, working tree clean
```

**Step 6: Add a second commit with plumbing**

```
$ echo "Second version" > hello.txt
$ git hash-object -w hello.txt
d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4

$ git update-index --add --cacheinfo 100644 \
  d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4 hello.txt

$ git write-tree
e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5

$ echo "Second commit using plumbing" | git commit-tree \
  e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5 \
  -p c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3

f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6

$ git update-ref refs/heads/main f6a7b8c9

$ git log --oneline
f6a7b8c9 Second commit using plumbing
c3d4e5f6 First commit using plumbing
```

### 4. Understanding Git's Internal Architecture

The plumbing/porcelain distinction reveals Git's layered architecture:

```
User Interface (Porcelain)
        |
git add, git commit, git log, git branch, git checkout
        |
Internal Operations (Plumbing)
        |
hash-object, cat-file, write-tree, read-tree,
commit-tree, update-ref, rev-parse
        |
Object Database
        |
.git/objects/ (blobs, trees, commits, tags)
        |
Reference Database
        |
.git/refs/ (branches, tags, HEAD)
```

**Porcelain is built on plumbing:**

```
$ git add hello.txt
  Internally calls:
  1. git hash-object -w hello.txt  (creates blob)
  2. git update-index --add hello.txt (updates index)

$ git commit -m "Message"
  Internally calls:
  1. git write-tree  (creates tree from index)
  2. git commit-tree (creates commit from tree)
  3. git update-ref  (updates branch reference)
```

**Other useful plumbing commands:**

`git symbolic-ref`: Reads or sets symbolic references (like HEAD).
```
$ git symbolic-ref HEAD
refs/heads/main
```

`git merge-base`: Finds the common ancestor of two commits.
```
$ git merge-base main feature
a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0
```

`git rev-list`: Lists commit objects in reverse chronological order.
```
$ git rev-list --count HEAD
42
```

`git check-ignore`: Checks if a file is ignored by .gitignore.
```
$ git check-ignore node_modules
node_modules
```

`git count-objects`: Counts loose objects and disk usage.
```
$ git count-objects -v
```

**The .git directory structure (full):**

```
.git/
  HEAD            # Points to current branch reference
  config          # Repository configuration
  description     # Repository description
  index           # Staging area (binary file)
  ORIG_HEAD       # Previous HEAD before dangerous operation
  objects/        # Object database
    aa/bbb...     # Loose objects (first 2 hex chars = directory)
    pack/         # Packed objects and indexes
  refs/
    heads/        # Local branch references
      main
      feature
    tags/         # Tag references
      v1.0
    remotes/      # Remote tracking branches
      origin/
        main
        feature
  logs/           # Reflogs
    HEAD
    refs/heads/main
    refs/remotes/origin/main
  hooks/          # Client-side hook scripts
    pre-commit
    commit-msg
    ...
  info/           # Additional info
    exclude       # Local-only .gitignore patterns
  packed-refs     # Packed references (for performance)
```

### Quiz: Plumbing and Porcelain

**Question 1:** Which of the following is a plumbing command rather than a porcelain command?

a) git commit
b) git log
c) git hash-object
d) git merge

**Question 2:** What does `git write-tree` do?

a) Writes the current commit to a file
b) Creates a tree object from the current state of the index and returns its hash
c) Writes the commit message template to a file
d) Creates a branch reference

**Question 3:** When you run `git commit`, which sequence of plumbing commands does it internally execute?

a) `git hash-object` -> `git write-tree` -> `git commit-tree` -> `git update-ref`
b) `git write-tree` -> `git commit-tree` -> `git update-ref`
c) `git create-commit` -> `git update-branch`
d) `git hash-object` -> `git read-tree` -> `git symbolic-ref`

---

**Answers:** 1-c, 2-b, 3-b
