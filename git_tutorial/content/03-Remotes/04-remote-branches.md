## Remote Branches

Remote-tracking branches are your local's view of the remote repository's branches. They let you see what the remote looks like without network access and provide a reference for where your branches should go.

### 1. What Are Remote-Tracking Branches?

Remote-tracking branches are references (pointers) that track the state of branches in remote repositories. They are local read-only copies of what the remote looked like the last time you fetched.

```
$ git branch -r
  origin/HEAD -> origin/main
  origin/feature-login
  origin/main
```

They live in `.git/refs/remotes/<remote-name>/`:

```
$ ls .git/refs/remotes/origin/
HEAD
feature-login
main
```

Remote-tracking branches:

- Are updated only by network operations (`git fetch`, `git pull`, `git push`)
- Cannot be checked out directly (you get detached HEAD if you try)
- Serve as bookmarks for what the remote looks like
- Are used as merge sources in pull operations

### 2. Viewing Remote Branches

**Only remote branches:**

```
$ git branch -r
  origin/HEAD -> origin/main
  origin/main
  origin/feature-login
```

**All branches (local + remote):**

```
$ git branch -a
* main
  feature-login
  remotes/origin/HEAD -> origin/main
  remotes/origin/feature-login
  remotes/origin/main
```

**Verbose view with tracking info:**

```
$ git branch -vv
* main           1a2b3c4 [origin/main] Update README
  feature-login 5d6e7f8 [origin/feature-login: ahead 2, behind 1] Add login form
```

### 3. How Remote Branches Get Updated

**After git fetch:**

```
$ git fetch origin
From https://github.com/user/repo.git
   1a2b3c4..9b8c7d6  main       -> origin/main
   * [new branch]      experiment -> origin/experiment
```

Remote-tracking branches are updated, but local branches and working tree are untouched.

**After git push:**

```
$ git push origin main
To https://github.com/user/repo.git
   1a2b3c4..9b8c7d6  main -> main
```

Git also updates `origin/main` locally to reflect that the push succeeded.

**After git pull:**

A pull fetches (updating remote-tracking branches) then merges.

### 4. git remote update - Fetching All Remotes

```
$ git remote update
Fetching origin
Fetching upstream
```

This is equivalent to running `git fetch` for every remote. It updates all remote-tracking branches from all remotes.

### 5. Checking Out a Remote Branch

You cannot directly check out a remote-tracking branch. Trying gives you detached HEAD:

```
$ git checkout origin/feature-login
Note: switching to 'origin/feature-login'.

You are in 'detached HEAD' state.
```

To work on a remote branch, create a local branch that tracks it:

```
$ git checkout -b feature-login origin/feature-login
Branch 'feature-login' set up to track remote branch 'feature-login' from 'origin'.
Switched to a new branch 'feature-login'
```

Or use the shorthand (creates a local branch with the same name):

```
$ git checkout feature-login
Branch 'feature-login' set up to track remote branch 'feature-login' from 'origin'.
Switched to a new branch 'feature-login'
```

### 6. Pruning Stale Branches

When a remote branch is deleted (by you or a collaborator), your local remote-tracking branches still reference it. This is stale or orphaned.

**Check what is stale:**

```
$ git remote show origin
Remote branches:
  main          tracked
  feature-old   stale (use 'git remote prune' to remove)
```

**Prune a single remote:**

```
$ git remote prune origin
Pruning origin
URL: https://github.com/user/repo.git
 * [pruned] origin/feature-old
```

**Fetch and prune in one command:**

```
$ git fetch --prune origin
From https://github.com/user/repo.git
 x [deleted]         (none)     -> origin/feature-old
```

**Prune all remotes:**

```
$ git fetch --all --prune
```

The `--prune` option removes any remote-tracking branches that no longer exist on the remote.

### 7. Deleting a Remote Branch

Delete from the remote:

```
$ git push origin --delete feature-old
To https://github.com/user/repo.git
 - [deleted]         feature-old
```

After deleting the remote branch, prune your local references:

```
$ git remote prune origin
$ git branch -r       # verify it is gone
```

### 8. HEAD in Remote Branches

When you clone a repository, a special ref `origin/HEAD` is created. It indicates the default branch on the remote.

```
$ git branch -r
  origin/HEAD -> origin/main
```

You can set or change it:

```
$ git remote set-head origin main
$ git remote set-head origin --auto
```

### 9. Upstream Relationship (Tracking)

The upstream relationship connects a local branch to a remote-tracking branch. It is what makes `git push` and `git pull` work without arguments.

Check upstream:

```
$ git rev-parse --abbrev-ref --symbolic-full-name @{upstream}
refs/remotes/origin/main
```

Set upstream:

```
$ git branch -u origin/main
$ git branch --set-upstream-to=origin/main
```

Remove upstream:

```
$ git branch --unset-upstream
```

### Quiz: 3 MCQs

**Q1.** A collaborator deleted a branch named `old-feature` on the remote. After running `git fetch`, your local still shows `origin/old-feature`. Why?

a) Remote branches are never removed locally
b) `git fetch` does not delete remote-tracking branches unless `--prune` is used
c) You need to delete your local branch first
d) The remote branch is cached indefinitely

**Q2.** What does `git fetch --prune origin` do?

a) Fetches updates and deletes all local branches
b) Fetches updates and removes remote-tracking branches that no longer exist on the remote
c) Removes all local branches that have been merged
d) Optimizes the local repository storage

**Q3.** You see `origin/feature-x` in `git branch -r` and want to create a local branch to work on it. What is the correct command?

a) `git checkout origin/feature-x`
b) `git branch origin/feature-x`
c) `git switch -c feature-x origin/feature-x` or `git checkout -b feature-x origin/feature-x`
d) `git branch feature-x && git pull origin feature-x`
