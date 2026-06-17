## Pushing and Pulling

Pushing and pulling are the mechanisms for synchronizing work between your local repository and a remote. This chapter covers the core commands `git push`, `git pull`, and `git fetch`, along with tracking branches and upstream configuration.

### 1. git push - Sending Changes to a Remote

`git push` uploads your local commits to a remote repository.

```
$ git push origin main
Enumerating objects: 5, done.
Counting objects: 100% (5/5), done.
Delta compression using up to 8 threads
Compressing objects: 100% (3/3), done.
Writing objects: 100% (3/3), 450 bytes | 450.00 KiB/s, done.
Total 3 (delta 1), reused 0 (delta 0), remotes/delta 1
To https://github.com/user/repo.git
   1a2b3c4..5d6e7f8  main -> main
```

This pushes the `main` branch to the remote named `origin`, updating the remote's `main` branch to match the local one.

**What happens during a push:**

1. Git checks if your local branch has the commits that the remote expects
2. If the remote has commits you do not have locally, Git rejects the push (non-fast-forward)
3. Git uploads the new objects
4. Git updates the remote reference

**Set upstream (-u):**

The first push to a new branch should set the upstream (tracking) relationship:

```
$ git push -u origin feature-login
* [new branch]      feature-login -> feature-login
Branch 'feature-login' set up to track remote branch 'feature-login' from 'origin'.
```

After setting upstream, you can simply use `git push` without arguments.

### 2. Tracking Branches

A tracking branch establishes a relationship between a local branch and a remote branch. It enables simple `git push` and `git pull` without specifying the remote and branch.

View tracking relationships:

```
$ git branch -vv
* main           1a2b3c4 [origin/main] Update README
  feature-login 5d6e7f8 [origin/feature-login] Add login form
  experiment    9b8c7d6 [origin/main: behind 2] Start experiment
```

The `[origin/main]` shows the tracking branch. You can see ahead/behind counts:

```
$ git status
On branch main
Your branch is ahead of 'origin/main' by 3 commits.
  (use "git push" to publish your local commits)
```

Set tracking for an existing branch:

```
$ git branch -u origin/main
Branch 'main' set up to track remote branch 'main' from 'origin'.

$ git branch -u origin/feature-login feature-login
```

### 3. git pull - Fetching and Merging

`git pull` is a combination of `git fetch` (download remote data) followed by `git merge` (integrate it into your current branch).

```
$ git pull
remote: Enumerating objects: 5, done.
remote: Counting objects: 100% (5/5), done.
remote: Total 3 (delta 1), reused 0 (delta 0), pack-reused 0
Unpacking objects: 100% (3/3), 345 bytes | 345.00 KiB/s, done.
From https://github.com/user/repo.git
   1a2b3c4..9b8c7d6  main       -> origin/main
Updating 1a2b3c4..9b8c7d6
Fast-forward
 README.md | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

This is equivalent to:

```
$ git fetch origin
$ git merge origin/main
```

**Pull with specific remote and branch:**

```
$ git pull origin main
```

### 4. git fetch - Downloading Without Merging

`git fetch` downloads commits, objects, and references from the remote but does NOT update your working tree or merge anything. It only updates remote-tracking branches.

```
$ git fetch
remote: Enumerating objects: 5, done.
remote: Counting objects: 100% (5/5), done.
remote: Total 3 (delta 1), reused 0 (delta 0), pack-reused 0
Unpacking objects: 100% (3/3), 345 bytes | 345.00 KiB/s, done.
From https://github.com/user/repo.git
   1a2b3c4..9b8c7d6  main       -> origin/main
```

After fetching, you can review the changes before merging:

```
$ git log --oneline origin/main
9b8c7d6 Update README
1a2b3c4 Initial commit

$ git diff main origin/main
```

Then merge when ready:

```
$ git merge origin/main
```

### 5. Push Rejection and Force Push

Git rejects a push if the remote has commits that you do not have locally (non-fast-forward rejection):

```
$ git push origin main
To https://github.com/user/repo.git
 ! [rejected]        main -> main (non-fast-forward)
error: failed to push some refs to 'https://github.com/user/repo.git'
hint: Updates were rejected because the remote contains work that you do not
hint: have locally.
```

**How to fix:**

1. Pull the remote changes first: `git pull origin main`
2. Resolve any conflicts
3. Push again

**git push --force** (and why to avoid it):

`git push --force` overwrites the remote branch with your local version, discarding any commits on the remote that you do not have.

```
$ git push --force origin main
```

Dangers of force push:

- Destroys commits on the remote that collaborators may have based work on
- Causes confusion and extra work for your team
- Should NEVER be used on shared branches (main, develop)

**Safer alternative: --force-with-lease**

```
$ git push --force-with-lease origin main
```

This checks if the remote branch has changed since you last fetched. If it has, the push is rejected. This prevents accidentally overwriting someone else's work.

### 6. git push --delete - Removing Remote Branches

```
$ git push origin --delete feature-login
To https://github.com/user/repo.git
 - [deleted]         feature-login
```

This deletes the branch on the remote. You should also delete the local branch:

```
$ git branch -d feature-login
```

### 7. Push to All Remotes

```
$ git push --all
$ git push --all origin
```

This pushes all local branches to the remote. Branches are created on the remote if they do not exist.

### Quiz: 3 MCQs

**Q1.** Your push is rejected with "non-fast-forward". What does this mean?

a) The remote repository does not exist
b) You do not have write access to the remote
c) The remote has commits that you do not have locally; you need to pull first
d) Your local branch name does not match the remote branch name

**Q2.** What is the difference between `git fetch` and `git pull`?

a) They are identical
b) `git fetch` downloads data and updates working tree; `git pull` only downloads data
c) `git fetch` only downloads data without merging; `git pull` downloads and merges into the current branch
d) `git fetch` works only with SSH remotes

**Q3.** You want to push a newly created local branch to the remote and set up tracking. Which command do you use?

a) `git push origin feature-x`
b) `git push -u origin feature-x`
c) `git push --all`
d) `git push origin HEAD`
