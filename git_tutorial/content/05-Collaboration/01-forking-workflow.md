## Forking Workflow

The forking workflow is a distributed workflow commonly used in open-source projects and organizations where contributors do not have write access to the main repository. Instead of working on shared branches, each contributor forks the repository and works independently.

### 1. Forking vs Branching

In the **branching workflow**, all developers work within a single shared repository. They create branches, push them, and open pull requests. Everyone has (at minimum) write access to create branches.

```
Shared repository branching:
main:         A---B---C---D
feature/alice:      \---E---F
feature/bob:         \---G---H
```

In the **forking workflow**, each developer creates their own copy (fork) of the repository on the hosting service (GitHub, GitLab, Bitbucket). They work in their fork and submit changes via pull requests to the upstream repository.

```
Forking workflow:
Upstream repo (org/project):
main: A---B---C---D

Alice's fork (alice/project):
main: A---B---C---D---E---F

Bob's fork (bob/project):
main: A---B---C---D---G---H
```

Key differences:

| Aspect         | Branching               | Forking                       |
|----------------|-------------------------|-------------------------------|
| Repository     | Single shared repo      | Multiple copies (forks)       |
| Access control | Write access needed     | No write access needed        |
| CI/CD setup    | One CI configuration    | Each fork has its own CI      |
| Visibility     | All branches visible    | Work in private until PR      |
| Management     | Simple for small teams  | Necessary for large projects  |

### 2. Fork on GitHub / GitLab

Forking on GitHub or GitLab is a one-click operation from the repository page.

**On GitHub:**
1. Navigate to the repository (e.g., `https://github.com/org/project`)
2. Click the "Fork" button in the top-right corner
3. Select your personal account or organization
4. GitHub creates a copy under your account (e.g., `https://github.com/yourname/project`)

**Clone your fork locally:**

```
$ git clone https://github.com/yourname/project.git
$ cd project
```

**On GitLab:**
1. Navigate to the project
2. Click "Fork" button
3. Select the namespace for the fork
4. GitLab creates the fork

### 3. Keeping Fork in Sync

Once you have a fork, it will fall behind the upstream repository as others contribute. You need to sync your fork periodically to stay up to date.

**Add the upstream as a remote:**

```
$ git remote add upstream https://github.com/org/project.git
$ git remote -v
origin    https://github.com/yourname/project.git (fetch)
origin    https://github.com/yourname/project.git (push)
upstream  https://github.com/org/project.git (fetch)
upstream  https://github.com/org/project.git (push)
```

**Fetch upstream changes:**

```
$ git fetch upstream
remote: Enumerating objects: 10, done.
remote: Counting objects: 100% (10/10), done.
remote: Compressing objects: 100% (5/5), done.
remote: Total 10 (delta 8), reused 7 (delta 5), pack-reused 0
Unpacking objects: 100% (10/10), done.
From https://github.com/org/project
 * [new branch]      main       -> upstream/main
```

**Merge upstream into your local main:**

```
$ git checkout main
$ git merge upstream/main
Updating a1b2c3d..e4f5g6h
Fast-forward
 src/file.go | 10 +++++-----
 1 file changed, 5 insertions(+), 5 deletions(-)
```

**Or rebase your feature branch:**

```
$ git checkout feature
$ git rebase upstream/main
```

**Push updates to your fork:**

```
$ git push origin main
```

Some developers prefer using `git pull upstream main` instead of fetch + merge:

```
$ git checkout main
$ git pull upstream main
```

### 4. Upstream Remote

The `upstream` remote is a convention, not a Git requirement. You can name it anything, but `upstream` is standard for referring to the original repository you forked from.

**Typical remote setup for forking:**

```
$ git remote add upstream https://github.com/original-owner/project.git
$ git remote set-url --push upstream no_push
```

The `--push` option with `no_push` prevents accidental pushes to upstream. If you try to push, Git will show a helpful error:

```
$ git push upstream main
fatal: 'no_push' does not appear to be a git repository
```

**Multiple remotes for different purposes:**

```
$ git remote add upstream https://github.com/org/project.git
$ git remote add alice https://github.com/alice/project.git
$ git remote add bob https://github.com/bob/project.git
```

**Checking your remotes:**

```
$ git remote -v
```

**Syncing a fork via command line (full workflow):**

```
$ git checkout main
$ git fetch upstream
$ git rebase upstream/main
$ git push origin main
```

**Syncing with GitHub CLI:**

```
$ gh repo sync yourname/project
```

### 5. Complete Forking Workflow Example

```
# Step 1: Fork on GitHub (click "Fork" button)

# Step 2: Clone your fork
$ git clone https://github.com/yourname/project.git
$ cd project

# Step 3: Add upstream remote
$ git remote add upstream https://github.com/org/project.git

# Step 4: Create a feature branch
$ git checkout -b fix-login-bug

# Step 5: Make changes and commit
$ git add .
$ git commit -m "Fix login validation bug"

# Step 6: Push to your fork
$ git push origin fix-login-bug

# Step 7: Open a Pull Request from your fork to upstream

# Step 8: When PR is merged, sync your fork
$ git checkout main
$ git fetch upstream
$ git rebase upstream/main
$ git push origin main

# Step 9: Delete the feature branch from your fork
$ git push origin --delete fix-login-bug
$ git branch -d fix-login-bug
```

### Quiz: Forking Workflow

**Question 1:** In a forking workflow, what is the purpose of adding an "upstream" remote?

a) To automatically mirror all changes to the original repository
b) To track the original repository so you can sync changes from it
c) To create a backup of your fork on the upstream server
d) To grant write access to the upstream repository maintainers

**Question 2:** After your pull request is merged into the upstream repository, what is the correct way to update your fork's main branch?

a) `git pull origin main`
b) `git fetch upstream && git merge upstream/main && git push origin main`
c) The fork is automatically updated when the PR is merged
d) Delete and recreate the fork

**Question 3:** Why might you set the push URL of the upstream remote to "no_push"?

a) To disable all network communication with the upstream
b) To prevent accidentally pushing commits to the original repository
c) To speed up fetch operations by disabling push
d) To enable two-factor authentication for push operations

---

**Answers:** 1-b, 2-b, 3-b
