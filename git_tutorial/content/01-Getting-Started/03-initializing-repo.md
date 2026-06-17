## Initializing a Repository

Every Git project starts with a repository. You can either create a new one from scratch or clone an existing one. This chapter walks through both approaches and explains the internal structure of the `.git` directory.

### 1. git init - Creating a New Repository

The `git init` command initializes a new Git repository in the current directory.

```
$ mkdir my-project
$ cd my-project
$ git init
Initialized empty Git repository in /home/alice/my-project/.git/
```

You can also point `git init` at any directory:

```
$ git init /path/to/new-project
Initialized empty Git repository in /path/to/new-project/.git/
```

After `git init`, the directory is still empty (no commits, no files tracked). You have an empty repository ready to accept your first commit.

What `git init` does:

1. Creates a `.git` subdirectory with the skeleton of a Git repository
2. Sets up the default branch (usually `master` or `main`, depending on `init.defaultBranch`)
3. No commits exist yet; you are on an unborn branch

### 2. The .git Directory Structure

The `.git` directory is the heart of the repository. It contains all of Git's metadata and object database.

```
$ ls -la .git
total 20
drwxr-xr-x  7 alice alice  320 Jun 17 10:00 .
drwxr-xr-x  3 alice alice   60 Jun 17 10:00 ..
drwxr-xr-x  2 alice alice   60 Jun 17 10:00 branches
-rw-r--r--  1 alice alice   92 Jun 17 10:00 config
-rw-r--r--  1 alice alice   73 Jun 17 10:00 description
-rw-r--r--  1 alice alice   23 Jun 17 10:00 HEAD
drwxr-xr-x  4 alice alice   60 Jun 17 10:00 hooks
-rw-r--r--  1 alice alice  217 Jun 17 10:00 index
drwxr-xr-x  4 alice alice   60 Jun 17 10:00 info
drwxr-xr-x  4 alice alice   60 Jun 17 10:00 objects
drwxr-xr-x  4 alice alice   60 Jun 17 10:00 refs
```

Key components:

**HEAD**: A pointer to the current branch. It typically contains `ref: refs/heads/main`.

```
$ cat .git/HEAD
ref: refs/heads/main
```

**config**: Repository-specific Git configuration. This is the local config file.

```
$ cat .git/config
[core]
    repositoryformatversion = 0
    filemode = true
    bare = false
    logallrefupdates = true
```

**objects/**: The object database. All commits, trees, and blobs are stored here. Objects are stored in subdirectories named by the first two characters of their SHA-1 hash.

**refs/**: References (pointers) to commits. Contains:
- `refs/heads/` -- local branches
- `refs/tags/` -- tags
- `refs/remotes/` -- remote-tracking branches

**branches/**: Legacy directory, rarely used.

**description**: Used by GitWeb; typically contains "Unnamed repository; edit this file to name the repository for gitweb."

**hooks/**: Scripts that Git runs before/after certain events (e.g., pre-commit, post-receive).

**index**: The staging area (binary file). Not human-readable.

**info/**: Contains the global exclude file (`exclude`), which works like `.gitignore` but is not committed.

### 3. git clone - Copying an Existing Repository

`git clone` copies an existing remote repository to your local machine, complete with all history.

```
$ git clone https://github.com/user/repo.git
Cloning into 'repo'...
remote: Enumerating objects: 48, done.
remote: Counting objects: 100% (48/48), done.
remote: Total 48 (delta 4), reused 0 (delta 0), pack-reused 0
Receiving objects: 100% (48/48), done.
Resolving deltas: 100% (4/4), done.
```

This creates a directory named `repo` containing the working tree and the full `.git` directory.

You can specify a different target directory name:

```
$ git clone https://github.com/user/repo.git my-copy
```

Cloning via SSH (requires configured SSH keys):

```
$ git clone git@github.com:user/repo.git
```

What `git clone` does:

1. Creates a new directory
2. Runs `git init` inside it
3. Adds a remote called `origin` pointing to the source URL
4. Fetches all objects and references from the remote
5. Checks out the default branch (usually `main` or `master`)

### 4. Working Directory vs. .git

The **working directory** is your project files -- the files you edit with your editor. The `.git` directory is the repository database. These are two separate parts of a Git repository.

```
my-project/              <-- working directory (your files)
|-- src/
|-- README.md
|-- package.json
|-- .git/                <-- repository database (metadata, history)
    |-- objects/
    |-- refs/
    |-- HEAD
    |-- config
    |-- ...
```

Key separation:

- Deleting files from the working directory does not remove them from Git history. They still exist in past commits inside `.git/objects/`.
- Corrupting the working directory does not affect `.git` (unless you explicitly delete `.git`).
- The staging area (index) lives in `.git/index` and bridges the two.

### 5. Exercise: Init Your First Repository

```
$ mkdir first-repo
$ cd first-repo
$ git init

$ echo "# My First Repo" > README.md
$ git status

$ git add README.md
$ git commit -m "Initial commit: add README"
[main (root-commit) a1b2c3d] Initial commit: add README
 1 file changed, 1 insertion(+)
 create mode 100644 README.md

$ git log
commit a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0 (HEAD -> main)
Author: Alice Johnson <alice@example.com>
Date:   Tue Jun 17 10:00:00 2026 -0500

    Initial commit: add README

$ ls -la .git/objects/
```

### Quiz: 3 MCQs

**Q1.** What is stored in the `.git/HEAD` file after initializing a new repository?

a) The hash of the most recent commit
b) A reference to the current branch (e.g., `ref: refs/heads/main`)
c) The name of the repository
d) The contents of the staging area

**Q2.** Which of the following does `git clone` NOT do automatically?

a) Create a new directory for the project
b) Run `git init` in the new directory
c) Set up `origin` as a remote pointing to the source
d) Create an empty `.gitignore` file

**Q3.** If you delete all files in your working directory but leave `.git` intact, what can you do?

a) Nothing; the files are lost forever
b) Run `git checkout HEAD -- .` to restore all files from the last commit
c) Push to a remote (since changes are already committed)
d) The files are automatically restored from the index
