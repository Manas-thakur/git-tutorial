## Git Hooks

Git hooks are custom scripts that run automatically when certain Git events occur. They are stored in the `.git/hooks/` directory and can enforce policies, run checks, or automate workflows.

### 1. Client-Side Hooks (pre-commit, prepare-commit-msg, post-commit)

Client-side hooks run on the developer's local machine. They are not pushed with the repository and must be set up per-clone.

**Available client-side hooks:**

| Hook                  | Trigger                          | Common use                     |
|-----------------------|----------------------------------|--------------------------------|
| pre-commit            | Before commit message is created | Linting, formatting, checks    |
| prepare-commit-msg    | After default message is created | Auto-append ticket numbers     |
| commit-msg            | After commit message is edited   | Validate commit message format |
| post-commit           | After commit is created          | Notifications, logging         |
| pre-rebase            | Before rebase starts             | Prevent rebasing certain refs  |
| post-checkout         | After git checkout               | Auto-install dependencies      |
| post-merge            | After a successful merge         | Run migrations, update deps    |
| pre-push              | Before git push                  | Run tests before pushing       |

**Setting up a hook:**

1. Go to the `.git/hooks/` directory in your repository
2. Create a script with the hook name (no file extension)
3. Make it executable

```
$ cd .git/hooks/
$ ls
applypatch-msg.sample  prepare-commit-msg.sample
commit-msg.sample      pre-rebase.sample
post-update.sample     pre-commit.sample
pre-applypatch.sample  pre-push.sample
pre-commit.sample      pre-receive.sample

$ cp pre-commit.sample pre-commit
$ chmod +x pre-commit
```

### 2. Server-Side Hooks (pre-receive, post-receive)

Server-side hooks run on the remote repository (e.g., GitHub or your own Git server). They can enforce policies before commits are accepted.

**Common server-side hooks:**

| Hook          | Trigger                      | Common use                          |
|---------------|------------------------------|-------------------------------------|
| pre-receive   | Before accepting a push      | Enforce branch permissions          |
| update        | Before each ref is updated   | Per-branch policies, size limits    |
| post-receive  | After all refs are updated   | CI/CD triggers, deploy scripts      |
| post-update   | After a ref is updated       | Git daemon updates, notifications   |

**Example pre-receive hook (enforce no direct pushes to main):**

```
#!/bin/bash
# Pre-receive hook to prevent direct pushes to main
while read oldrev newrev refname
do
    if [[ $refname == "refs/heads/main" ]]; then
        echo "Direct pushes to main are not allowed."
        echo "Please use a pull request instead."
        exit 1
    fi
done
```

Server-side hooks are configured by the Git server administrator. On GitHub, you use branch protection rules instead of custom hooks. On self-hosted Git servers, you place hooks in the `hooks/` directory of the bare repository.

### 3. pre-commit Hooks for Linting

A pre-commit hook runs before each commit and can reject the commit if checks fail.

**Example pre-commit hook for Python (flake8):**

```
#!/bin/bash
echo "Running flake8 linting..."
flake8 --statistics .
if [ $? -ne 0 ]; then
    echo "Linting failed. Fix the errors and commit again."
    exit 1
fi
```

**Example pre-commit hook for JavaScript (ESLint):**

```
#!/bin/bash
echo "Running ESLint..."
npx eslint src/
if [ $? -ne 0 ]; then
    echo "ESLint found errors. Please fix them before committing."
    exit 1
fi
```

**Staged-only linting (check only what is being committed):**

```
#!/bin/bash
for file in $(git diff --cached --name-only --diff-filter=ACM | grep '\.py$'); do
    flake8 "$file"
    if [ $? -ne 0 ]; then
        echo "Linting failed in $file"
        exit 1
    fi
done
```

**Using pre-commit framework (pre-commit.com):**

