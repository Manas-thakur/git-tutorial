## Understanding Branches

Branches are one of Git's most powerful features. They let you diverge from the main line of development, experiment, and merge back cleanly. Unlike other VCS tools where branching means copying entire directories, Git branches are lightweight pointers.

### 1. What is a Branch?

In Git, a branch is simply a movable pointer to a specific commit.

```
$ git log --oneline
1a2b3c4 (HEAD -> main) Add authentication
9b8c7d6 Fix login redirect bug
f4e3d2c Initial commit
```

The branch `main` points to commit `1a2b3c4`. When you make a new commit, the pointer moves forward automatically.

```
$ echo "new feature" > feature.txt
$ git add feature.txt
$ git commit -m "Add feature"
[main 5d6e7f8] Add feature
 1 file changed, 1 insertion(+)

$ git log --oneline
5d6e7f8 (HEAD -> main) Add feature
1a2b3c4 Add authentication
9b8c7d6 Fix login redirect bug
f4e3d2c Initial commit
```

The branch pointer is stored as a file in `.git/refs/heads/`:

```
$ cat .git/refs/heads/main
5d6e7f8a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e
```

That is it -- a 41-byte file containing the commit hash. Creating a branch is nearly instantaneous because Git just writes a new reference file. There is no copying of files.

### 2. HEAD: The Current Branch Pointer

HEAD is a special pointer that tells Git which branch you are currently on. It is stored in `.git/HEAD`.

When you are on a branch, HEAD points to that branch reference:

```
$ cat .git/HEAD
ref: refs/heads/main
```

When you make a commit, Git reads HEAD to find which branch to advance. It then updates the branch reference to the new commit.

### 3. Detached HEAD State

HEAD can also point directly to a commit instead of a branch. This is called **detached HEAD**.

```
$ git checkout 1a2b3c4
Note: switching to '1a2b3c4'.

You are in 'detached HEAD' state. You can look around, make experimental
changes and commit them, and you can discard any commits you make in this
state without impacting any branches by switching back to a branch.

$ cat .git/HEAD
1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0
```

In detached HEAD, new commits are orphaned -- they do not belong to any branch:

```
$ echo "experiment" > experiment.txt
$ git add experiment.txt
$ git commit -m "Experiment in detached HEAD"
[detached HEAD 7a8b9c0] Experiment in detached HEAD

$ git log --oneline
7a8b9c0 (HEAD) Experiment in detached HEAD
1a2b3c4 Add authentication
9b8c7d6 Fix login redirect bug
f4e3d2c Initial commit
```

If you switch back to `main`, commit `7a8b9c0` is not reachable from any branch. It still exists in the object database but can be garbage collected. To keep it, create a branch:

```
$ git branch experiment 7a8b9c0
$ git checkout main
```

### 4. Default Branch Name

Historically, Git's default branch was `master`. Many projects now use `main`. You can set your preference:

```
$ git config --global init.defaultBranch main
```

This affects `git init` going forward. You can rename an existing branch:

```
$ git branch -m master main
```

### 5. Visualizing Branches

Branches form a directed acyclic graph. Visual tools help understand the structure.

**Text-based with git log:**

```
$ git log --oneline --graph --all --decorate
* 5d6e7f8 (HEAD -> main) Add feature
| * 7c8d9e0 (feature-login) Add login validation
|/
* 1a2b3c4 Add authentication
* 9b8c7d6 Fix login redirect bug
* f4e3d2c Initial commit
```

Each `*` is a commit. The lines show parent relationships. Branch labels appear in parentheses.

**Visual diagram of branching:**

```
  f4e3d2c --- 9b8c7d6 --- 1a2b3c4 --- 5d6e7f8 (main)
                                       /
                       7c8d9e0 --------
                       (feature-login)
```

Here, `feature-login` branched off after `1a2b3c4`, and `main` moved forward. The two branches diverged.

### 6. Why Branches Matter

- **Isolation**: Work on a new feature without affecting the stable codebase.
- **Experimentation**: Create throwaway branches to test ideas.
- **Collaboration**: Multiple developers work on different branches simultaneously.
- **Release management**: Maintain separate branches for development, staging, and production.
- **Bug fixes**: Create a hotfix branch from a specific release tag.

### Quiz: 3 MCQs

**Q1.** What is a branch in Git?

a) A complete copy of all project files
b) A lightweight movable pointer to a commit
c) A label that can only point to the current commit
d) A subdirectory in the working tree

**Q2.** What does detached HEAD mean?

a) The repository is corrupted
b) HEAD points directly to a commit instead of a branch
c) The current branch has no upstream configured
d) The working tree is out of sync with the staging area

**Q3.** When you create a new commit on a branch, what happens to the branch pointer?

a) It stays at the same commit; a new pointer is created
b) It advances to the new commit
c) It moves to the parent of the new commit
d) It is deleted and recreated at HEAD
