## Cloning

`git clone` creates a local copy of an existing remote repository. It is the primary way to get a copy of someone else's project or to set up a local working copy of your own remote project.

### 1. Basic git clone

```
$ git clone https://github.com/user/repo.git
Cloning into 'repo'...
remote: Enumerating objects: 152, done.
remote: Counting objects: 100% (152/152), done.
remote: Total 152 (delta 52), reused 0 (delta 0), pack-reused 0
Receiving objects: 100% (152/152), 34.56 KiB | 1.38 MiB/s, done.
Resolving deltas: 100% (52/52), done.
```

This creates a directory named `repo` (derived from the repository name) containing the full project history and a working tree checked out at the default branch.

**Clone into a specific directory:**

```
$ git clone https://github.com/user/repo.git my-custom-name
Cloning into 'my-custom-name'...
```

### 2. HTTPS vs. SSH

**HTTPS:**

```
$ git clone https://github.com/user/repo.git
```

- No setup required for read-only access
- For write access, you need a personal access token (password authentication is deprecated by GitHub)
- Works through corporate firewalls

**SSH:**

```
$ git clone git@github.com:user/repo.git
```

- Requires generating and adding an SSH key to your account
- No credentials prompt for each push
- More secure (uses public-key cryptography)
- May be blocked by some corporate firewalls

**Setting up SSH keys:**

```
$ ssh-keygen -t ed25519 -C "your_email@example.com"
$ cat ~/.ssh/id_ed25519.pub
# Add this output to your GitHub/GitLab/Bitbucket SSH keys settings
```

### 3. Shallow Clone (--depth)

A shallow clone fetches only a limited number of commits instead of the entire history. This is useful for large repositories where you only need the latest version.

```
$ git clone --depth 1 https://github.com/user/repo.git
Cloning into 'repo'...
remote: Enumerating objects: 48, done.
remote: Counting objects: 100% (48/48), done.
remote: Total 48 (delta 4), reused 0 (delta 0), pack-reused 0
Receiving objects: 100% (48/48), done.
Resolving deltas: 100% (4/4), done.
```

This fetches only the most recent commit. The clone is much smaller and faster.

**Shallow clone with a specific depth:**

```
$ git clone --depth 5 https://github.com/user/repo.git   # last 5 commits
```

**Later deepening a shallow clone:**

```
$ git fetch --depth 50       # increase depth to 50
$ git fetch --unshallow      # convert to full clone
```

**Limitations of shallow clones:**

- Cannot `git log` beyond the shallow boundary
- Cannot `git checkout` older commits that were not fetched
- Cannot `git push` from a shallow clone to a remote (by default)
- Some Git operations may fail or behave differently

### 4. Cloning a Specific Branch

Clone only a single branch (not all branches):

```
$ git clone --branch feature-x --single-branch https://github.com/user/repo.git
```

This is faster for large repos when you only need one branch.

Clone a specific tag:

```
$ git clone --branch v1.0.0 https://github.com/user/repo.git
```

### 5. Bare Repositories (--bare)

A bare repository has no working tree. It contains only the `.git` contents (objects, refs, HEAD, config). Bare repos are used as server-side repositories for push targets.

```
$ git clone --bare https://github.com/user/repo.git
Cloning into bare repository 'repo.git'...
```

Characteristics of a bare repo:

- No working directory (no files checked out)
- The directory name typically ends in `.git`
- Used as the central hub for team collaboration
- Cannot run `git status` or `git log -p` (no working tree to compare)

**Creating a bare repo from scratch:**

```
$ git init --bare /path/to/project.git
```

**When to use bare repos:**

- Setting up a central Git server
- Creating a remote backup of a repository
- Hosting a repository for other developers to push to

### 6. What git clone Actually Does

1. Creates a new directory (unless you specify an existing empty directory)
2. Runs `git init` to initialize an empty repository
3. Adds a remote named `origin` pointing to the source URL
4. Fetches all objects and references from the remote
5. Checks out the default branch (or the branch specified with `--branch`)

After cloning:

```
$ git remote -v
origin  https://github.com/user/repo.git (fetch)
origin  https://github.com/user/repo.git (push)

$ git branch -a
* main
  remotes/origin/main
  remotes/origin/feature-x

$ git log --oneline
1a2b3c4 (HEAD -> main, origin/main, origin/HEAD) Update README
9b8c7d6 Add new feature
```

### 7. Other Useful Clone Options

| Option | Effect |
|--------|--------|
| `--recurse-submodules` | Also clone submodules |
| `--shallow-submodules` | Clone submodules shallowly |
| `--no-checkout` | Clone but do not check out any file |
| `--filter=blob:none` | Partial clone: omit blobs until needed (Git 2.19+) |
| `--template` | Use a custom template directory |
| `--origin <name>` | Use a different remote name instead of `origin` |

**Partial clone example (saves bandwidth):**

```
$ git clone --filter=blob:none https://github.com/user/repo.git
```

Git downloads only commit and tree objects initially. Blobs (file contents) are fetched on demand when you check out a file or run `git diff`.

### Quiz: 3 MCQs

**Q1.** What is the primary difference between `git clone` with HTTPS vs SSH?

a) HTTPS is faster than SSH
b) HTTPS can only be used for read-only; SSH is required for write
c) SSH uses public-key authentication, while HTTPS can use tokens or passwords
d) They are identical in functionality

**Q2.** When would you use `git clone --depth 1`?

a) When you need all branches but only the latest commit
b) When you want a minimal clone with only the most recent commit, useful for CI or large repos
c) When you want to clone only the .git directory without a working tree
d) When you want to clone and immediately start contributing

**Q3.** What is a bare repository used for?

a) Daily development work with a visible working tree
b) A server-side repository that accepts pushes but has no working tree
c) A compressed backup that cannot be pushed to
d) A repository with no commit history