Instead of writing hooks manually, many projects use the `pre-commit` framework with a `.pre-commit-config.yaml` file:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black
```

Then install the hooks:

```
$ pip install pre-commit
$ pre-commit install
```

### 4. commit-msg for Conventional Commits

The `commit-msg` hook runs after the commit message is written but before the commit is created. It can enforce commit message conventions.

**Example commit-msg hook enforcing conventional commits:**

```
#!/bin/bash
# Enforces conventional commit format:
# type(scope): subject
# types: feat, fix, docs, style, refactor, perf, test, chore

commit_message=$(cat "$1")

if ! echo "$commit_message" | grep -qE '^(feat|fix|docs|style|refactor|perf|test|chore)(\(.+\))?: '; then
    echo "ERROR: Commit message must follow conventional commit format."
    echo "Example: feat(login): add password validation"
    exit 1
fi

if [ ${#commit_message} -gt 72 ]; then
    echo "ERROR: Commit message must be 72 characters or less."
    exit 1
fi
```

**Example commit-msg hook for Jira ticket links:**

```
#!/bin/bash
# Ensures every commit references a Jira ticket
commit_message=$(cat "$1")
if ! echo "$commit_message" | grep -qE '\[PROJ-[0-9]+\]'; then
    echo "Warning: Commit message does not include a Jira ticket reference."
    echo "Format: [PROJ-123] description"
    # Uncomment to make this blocking:
    # exit 1
fi
```

### 5. Sample Hook Scripts

**pre-push hook (run tests before pushing):**

```
#!/bin/bash
# Run tests before allowing push
echo "Running tests before push..."
npm test
if [ $? -ne 0 ]; then
    echo "Tests failed. Push aborted."
    exit 1
fi
```

**post-checkout hook (auto-install dependencies):**

```
#!/bin/bash
# Check if package.json changed and auto-install
if git diff HEAD@{1} HEAD --name-only | grep -q "package.json"; then
    echo "package.json changed. Running npm install..."
    npm install
fi
```

**post-commit hook (update task status):**

```
#!/bin/bash
# Send a notification when a commit is made
commit_message=$(git log -1 --pretty=%B)
echo "Commit made: $commit_message"
# curl -X POST https://api.example.com/notify -d "message=$commit_message"
```

**create-branch hook via prepare-commit-msg (auto-add branch name):**

```
#!/bin/bash
# Auto-prepend the branch name to commits
BRANCH=$(git symbolic-ref --short HEAD)
if echo "$BRANCH" | grep -qE '^(feature|bugfix|hotfix)/'; then
    TICKET=$(echo "$BRANCH" | sed 's/.*\/\([A-Z]*-[0-9]*\).*/\1/')
    sed -i "1s/^/[$TICKET] /" "$1"
fi
```

**Shared hooks across the team:**

Since `.git/hooks/` is not pushed to the remote, teams often store hooks in the repository and symlink them:

```
$ mkdir -p .githooks
$ cat > .githooks/pre-commit << 'EOF'
#!/bin/bash
# Shared pre-commit hook
echo "Running shared hook..."
EOF
$ chmod +x .githooks/pre-commit
$ git config core.hooksPath .githooks
```

The `core.hooksPath` configuration tells Git to look for hooks in a version-controlled directory instead of `.git/hooks/`. This allows the entire team to share hooks.

### Quiz: Git Hooks

**Question 1:** Which Git hook is best suited for running linters and formatters before a commit is created?

a) post-commit
b) pre-commit
c) prepare-commit-msg
d) pre-push

**Question 2:** If you want to enforce that every commit message contains a Jira ticket reference, which hook should you use?

a) pre-commit
b) post-commit
c) commit-msg
d) prepare-commit-msg

**Question 3:** How can you share Git hooks with other team members through a version-controlled repository?

a) Place hooks in `.git/hooks/` and commit them
b) Set `core.hooksPath` to a version-controlled directory like `.githooks/`
c) Email the hook scripts to each team member
d) Git automatically shares hooks via the remote repository

---

**Answers:** 1-b, 2-c, 3-b
