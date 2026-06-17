## What is Git

**Version control** is a system that records changes to files over time so you can recall specific versions later. It is essential for software development, documentation, and any project where multiple revisions matter.

### 1. What is Version Control?

Version control systems (VCS) manage changes to files, allowing you to:

- Track every modification with a timestamp and author
- Revert files or entire projects to a previous state
- Compare changes across time
- Collaborate with multiple people without stepping on each other's work

Without version control, teams resort to copying files around (e.g., `report-v2-final-really-final.docx`). This approach is error-prone, fragile, and does not scale.

### 2. Centralized vs. Distributed VCS

**Centralized VCS** (e.g., Subversion, CVS, Perforce):

- A single server stores all versioned files.
- Clients check out snapshots from that central server.
- If the server goes down, nobody can collaborate or access history.
- If the database becomes corrupted and backups are outdated, the entire history may be lost.

**Distributed VCS** (e.g., Git, Mercurial):

- Every client fully mirrors the repository, including its full history.
- If the server dies, any client copy can restore it.
- Most operations are local (no network round-trip), making them extremely fast.
- You can commit, branch, and browse history offline.
- Collaboration still uses a remote server, but the server is just a peer, not a single point of failure.

### 3. Git's History and Philosophy

Git was created in 2005 by Linus Torvalds, the creator of Linux. The Linux kernel project needed a VCS after BitKeeper revoked its free license. No existing tool met their needs:

- Speed: patches and commits had to be nearly instantaneous
- Distributed workflow: thousands of developers worldwide
- Data integrity: strong checksums to prevent corruption
- Support for non-linear development: heavy branching and merging

Torvalds designed Git with these design goals:

- **Trust in content**: every object is checksummed with SHA-1. You cannot change a file, date, or message without Git knowing.
- **Mostly local**: most operations need no network, so they are fast.
- **Branching is cheap**: creating a branch is just writing a 41-byte file. This encourages experimental work.
- **The staging area (index)**: a unique Git concept that lets you craft commits in pieces.

### 4. Key Concepts

**Repository (repo)**: A directory that contains your project files and the entire history of changes. It lives inside the `.git` folder.

**Commit**: A snapshot of your project at a point in time. Each commit has a unique SHA-1 hash (e.g., `a1b2c3d...`), an author, a date, a message, and a pointer to its parent commit(s).

**Working tree (working directory)**: The actual files you edit. This is your copy of a specific commit plus any uncommitted changes.

**Staging area (index)**: An intermediate space between the working tree and the repository. You stage changes (with `git add`) to prepare them for the next commit. This allows you to commit only part of your changes.

```
  Working Tree  ---git add--->  Staging Area  ---git commit--->  Repository (.git)
       |                              |                                |
   modified files               selected changes                 permanent snapshot
```

### 5. Git Data Model

Git stores data as a collection of **objects**. There are four types:

**Blob (Binary Large Object)**:

- Stores the content of a file (not the filename).
- Identified by the SHA-1 hash of its content.
- Two files with identical content share the same blob (deduplication).

**Tree**:

- Represents a directory.
- Maps filenames to blobs (or sub-trees).
- Stores file modes (e.g., 100644 for a regular file, 100755 for executable).

**Commit**:

- Points to a tree (the root directory snapshot).
- Contains parent commit hash(es), author, committer, timestamp, and message.
- A commit with no parent is a root commit (first commit in a repo).
- A commit with two parents is a merge commit.

**Tag**:

- A named pointer to a specific commit (usually used for releases).
- Annotated tags store a message and can be signed.

Object storage model:

```
commit  a1b2c3d
  tree  f6e4d2c
  parent b8c9a1f
  author Alice <alice@example.com>
  message: Initial commit

tree  f6e4d2c
  blob 7c4a8d0  README.md
  blob 3b2e1f5  src/main.py
  tree  a9b8c7d  src/

blob  7c4a8d0  -> "# My Project\n"
blob  3b2e1f5  -> "print('hello')\n"
tree  a9b8c7d  -> (empty directory src/utils/)
```

Immutability: once created, an object is never modified. If you change a file, Git creates a new blob with a new hash. Old blobs remain for history. This is why Git never loses data.

### Quiz: 3 MCQs

**Q1.** Which statement about distributed version control is true?

a) All operations require network access to a central server
b) Every client has a full copy of the repository history
c) Branches are only possible on the server
d) Only one developer can work at a time

**Q2.** In Git's data model, what does a tree object represent?

a) A single file's content
b) A commit message
c) A directory and its contents (mapping names to blobs or sub-trees)
d) A branch pointer

**Q3.** What is the purpose of the staging area (index)?

a) To permanently store all project files
b) To act as a cache for remote servers
c) To let you selectively choose which changes to include in the next commit
d) To replace the working directory
